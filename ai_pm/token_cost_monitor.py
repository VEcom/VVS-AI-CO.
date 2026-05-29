"""ai_pm/token_cost_monitor.py — 토큰 사용량/비용 모니터.

모델별 토큰 사용량을 누적하고 USD 비용을 추정한다. 프로세스 내 누적
상태를 유지한다(테스트는 reset 으로 초기화).
"""

from __future__ import annotations

# 모델별 단가 (USD per 1K tokens). 근사치이며 운영 시 갱신.
PRICING: dict[str, float] = {
    "gpt-4": 0.03,
    "gpt-4o": 0.005,
    "claude": 0.015,
    "claude-opus": 0.015,
    "claude-sonnet": 0.003,
    "default": 0.01,
}

_TOTAL = {"tokens": 0, "cost_usd": 0.0}


def _rate(model: str) -> float:
    return PRICING.get(model, PRICING["default"])


def track(tokens: int, model: str) -> dict:
    """토큰 사용을 기록하고 이번 호출의 비용을 반환.

    반환: {"tokens": int, "model": str, "cost_usd": float}
    """
    tokens = int(tokens)
    if tokens < 0:
        raise ValueError("tokens must be non-negative")
    cost = round(tokens / 1000.0 * _rate(model), 6)
    _TOTAL["tokens"] += tokens
    _TOTAL["cost_usd"] = round(_TOTAL["cost_usd"] + cost, 6)
    return {"tokens": tokens, "model": model, "cost_usd": cost}


def get_total() -> dict:
    """누적 토큰/비용을 반환."""
    return {"tokens": _TOTAL["tokens"], "cost_usd": round(_TOTAL["cost_usd"], 6)}


def reset() -> None:
    """누적 상태 초기화(주로 테스트용)."""
    _TOTAL["tokens"] = 0
    _TOTAL["cost_usd"] = 0.0
