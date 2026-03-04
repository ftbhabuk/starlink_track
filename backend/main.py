from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from database import fetchall, fetchone

app = FastAPI(title="Starlink Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Starlink Tracker API 🛰", "docs": "/docs"}


@app.get("/satellites")
def list_satellites(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    shell: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
):
    # Build WHERE clauses dynamically
    conditions = []
    params = []

    if status:
        conditions.append("status = %s")
        params.append(status)
    if shell:
        conditions.append("shell = %s")
        params.append(shell)
    if search:
        conditions.append("(name ILIKE %s OR CAST(norad_id AS TEXT) = %s)")
        params.append(f"%{search}%")
        params.append(search)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    # Get paginated rows
    rows = fetchall(
        f"SELECT * FROM satellites {where} ORDER BY norad_id LIMIT %s OFFSET %s",
        params + [limit, offset],
    )

    # Get total count (same filters, no limit)
    count_row = fetchone(
        f"SELECT COUNT(*) AS total FROM satellites {where}",
        params,
    )

    return {
        "total": count_row["total"],
        "limit": limit,
        "offset": offset,
        "data": [dict(r) for r in rows],
    }


@app.get("/satellites/{norad_id}")
def get_satellite(norad_id: int):
    row = fetchone("SELECT * FROM satellites WHERE norad_id = %s", (norad_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Satellite not found")
    return dict(row)


@app.get("/satellites/{norad_id}/history")
def get_history(norad_id: int):
    rows = fetchall(
        """
        SELECT altitude_km, perigee_km, apogee_km, recorded_at
        FROM satellite_history
        WHERE norad_id = %s
        ORDER BY recorded_at DESC
        LIMIT 90
        """,
        (norad_id,),
    )
    return [dict(r) for r in rows]


@app.get("/stats")
def get_stats():
    row = fetchone(
        """
        SELECT
            COUNT(*)                                        AS total,
            COUNT(*) FILTER (WHERE status = 'active')      AS active,
            COUNT(*) FILTER (WHERE status = 'decayed')     AS decayed,
            COUNT(*) FILTER (WHERE status = 'decaying')    AS decaying,
            COUNT(*) FILTER (WHERE status = 'unknown')     AS unknown,
            ROUND(AVG(altitude_km) FILTER (
                WHERE status = 'active' AND altitude_km IS NOT NULL
            )::numeric, 1)                                 AS avg_altitude_km
        FROM satellites
        """
    )
    return dict(row)