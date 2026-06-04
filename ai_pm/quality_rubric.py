"""ai_pm/quality_rubric.py — 문서 품질 채점 루브릭.

문서를 완전성·정확성·절대선준수·가독성 4기준(각 25점)으로 채점한다.
70점 미만은 실패. 절대선준수 기준은 banned_phrase_filter·disclaimer 검사와
연동한다.
"""

from __future__ import annotations

from .banned_phrase_filter import filter_text
from .disclaimer_injector import has_disclaimer

# 채점 기준 (각 25점, 합 100)
RUBRIC: dict[str, int] = {
    "completeness": 25,  # 완전성
    "accuracy": 25,      # 정확성
    "absolute_line": 25, # 절대선준수
    "readability": 25,   # 가독성
}

PASS_THRESHOLD = 70


def _score_completeness(doc: dict) -> int:
    """필수 섹션이 모두 채워졌는지로 완전성 채점."""
    sections = doc.get("sections") or {}
    required = doc.get("required_sections") or list(sections.keys())
    if not required:
        return 0
    filled = sum(1 for s in required if sections.get(s))
    return round(RUBRIC["completeness"] * filled / len(required))


def _score_accuracy(doc: dict) -> int:
    """검증된 주장 비율로 정확성 채점."""
    facts = doc.get("facts") or []
    if not facts:
        # 주장이 없으면 정확성 만점(검증 대상 없음)
        return RUBRIC["accuracy"]
    verified = sum(1 for f in facts if f.get("verified"))
    return round(RUBRIC["accuracy"] * verified / len(facts))


def _score_absolute_line(doc: dict) -> int:
    """절대선준수: 금지표현 없음 + 면책고지 포함."""
    text = doc.get("text", "")
    score = RUBRIC["absolute_line"]
    if not filter_text(text)["clean"]:
        score -= 13  # 금지표현 위반
    if not has_disclaimer(text):
        score -= 12  # 면책고지 누락
    return max(0, score)


def _score_readability(doc: dict) -> int:
    """가독성: 본문 길이가 적정 범위면 만점."""
    text = doc.get("text", "")
    length = len(text)
    if length == 0:
        return 0
    if length < 50:
        return round(RUBRIC["readability"] * 0.5)
    return RUBRIC["readability"]


def score(doc: dict) -> dict:
    """문서를 채점한다.

    반환: {"total": int, "breakdown": dict, "passed": bool}
    """
    doc = doc or {}
    breakdown = {
        "completeness": _score_completeness(doc),
        "accuracy": _score_accuracy(doc),
        "absolute_line": _score_absolute_line(doc),
        "readability": _score_readability(doc),
    }
    total = sum(breakdown.values())
    return {
        "total": total,
        "breakdown": breakdown,
        "passed": total >= PASS_THRESHOLD,
    }
