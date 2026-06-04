"""ai_pm/delivery_start_gate.py — 착수 전 게이트.

납품/제작 착수 전 충족해야 할 체크리스트를 검사해, 미충족 항목(blockers)이
하나라도 있으면 착수를 막는다.
"""

from __future__ import annotations

# 착수 전 필수 체크 항목
REQUIRED_CHECKS: list[str] = [
    "scope_frozen",        # 범위 동결됨
    "legal_cleared",       # 법무 검토 완료(필요 시)
    "absolute_line_passed",# 절대선 통과
    "customer_approved",   # 고객 승인
]


def can_start(checklist: dict) -> dict:
    """체크리스트를 검사.

    반환: {"can_start": bool, "blockers": list[str]}
    """
    checklist = checklist or {}
    blockers = [check for check in REQUIRED_CHECKS if not checklist.get(check)]
    return {"can_start": not blockers, "blockers": blockers}
