"""
ingest.py — Daily ingestion script for Starlink satellite data.

Sources:
  - CelesTrak: TLE/orbital data (no auth)
  - Space-Track: launch dates, decay info (free account)
    Register: https://www.space-track.org/auth/createAccount

Run: python ingest.py
"""

import requests
import os
import math
import time
from datetime import datetime, timezone
from database import executemany, execute
from dotenv import load_dotenv

load_dotenv()


# ─── Fetch from CelesTrak ────────────────────────────────────────────────────

def fetch_celestrak():
    print("📡 Fetching Starlink TLE data from CelesTrak...")
    import subprocess
    import tempfile
    import os
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    subprocess.run([
        "curl", "-s", "--max-time", "120",
        "-o", temp_path,
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=json"
    ], check=True)
    
    with open(temp_path, 'r') as f:
        data = json.load(f)
    
    os.unlink(temp_path)
    print(f"   → {len(data)} satellites received")
    return data


# ─── Parse orbital elements from TLE line 2 ──────────────────────────────────

def parse_tle(tle2: str) -> dict:
    try:
        parts = tle2.split()
        mean_motion  = float(parts[7])
        inclination  = float(parts[2])
        eccentricity = float("0." + parts[4])

        mu = 398600.4418          # km³/s²
        n  = mean_motion * 2 * math.pi / 86400
        a  = (mu / n**2) ** (1/3)

        R  = 6371.0
        apogee  = a * (1 + eccentricity) - R
        perigee = a * (1 - eccentricity) - R

        return {
            "altitude_km":  round((apogee + perigee) / 2, 1),
            "apogee_km":    round(apogee, 1),
            "perigee_km":   round(perigee, 1),
            "inclination":  round(inclination, 4),
            "mean_motion":  round(mean_motion, 8),
            "eccentricity": round(eccentricity, 7),
            "period_min":   round(1440 / mean_motion, 2),
        }
    except Exception as e:
        print(f"   ⚠ TLE parse error: {e}")
        return {}


# ─── Fetch SATCAT from Space-Track ───────────────────────────────────────────

def fetch_spacetrack(norad_ids: list) -> dict:
    user = os.environ.get("SPACETRACK_USER")
    pw   = os.environ.get("SPACETRACK_PASS")

    if not user or not pw:
        print("   ⚠ No Space-Track credentials — skipping launch/decay enrichment.")
        print("     Set SPACETRACK_USER and SPACETRACK_PASS in .env to get full data.")
        return {}

    session = requests.Session()
    session.post(
        "https://www.space-track.org/ajaxauth/login",
        data={"identity": user, "password": pw},
        timeout=20,
    ).raise_for_status()

    satcat = {}
    chunk_size = 500
    for i in range(0, len(norad_ids), chunk_size):
        chunk = norad_ids[i : i + chunk_size]
        ids   = ",".join(str(n) for n in chunk)
        resp  = session.get(
            f"https://www.space-track.org/basicspacedata/query/class/satcat"
            f"/NORAD_CAT_ID/{ids}/format/json/emptyresult/show",
            timeout=30,
        )
        resp.raise_for_status()
        for entry in resp.json():
            satcat[int(entry["NORAD_CAT_ID"])] = {
                "launch_date":      entry.get("LAUNCH"),
                "decay_date":       entry.get("DECAY"),
                "intl_designator":  entry.get("INTLDES"),
            }
        time.sleep(1)

    print(f"   → SATCAT data for {len(satcat)} satellites")
    return satcat


# ─── Infer orbital shell from altitude ───────────────────────────────────────

def infer_shell(alt):
    if alt is None: return 0
    if alt < 340:   return 1
    if alt < 370:   return 2
    if alt < 410:   return 3
    if alt < 480:   return 4
    if alt < 560:   return 5
    if alt < 600:   return 6
    return 7


# ─── Upsert to local Postgres ────────────────────────────────────────────────

