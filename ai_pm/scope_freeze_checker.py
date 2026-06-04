"""ai_pm/scope_freeze_checker.py — 범위 동결 검사.

원본 범위와 현재 범위를 비교해 변경(추가·삭제·수정)을 감지한다.
"""

from __future__ import annotations


def check_scope(original: dict, current: dict) -> dict:
    """원본 대비 현재 범위의 변경을 감지.

    반환: {"frozen": bool, "changes": list[dict]}
      change: {"field": str, "type": "added|removed|modified",
               "from": ..., "to": ...}
    """
    original = original or {}
    current = current or {}
    changes: list[dict] = []

    for key in original:
        if key not in current:
            changes.append({"field": key, "type": "removed", "from": original[key], "to": None})
        elif original[key] != current[key]:
            changes.append(
                {"field": key, "type": "modified", "from": original[key], "to": current[key]}
            )

    for key in current:
        if key not in original:
            changes.append({"field": key, "type": "added", "from": None, "to": current[key]})

    return {"frozen": not changes, "changes": changes}
