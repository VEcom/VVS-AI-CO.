"""vvs-deliverable-doc 공통 — 블록 조립 헬퍼.

레벨별 템플릿으로 block_library 블록 스펙을 만든다. 송출/렌더는 하지 않는다
(build_pptx/build_pdf 가 document_pipeline 으로 게이트+렌더+전달).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "deliverable.blocks.json"


def load_levels() -> dict:
    with open(_TEMPLATE, encoding="utf-8") as fh:
        return json.load(fh)["levels"]


def level_config(level: str) -> dict:
    levels = load_levels()
    if level not in levels:
        raise ValueError(f"unknown level {level!r}; expected one of {sorted(levels)}")
    return levels[level]


def build_blocks(data: dict, level: str) -> tuple[list, str]:
    """입력 데이터 → (블록 스펙, doc_type). 레벨 템플릿 순서를 따른다."""
    data = data or {}
    cfg = level_config(level)
    field_map = {
        "header": {"title": data.get("title", "VVS 산출물"), "date": data.get("date", "")},
        "company_intro": {
            "company": data.get("company", ""),
            "summary": data.get("summary", ""),
        },
        "terms": {"terms": data.get("terms", "")},
        "footer": {"contact": data.get("contact", "")},
    }
    blocks = [(bid, field_map.get(bid, {})) for bid in cfg["blocks"]]
    return blocks, cfg["doc_type"]
