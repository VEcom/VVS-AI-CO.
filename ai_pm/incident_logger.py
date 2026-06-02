"""ai_pm/incident_logger.py — 인시던트 기록.

절대선 위반 등 사건을 incidents 테이블에 기록하고 조회한다. sqlite_db 의
스키마에 의존한다.
"""

from __future__ import annotations

import sqlite3


def log_incident(conn: sqlite3.Connection, incident: dict) -> int:
    """인시던트를 기록하고 새 행 id 를 반환.

    incident 예: {"kind": "absolute_line_violation",
                  "detail": "banned phrase: 절대", "severity": "high"}
    """
    kind = incident.get("kind")
    if not kind:
        raise ValueError("incident requires kind")
    cur = conn.execute(
        "INSERT INTO incidents (kind, detail, severity) VALUES (?, ?, ?)",
        (kind, incident.get("detail"), incident.get("severity", "info")),
    )
    conn.commit()
    return int(cur.lastrowid)


def get_incidents(conn: sqlite3.Connection) -> list[dict]:
    """모든 인시던트를 최신순으로 조회."""
    rows = conn.execute(
        "SELECT id, kind, detail, severity, created_at FROM incidents "
        "ORDER BY id DESC"
    ).fetchall()
    return [dict(row) for row in rows]
