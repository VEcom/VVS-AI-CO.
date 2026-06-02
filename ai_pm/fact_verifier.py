"""ai_pm/fact_verifier.py — 절대선 #1: 사실 검증.

합성 데이터만 허용하고(절대선 #2 격리와 연동), 출처 없는 주장·근거 없는
숫자 주장을 거부한다. 헌법의 일부이므로 계약(시그니처·예외·반환)을 정확히
지킨다.
"""

from __future__ import annotations

from .sandbox import (  # noqa: F401  (SYNTHETIC_MARK 재노출 목적 포함)
    SYNTHETIC_MARK,
    SyntheticMarkingError,
    assert_invalid_identifier,
    validate_synthetic,
)


def _has_number(value) -> bool:
    """주장 값에 숫자가 포함되어 있는지."""
    if isinstance(value, (int, float)):
        return True
    text = str(value)
    return any(ch.isdigit() for ch in text)


def verify_fact(claim: dict) -> dict:
    """주장(claim)을 검증한다.

    claim 예: {"synthetic": True, "marking": "[SYNTHETIC]",
               "statement": "...", "source": "...", "evidence": "...",
               "value": 12}

    규칙:
      - 합성 데이터만 허용 (validate_synthetic). 위반 시 verified=False.
      - 출처(source) 없으면 verified=False.
      - 숫자 주장(value/statement에 숫자)은 근거(evidence) 필수.

    반환: {"verified": bool, "reason": str}
    """
    if not isinstance(claim, dict):
        return {"verified": False, "reason": "claim must be a dict"}

    # 합성 데이터만 허용 (절대선 #2 연동)
    try:
        validate_synthetic(claim)
    except SyntheticMarkingError as exc:
        return {"verified": False, "reason": f"synthetic check failed: {exc}"}

    # 출처 필수
    source = claim.get("source")
    if not source:
        return {"verified": False, "reason": "missing source"}

    # 숫자 주장은 근거 필수
    numeric = _has_number(claim.get("value", "")) or _has_number(
        claim.get("statement", "")
    )
    if numeric and not claim.get("evidence"):
        return {"verified": False, "reason": "numeric claim requires evidence"}

    return {"verified": True, "reason": "ok"}
