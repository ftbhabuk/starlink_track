"""
Sync SpaceX assets from SpaceXNow into local PostgreSQL.

Run:
  python sync_spacex_assets.py
"""

from __future__ import annotations

from datetime import datetime, timezone
import html
import json

import requests

from database import execute, executemany

BOOSTERS_URL = "https://spacexnow.com/boosters"
CAPSULES_URL = "https://spacexnow.com/capsules"


def _fetch_html(url: str) -> str:
    resp = requests.get(url, timeout=25)
    resp.raise_for_status()
    return html.unescape(resp.text)


def _status_from_text(value: str) -> str:
    lowered = (value or "").lower()
    if any(token in lowered for token in ["destroyed", "lost", "expended"]):
        return "destroyed"
    if "retired" in lowered:
        return "retired"
    if "inactive" in lowered:
        return "inactive"
    if "active" in lowered:
        return "active"
    return "unknown"


def _infer_booster_type(value: str) -> str:
    lowered = (value or "").lower()
    if "falcon heavy" in lowered:
        return "Falcon Heavy"
    if "falcon 9" in lowered or "falcon" in lowered:
        return "Falcon 9"
    return "Falcon"


def _extract_embedded_array(text: str, serial_prefix: str) -> list[dict]:
    marker = f'[{{"serial":"{serial_prefix}'
    start = text.find(marker)
    if start == -1:
        return []

    depth = 0
    end = None
    for idx, ch in enumerate(text[start:], start=start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = idx + 1
                break

    if not end:
        return []

    try:
        payload = json.loads(text[start:end])
    except json.JSONDecodeError:
        return []

    return payload if isinstance(payload, list) else []


def scrape_boosters() -> list[dict]:
    payload = _extract_embedded_array(_fetch_html(BOOSTERS_URL), "B")
    out = []
    for row in payload:
        serial = (row.get("serial") or "").upper().strip()
        if not serial.startswith("B"):
            continue
        details = row.get("details") or ""
        row_type = row.get("type") or ""
        out.append(
            {
                "serial": serial,
                "vehicle": "Falcon",
                "booster_type": _infer_booster_type(
                    f"{row_type} {details} {row.get('version') or ''}"
                ),
                "version": row.get("version"),
                "status": _status_from_text(row.get("status")),
                "flights": row.get("flights") or 0,
                "landings_success": (row.get("rtls_landings") or 0)
                + (row.get("asds_landings") or 0),
                "landings_attempts": (row.get("rtls_attempts") or 0)
                + (row.get("asds_attempts") or 0),
                "comment": details,
            }
        )
    return out


def scrape_capsules() -> list[dict]:
    payload = _extract_embedded_array(_fetch_html(CAPSULES_URL), "C")
    out = []
    for row in payload:
        capsule_id = (row.get("serial") or "").upper().strip()
        if not capsule_id.startswith("C"):
            continue
        out.append(
            {
                "capsule_id": capsule_id,
                "version": row.get("version") or row.get("mode"),
                "status": _status_from_text(row.get("status")),
                "flights": row.get("flights") or 0,
                "comment": row.get("details"),
            }
        )
    return out


def ensure_columns() -> None:
    execute("ALTER TABLE spacex_boosters ADD COLUMN IF NOT EXISTS booster_type TEXT")


def upsert_boosters(rows: list[dict]) -> None:
    now = datetime.now(timezone.utc)
    params = [
        (
            row["serial"],
            row["vehicle"],
            row.get("booster_type"),
            row.get("version"),
            row.get("status") or "unknown",
            row.get("flights") or 0,
            row.get("comment"),
            row.get("landings_success"),
            row.get("landings_attempts"),
            now,
        )
        for row in rows
    ]
    executemany(
        """
        INSERT INTO spacex_boosters (
            serial, vehicle, booster_type, version, status, flights, comment,
            landings_success, landings_attempts, updated_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (serial) DO UPDATE SET
            vehicle = EXCLUDED.vehicle,
            booster_type = COALESCE(EXCLUDED.booster_type, spacex_boosters.booster_type),
            version = COALESCE(EXCLUDED.version, spacex_boosters.version),
            status = EXCLUDED.status,
            flights = EXCLUDED.flights,
            comment = EXCLUDED.comment,
            landings_success = COALESCE(EXCLUDED.landings_success, spacex_boosters.landings_success),
            landings_attempts = COALESCE(EXCLUDED.landings_attempts, spacex_boosters.landings_attempts),
            updated_at = EXCLUDED.updated_at
        """,
        params,
    )


def upsert_capsules(rows: list[dict]) -> None:
    now = datetime.now(timezone.utc)
    params = [
        (
            row["capsule_id"],
            row.get("version"),
            row.get("status") or "unknown",
            row.get("flights") or 0,
            row.get("comment"),
            now,
        )
        for row in rows
    ]
    executemany(
        """
        INSERT INTO spacex_capsules (
            capsule_id, version, status, flights, comment, updated_at
        ) VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (capsule_id) DO UPDATE SET
            version = COALESCE(EXCLUDED.version, spacex_capsules.version),
            status = EXCLUDED.status,
            flights = EXCLUDED.flights,
            comment = EXCLUDED.comment,
            updated_at = EXCLUDED.updated_at
        """,
        params,
    )


def main() -> None:
    ensure_columns()
    boosters = scrape_boosters()
    capsules = scrape_capsules()
    if not boosters:
        raise RuntimeError("No boosters parsed from SpaceXNow")
    upsert_boosters(boosters)
    if capsules:
        upsert_capsules(capsules)
    print(f"Synced boosters={len(boosters)} capsules={len(capsules)} at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
