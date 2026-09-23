"""Database access and initialization layer for TechNova Business Operations."""

import sqlite3
from typing import Any, Dict, List, Optional
from backend.config import settings
from backend.data.seed_data import generate_all_data

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database. Generates seed data if DB does not exist."""
    if not settings.DB_PATH.exists():
        generate_all_data()
    
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Executes a read-only SQL query and returns a list of dictionary rows."""
    # Enforce read-only constraint for Responsible AI
    normalized = query.strip().upper()
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]
    if any(normalized.startswith(verb) for verb in forbidden):
        raise PermissionError(f"Security Alert: Agent attempted forbidden SQL write operation: {query[:30]}...")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def execute_scalar(query: str, params: tuple = ()) -> Any:
    """Executes a query and returns a single scalar value."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

def ensure_db_ready():
    """Validates that SQLite database exists and has records."""
    if not settings.DB_PATH.exists():
        generate_all_data()
