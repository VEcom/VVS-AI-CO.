"""ai_pm/disclaimer_injector.py — 절대선 #4: 면책 고지 주입.

모든 생성 문서에 AI 초안 면책 고지가 포함되도록 강제한다.
"""

from __future__ import annotations

REQUIRED_DISCLAIMER: str = "본 문서는 AI가 생성한 초안이며, 최종 검토가 필요합니다."


def has_disclaimer(doc: str) -> bool:
    """문서에 필수 면책 고지가 포함되어 있는지."""
    doc = "" if doc is None else str(doc)
    return REQUIRED_DISCLAIMER in doc


def inject(doc: str) -> str:
    """면책 고지가 없으면 문서 끝에 추가한다. 있으면 그대로 반환."""
    doc = "" if doc is None else str(doc)
    if has_disclaimer(doc):
        return doc
    separator = "" if doc.endswith("\n") or doc == "" else "\n\n"
    return f"{doc}{separator}{REQUIRED_DISCLAIMER}"
