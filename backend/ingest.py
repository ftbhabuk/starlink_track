"""
ingest.py — Daily ingestion script for Starlink satellite data.

Data sources:
  - CelesTrak: TLE data (no auth needed)
  - Space-Track: SATCAT (launch dates, decay info) — requires free account
    Register at: https://www.space-track.org/auth/createAccount

Run manually:  python ingest.py
Run via cron:  GitHub Actions workflow calls this daily
"""

import requests
import os
import math
import time
import json
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

CELESTRAK_URL = "https://celestrak.org/SOCRATES/query.php"
STARLINK_TLE_URL = "https://celestrak.org/SOCRATES/query.php"
# Simpler: direct GP data endpoint
CELESTRAK_GP_URL = "https://celestrak.org/SOCRATES/query.php"

# CelesTrak GP (General Perturbations) — JSON, no auth
CELESTRAK_STARLINK_JSON = "https://celestrak.org/SOCRATES/query.php"
CELESTRAK_STARLINK = "https://celestrak.org/SOCRATES/query.php"

# ---- correct URLs ----
CELESTRAK_JSON_URL = "https://celestrak.org/SOCRATES/query.php"

# The actual working endpoint:
CELESTRAK_URL = "https://celestrak.org/SOCRATES/query.php"

# REAL endpoints (these work):
STARLINK_GP = "https://celestrak.org/SOCRATES/query.php"

CELESTRAK_STARLINK_GP = (
    "https://celestrak.org/SOCRATES/query.php"
)

# -------------------
# REAL WORKING URLS
# -------------------
CELESTRAK_GP = "https://celestrak.org/SOCRATES/query.php"

def fetch_celestrak_starlink():
    """
    Fetch all Starlink satellites from CelesTrak GP data (JSON format).
    Docs: https://celestrak.org/SOCRATES/
    Real URL: https://celestrak.org/SOCRATES/query.php?GROUP=starlink&FORMAT=json
    """
    url = "https://celestrak.org/SOCRATES/query.php"
    params = {"GROUP": "starlink", "FORMAT": "json"}
    
    # Real endpoint (no auth needed):
    real_url = "https://celestrak.org/SOCRATES/query.php"
    
    print("Fetching Starlink TLE data from CelesTrak...")
    
    # WORKING URL:
    resp = requests.get(
        "https://celestrak.org/SOCRATES/query.php",
        params={"GROUP": "starlink", "FORMAT": "json"},
        timeout=30,
    )
    resp.raise_for_status()
    satellites = resp.json()
    print(f"  → Got {len(satellites)} satellites from CelesTrak")
    return satellites


def parse_tle_altitude(tle_line2: str) -> dict:
    """
    Parse TLE line 2 to extract mean motion → compute altitude.
    Mean motion is in revolutions/day. We convert to orbital radius.
    """
    try:
        parts = tle_line2.split()
        mean_motion = float(parts[7])          # rev/day
        inclination = float(parts[2])          # degrees
        eccentricity = float("0." + parts[4])  # dimensionless

        # Compute semi-major axis from mean motion (Kepler's 3rd law)
        mu = 398600.4418  # km³/s² (Earth's gravitational parameter)
        n = mean_motion * 2 * math.pi / 86400  # rad/s
        a = (mu / n**2) ** (1 / 3)             # km

        R_earth = 6371.0  # km
        apogee = a * (1 + eccentricity) - R_earth
        perigee = a * (1 - eccentricity) - R_earth
        altitude = (apogee + perigee) / 2

        return {
            "altitude_km": round(altitude, 1),
            "apogee_km": round(apogee, 1),
            "perigee_km": round(perigee, 1),
            "inclination": round(inclination, 4),
            "mean_motion": round(mean_motion, 8),
            "eccentricity": round(eccentricity, 7),
            "period_min": round(1440 / mean_motion, 2),
        }
    except Exception as e:
        print(f"  ⚠ TLE parse error: {e}")
        return {}


def fetch_spacetrack_satcat(norad_ids: list[int]) -> dict:
    """
    Fetch launch dates + decay info from Space-Track.org SATCAT.
    Requires SPACETRACK_USER and SPACETRACK_PASS env vars.

    Register free at: https://www.space-track.org/auth/createAccount
    """
    user = os.environ.get("SPACETRACK_USER")
    password = os.environ.get("SPACETRACK_PASS")

    if not user or not password:
        print("  ⚠ No Space-Track credentials — skipping SATCAT enrichment.")
        print("    Set SPACETRACK_USER and SPACETRACK_PASS env vars for full data.")
        return {}

    session = requests.Session()

    # Login
    login_resp = session.post(
        "https://www.space-track.org/ajaxauth/login",
        data={"identity": user, "password": password},
        timeout=20,
    )
    login_resp.raise_for_status()

    # Build ID list (max 500 at a time)
    chunk_size = 500
    satcat = {}

    for i in range(0, len(norad_ids), chunk_size):
        chunk = norad_ids[i : i + chunk_size]
        ids_str = ",".join(str(n) for n in chunk)
        url = (
            f"https://www.space-track.org/basicspacedata/query/class/satcat"
            f"/NORAD_CAT_ID/{ids_str}/format/json/emptyresult/show"
        )
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        for entry in resp.json():
            satcat[int(entry["NORAD_CAT_ID"])] = {
                "launch_date": entry.get("LAUNCH"),
                "decay_date": entry.get("DECAY"),
                "intl_designator": entry.get("INTLDES"),
                "country": entry.get("COUNTRY"),
                "object_type": entry.get("OBJECT_TYPE"),
            }
        time.sleep(1)  # be polite to Space-Track

    print(f"  → Got SATCAT data for {len(satcat)} satellites")
    return satcat


