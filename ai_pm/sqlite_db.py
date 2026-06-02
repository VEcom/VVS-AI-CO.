"""ai_pm/sqlite_db.py — sandbox 격리 SQLite 접근.

DB 파일은 반드시 sandbox 트리 안에만 생성된다(절대선 #2 격리). production
경로 탈출은 Sandbox.path 가 차단한다.
"""

from __future__ import annotations

import os
import sqlite3

from .sandbox import Sandbox

# 기본 sandbox 루트. 환경변수로 재정의 가능(B-1에서 HERMES_HOME 격리와 통합).
_DEFAULT_SANDBOX_ROOT = os.environ.get(
    "VVS_SANDBOX_ROOT", os.path.join(os.getcwd(), ".vvs_sandbox")
)


def open_sandboxed(relpath: str, sandbox_root: str | None = None) -> sqlite3.Connection:
    """sandbox 트리 내 상대경로에 SQLite 연결을 연다.

    relpath 가 sandbox 밖으로 탈출하면 Sandbox 가 SandboxEscapeError 를 던진다.
    """
    sandbox = Sandbox(sandbox_root or _DEFAULT_SANDBOX_ROOT)
    db_path = sandbox.path(relpath)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """documents·patterns·incidents 테이블을 생성한다(존재 시 무시)."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type    TEXT NOT NULL,
            content     TEXT,
            score       INTEGER,
            created_at  TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS patterns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type    TEXT NOT NULL,
            pattern     TEXT NOT NULL,
            score       INTEGER,
            created_at  TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS incidents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            kind        TEXT NOT NULL,
            detail      TEXT,
            severity    TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );
        """
    )
    conn.commit()
