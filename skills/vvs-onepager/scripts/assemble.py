"""vvs-onepager L4 1페이지 요약서 — 조립 스크립트.

block_library 블록 스펙을 만들고, ai_pm.production_pipeline 으로 절대선 게이트를
거쳐 전달한다. 송출 함수를 직접 호출하지 않는다(파이프라인이 게이트 강제).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_pm.production_pipeline import produce_and_deliver  # noqa: E402

_TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "onepager.blocks.json"


def _load_template() -> dict:
    with open(_TEMPLATE, encoding="utf-8") as fh:
        return json.load(fh)


def build_blocks(data: dict) -> list:
    """입력 데이터를 block_library 블록 스펙으로 변환 (1페이지: 간결)."""
    data = data or {}
    field_map = {
        "header": {"title": data.get("title", "1페이지 요약"), "date": data.get("date", "")},
        "company_intro": {
            "company": data.get("company", ""),
            "summary": data.get("summary", ""),
        },
        "footer": {"contact": data.get("contact", "")},
    }
    tmpl = _load_template()
    return [(bid, field_map.get(bid, {})) for bid in tmpl["blocks"]]


def run(data: dict, real_send, *, claims=None, **send_kwargs) -> dict:
    """1페이지 요약서를 조립 + 절대선 게이트 통과 시 전달."""
    tmpl = _load_template()
    blocks = build_blocks(data)
    return produce_and_deliver(
        real_send,
        blocks,
        doc_type=tmpl["doc_type"],
        claims=claims,
        **send_kwargs,
    )
