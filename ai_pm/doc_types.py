"""ai_pm/doc_types.py — VVS 문서 유형 정의.

반도체 협력사 AI 문서제작이 다루는 문서 유형과 각 유형의 법무 검토 필요
여부·필수 섹션을 정의한다. legal_safety_router·quality_rubric 등이 참조한다.
"""

from __future__ import annotations


class UnknownDocTypeError(KeyError):
    """정의되지 않은 문서 유형."""


# 문서 유형 정의. requires_legal=True 이면 legal_safety_router 가 법무 라우팅.
DOC_TYPES: dict[str, dict] = {
    "견적서": {
        "name": "견적서",
        "requires_legal": False,
        "sections": ["header", "company_intro", "quote_table", "terms", "footer"],
    },
    "제안서": {
        "name": "제안서",
        "requires_legal": False,
        "sections": ["header", "company_intro", "background", "solution", "footer"],
    },
    "회사소개서": {
        "name": "회사소개서",
        "requires_legal": False,
        "sections": ["header", "company_intro", "history", "capabilities", "footer"],
    },
    "기술문서": {
        "name": "기술문서",
        "requires_legal": False,
        "sections": ["header", "overview", "specification", "appendix", "footer"],
    },
    "계약서": {
        "name": "계약서",
        "requires_legal": True,
        "sections": ["header", "parties", "terms", "liability", "signature", "footer"],
    },
}


def get_type(name: str) -> dict:
    """문서 유형 정의를 반환. 없으면 UnknownDocTypeError."""
    try:
        return DOC_TYPES[name]
    except KeyError as exc:
        raise UnknownDocTypeError(f"unknown doc type: {name!r}") from exc


def list_types() -> list[str]:
    """정의된 모든 문서 유형 이름."""
    return list(DOC_TYPES.keys())