def upsert_satellites(satellites, satcat):
    now = datetime.now(timezone.utc)
    records = []

    for sat in satellites:
        norad_id = int(sat.get("NORAD_CAT_ID", 0))
        
        mean_motion = sat.get("MEAN_MOTION")
        inclination = sat.get("INCLINATION")
        eccentricity = sat.get("ECCENTRICITY")
        
        mu = 398600.4418
        if mean_motion:
            n = mean_motion * 2 * math.pi / 86400
            a = (mu / n**2) ** (1/3)
            R = 6371.0
            ecc = eccentricity or 0
            apogee = a * (1 + ecc) - R
            perigee = a * (1 - ecc) - R
            altitude_km = (apogee + perigee) / 2
            period_min = 1440 / mean_motion
        else:
            altitude_km = apogee = perigee = period_min = None
        
        cat = satcat.get(norad_id, {})
        decay_date = cat.get("decay_date") or None
        
        if decay_date:
            status = "decayed"
        elif perigee and perigee < 200:
            status = "decaying"
        else:
            status = "active"

        records.append((
            norad_id,
            sat.get("OBJECT_NAME", "").strip(),
            cat.get("intl_designator") or sat.get("OBJECT_ID", ""),
            cat.get("launch_date") or None,
            decay_date,
            status,
            infer_shell(altitude_km),
            round(altitude_km, 1) if altitude_km else None,
            round(apogee, 1) if apogee else None,
            round(perigee, 1) if perigee else None,
            round(inclination, 4) if inclination else None,
            round(mean_motion, 8) if mean_motion else None,
            round(eccentricity, 7) if eccentricity else None,
            round(period_min, 2) if period_min else None,
            None,
            None,
            now,
        ))

    print(f"💾 Upserting {len(records)} satellites to local Postgres...")

    # ON CONFLICT DO UPDATE = "upsert" in SQL
    # If norad_id already exists → update it. Otherwise → insert.
    sql = """
        INSERT INTO satellites (
            norad_id, name, intl_designator, launch_date, decay_date,
            status, shell, altitude_km, apogee_km, perigee_km,
            inclination, mean_motion, eccentricity, period_min,
            tle_line1, tle_line2, tle_updated_at
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s
        )
        ON CONFLICT (norad_id) DO UPDATE SET
            name            = EXCLUDED.name,
            intl_designator = EXCLUDED.intl_designator,
            launch_date     = COALESCE(satellites.launch_date, EXCLUDED.launch_date),
            decay_date      = EXCLUDED.decay_date,
            status          = EXCLUDED.status,
            shell           = EXCLUDED.shell,
            altitude_km     = EXCLUDED.altitude_km,
            apogee_km       = EXCLUDED.apogee_km,
            perigee_km      = EXCLUDED.perigee_km,
            inclination     = EXCLUDED.inclination,
            mean_motion     = EXCLUDED.mean_motion,
            eccentricity    = EXCLUDED.eccentricity,
            period_min      = EXCLUDED.period_min,
            tle_line1       = EXCLUDED.tle_line1,
            tle_line2       = EXCLUDED.tle_line2,
            tle_updated_at  = EXCLUDED.tle_updated_at,
            updated_at      = NOW()
    """
    executemany(sql, records)
    print(f"   ✓ Done")


def save_history(satellites):
    now     = datetime.now(timezone.utc)
    records = []
    mu = 398600.4418
    R = 6371.0
    
    for sat in satellites:
        mean_motion = sat.get("MEAN_MOTION")
        eccentricity = sat.get("ECCENTRICITY", 0)
        
        if not mean_motion:
            continue
            
        n = mean_motion * 2 * math.pi / 86400
        a = (mu / n**2) ** (1/3)
        ecc = eccentricity or 0
        apogee = a * (1 + ecc) - R
        perigee = a * (1 - ecc) - R
        altitude_km = (apogee + perigee) / 2
        
        records.append((
            int(sat["NORAD_CAT_ID"]),
            round(altitude_km, 1),
            round(perigee, 1),
            round(apogee, 1),
            now,
        ))

    if records:
        executemany(
            """
            INSERT INTO satellite_history (norad_id, altitude_km, perigee_km, apogee_km, recorded_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            records,
        )
        print(f"   → Saved {len(records)} history snapshots")


# ─── Main ─────────────────────────────────────────────────────────────────────

def run():
    print(f"\n🛰  Starlink Ingestion — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    satellites = fetch_celestrak()
    norad_ids  = [int(s["NORAD_CAT_ID"]) for s in satellites if s.get("NORAD_CAT_ID")]
    satcat     = fetch_spacetrack(norad_ids)

    upsert_satellites(satellites, satcat)
    save_history(satellites)

    print("\n✅ Ingestion complete!\n")


if __name__ == "__main__":
    run()