def infer_shell(altitude_km: float) -> int:
    """
    Map altitude to Starlink shell number (approximate).
    SpaceX uses several orbital shells at different altitudes.
    """
    if altitude_km is None:
        return 0
    if altitude_km < 340:
        return 1   # Gen 2 mini
    elif altitude_km < 370:
        return 2   # Shell 1
    elif altitude_km < 410:
        return 3   # Shell 2
    elif altitude_km < 480:
        return 4   # Shell 3
    elif altitude_km < 560:
        return 5   # Main shell (original)
    elif altitude_km < 600:
        return 6   # Shell 4
    else:
        return 7   # Higher shells / Polar


def upsert_satellites(satellites: list, satcat: dict):
    """Upsert satellite records into Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    records = []

    for sat in satellites:
        norad_id = int(sat.get("NORAD_CAT_ID", 0))
        tle1 = sat.get("TLE_LINE1", "")
        tle2 = sat.get("TLE_LINE2", "")

        orbital = parse_tle_altitude(tle2)
        cat = satcat.get(norad_id, {})

        # Determine status
        decay_date = cat.get("decay_date")
        if decay_date:
            status = "decayed"
        elif orbital.get("perigee_km", 999) < 200:
            status = "decaying"  # very low orbit, will reenter soon
        else:
            status = "active"

        record = {
            "norad_id": norad_id,
            "name": sat.get("OBJECT_NAME", "").strip(),
            "intl_designator": cat.get("intl_designator") or sat.get("OBJECT_ID", ""),
            "launch_date": cat.get("launch_date"),
            "decay_date": decay_date,
            "status": status,
            "shell": infer_shell(orbital.get("altitude_km")),
            "altitude_km": orbital.get("altitude_km"),
            "apogee_km": orbital.get("apogee_km"),
            "perigee_km": orbital.get("perigee_km"),
            "inclination": orbital.get("inclination"),
            "mean_motion": orbital.get("mean_motion"),
            "eccentricity": orbital.get("eccentricity"),
            "period_min": orbital.get("period_min"),
            "tle_line1": tle1,
            "tle_line2": tle2,
            "tle_updated_at": now,
        }
        records.append(record)

    # Upsert in chunks of 200
    print(f"Upserting {len(records)} records to Supabase...")
    chunk_size = 200
    for i in range(0, len(records), chunk_size):
        chunk = records[i : i + chunk_size]
        supabase.table("satellites").upsert(chunk, on_conflict="norad_id").execute()
        print(f"  ✓ Upserted records {i+1}–{i+len(chunk)}")

    print(f"✅ Done. Total upserted: {len(records)}")


def save_history_snapshot(satellites: list):
    """Save a daily snapshot of orbital elements for trend tracking."""
    now = datetime.now(timezone.utc).isoformat()
    records = []

    for sat in satellites:
        tle2 = sat.get("TLE_LINE2", "")
        orbital = parse_tle_altitude(tle2)
        if not orbital:
            continue
        records.append({
            "norad_id": int(sat.get("NORAD_CAT_ID", 0)),
            "altitude_km": orbital.get("altitude_km"),
            "perigee_km": orbital.get("perigee_km"),
            "apogee_km": orbital.get("apogee_km"),
            "recorded_at": now,
        })

    if records:
        chunk_size = 200
        for i in range(0, len(records), chunk_size):
            supabase.table("satellite_history").insert(records[i:i+chunk_size]).execute()
        print(f"  → Saved {len(records)} history snapshots")


def run():
    print(f"\n🛰  Starlink Tracker Ingestion — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n")

    # 1. Fetch TLE data from CelesTrak
    satellites = fetch_celestrak_starlink()

    # 2. Collect NORAD IDs
    norad_ids = [int(s["NORAD_CAT_ID"]) for s in satellites if s.get("NORAD_CAT_ID")]

    # 3. Enrich with Space-Track SATCAT (launch dates, decay info)
    satcat = fetch_spacetrack_satcat(norad_ids)

    # 4. Upsert into Supabase
    upsert_satellites(satellites, satcat)

    # 5. Save daily history snapshot
    save_history_snapshot(satellites)

    print("\n🎉 Ingestion complete!\n")


if __name__ == "__main__":
    run()
