"""ai_pm/banned_phrase_filter.py — 절대선 #3: 금지 표현 필터.

banned_phrases.BANNED 를 사용해 텍스트의 과장·단정 표현을 검사·차단한다.
"""

from __future__ import annotations

from .banned_phrases import BANNED


class BannedPhraseError(Exception):
    """금지 표현 위반."""


def filter_text(text: str) -> dict:
    """텍스트에서 금지 표현 위반을 찾는다.

    반환: {"clean": bool, "violations": list[str]}
    """
    text = "" if text is None else str(text)
    violations = [phrase for phrase in BANNED if phrase in text]
    return {"clean": not violations, "violations": violations}


def check_and_raise(text: str) -> None:
    """위반이 있으면 BannedPhraseError 를 발생시킨다."""
    result = filter_text(text)
    if not result["clean"]:
        raise BannedPhraseError(
            "banned phrases found: " + ", ".join(result["violations"])
        )
