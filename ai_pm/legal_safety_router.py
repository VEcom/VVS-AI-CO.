"""ai_pm/legal_safety_router.py — 절대선 #5: 법무 안전 라우팅.

계약·보증·법적 책임 관련 문서/내용을 법무 검토 경로로 라우팅한다.
"""

from __future__ import annotations

# 법무 검토를 유발하는 트리거 키워드 (정확히)
LEGAL_TRIGGERS: list[str] = ["계약", "보증", "법적", "책임", "배상", "위약금"]


def route(doc_type: str, content: str) -> dict:
    """문서 유형·내용을 보고 법무 검토 필요 여부를 판정한다.

    반환: {"requires_legal": bool, "reason": str}
    """
    doc_type = "" if doc_type is None else str(doc_type)
    content = "" if content is None else str(content)

    # 문서 유형 자체가 계약/법률/보증류면 즉시 법무
    type_triggers = [t for t in LEGAL_TRIGGERS if t in doc_type]
    if doc_type in ("계약서",) or type_triggers:
        reason = f"doc_type triggers legal review: {doc_type!r}"
        return {"requires_legal": True, "reason": reason}

    # 내용에 트리거 키워드가 있으면 법무
    hits = [t for t in LEGAL_TRIGGERS if t in content]
    if hits:
        return {
            "requires_legal": True,
            "reason": "content triggers: " + ", ".join(hits),
        }

    return {"requires_legal": False, "reason": "no legal triggers"}
