"""SQLite helpers for session and mapping persistence."""

import json
import sqlite3
from typing import Any, Dict, Optional

from codeabstract.config.settings import DB_PATH


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                privacy_level TEXT NOT NULL,
                source_code_hash TEXT NOT NULL,
                encrypted_mapping BLOB NOT NULL,
                metadata TEXT
            )
            """
        )
    conn.close()


def store_session(
    session_id: str,
    privacy_level: str,
    source_code_hash: str,
    encrypted_mapping: bytes,
    metadata: Dict[str, Any],
) -> None:
    conn = get_conn()
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions
            (session_id, privacy_level, source_code_hash, encrypted_mapping, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, privacy_level, source_code_hash, encrypted_mapping, json.dumps(metadata)),
        )
    conn.close()


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    out = dict(row)
    out["metadata"] = json.loads(out["metadata"]) if out.get("metadata") else {}
    return out

