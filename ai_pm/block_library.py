"""ai_pm/block_library.py — 재사용 문서 블록 라이브러리.

견적서·제안서 등이 공유하는 문서 블록(머리말·회사소개·견적표·약관·꼬리말)을
정의하고 데이터로 렌더링한다.
"""

from __future__ import annotations


class UnknownBlockError(KeyError):
    """정의되지 않은 블록."""


# 재사용 블록 정의. template 는 str.format 으로 렌더링한다.
BLOCKS: dict[str, dict] = {
    "header": {
        "id": "header",
        "fields": ["title", "date"],
        "template": "# {title}\n작성일: {date}",
    },
    "company_intro": {
        "id": "company_intro",
        "fields": ["company", "summary"],
        "template": "## 회사 소개\n{company}\n{summary}",
    },
    "quote_table": {
        "id": "quote_table",
        "fields": ["item", "qty", "price"],
        "template": "## 견적\n| 품목 | 수량 | 단가 |\n|---|---|---|\n| {item} | {qty} | {price} |",
    },
    "terms": {
        "id": "terms",
        "fields": ["terms"],
        "template": "## 거래 조건\n{terms}",
    },
    "footer": {
        "id": "footer",
        "fields": ["contact"],
        "template": "---\n문의: {contact}",
    },
}


def get_block(block_id: str) -> dict:
    """블록 정의를 반환. 없으면 UnknownBlockError."""
    try:
        return BLOCKS[block_id]
    except KeyError as exc:
        raise UnknownBlockError(f"unknown block: {block_id!r}") from exc


def render_block(block_id: str, data: dict) -> str:
    """블록을 데이터로 렌더링한다. 누락 필드는 빈 문자열로 채운다."""
    block = get_block(block_id)
    data = data or {}
    safe = {field: data.get(field, "") for field in block["fields"]}
    return block["template"].format(**safe)
