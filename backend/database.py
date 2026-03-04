"""
database.py — Postgres connection pool.
All other files import `get_conn` from here.
"""

import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# Connection string from .env
DB_URL = os.environ["DATABASE_URL"]
# e.g. postgresql://starlink_user:starlink123@localhost:5432/starlink_tracker


def get_conn():
    """Open and return a new DB connection. Use as a context manager."""
    return psycopg.connect(DB_URL, row_factory=psycopg.rows.dict_row)


def fetchall(sql: str, params=None):
    """Run a SELECT, return list of dicts."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()


def fetchone(sql: str, params=None):
    """Run a SELECT, return single dict or None."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()


def execute(sql: str, params=None):
    """Run INSERT/UPDATE/DELETE. Auto-commits."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()


def executemany(sql: str, params_list: list):
    """Run INSERT/UPDATE for a list of param tuples. Auto-commits."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, params_list)
        conn.commit()