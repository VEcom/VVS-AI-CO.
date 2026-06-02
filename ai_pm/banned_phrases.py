"""ai_pm/banned_phrases.py — 절대선 #3 토대: 금지 표현 목록.

과장·단정 표현 금지 목록. banned_phrase_filter 가 이를 사용해 검사한다.
헌법의 일부이므로 목록을 정확히 유지한다.
"""

from __future__ import annotations

# 과장/단정 표현 금지 목록 (정확히)
BANNED: list[str] = [
    "100% 보장",
    "절대",
    "확실히",
    "무조건",
    "최고",
    "1위",
    "유일한",
]


def get_banned() -> list[str]:
    """금지 표현 목록의 복사본을 반환."""
    return list(BANNED)
