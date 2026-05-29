"""ai_pm/pattern_db.py — 성공 패턴 저장/조회.

문서 유형별 성공 패턴을 patterns 테이블에 저장하고 조회한다. sqlite_db 의
스키마에 의존한다.
"""

from __future__ import annotations

import json
import sqlite3


def save_pattern(conn: sqlite3.Connection, pattern: dict) -> int:
    """패턴을 저장하고 새 행 id 를 반환.

    pattern 예: {"doc_type": "견적서", "pattern": {...}, "score": 88}
    """
    doc_type = pattern.get("doc_type")
    if not doc_type:
        raise ValueError("pattern requires doc_type")
    body = pattern.get("pattern", {})
    payload = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
    cur = conn.execute(
        "INSERT INTO patterns (doc_type, pattern, score) VALUES (?, ?, ?)",
        (doc_type, payload, pattern.get("score")),
    )
    conn.commit()
    return int(cur.lastrowid)


def find_patterns(conn: sqlite3.Connection, doc_type: str) -> list[dict]:
    """문서 유형의 패턴을 점수 내림차순으로 조회."""
    rows = conn.execute(
        "SELECT id, doc_type, pattern, score, created_at FROM patterns "
        "WHERE doc_type = ? ORDER BY score DESC, id DESC",
        (doc_type,),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["pattern"] = json.loads(item["pattern"])
        except (json.JSONDecodeError, TypeError):
            pass  # 평문 패턴은 그대로 둔다
        result.append(item)
    return result
