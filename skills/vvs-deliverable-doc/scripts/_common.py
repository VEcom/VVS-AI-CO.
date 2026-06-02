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
    """입력 데이터 → (블록 스펙, doc_type).

    원청 제출 수준 회사소개서(8섹션, 표 포함)를 위해 동적 'profile' 블록을
    사용한다. data 는 sample_data.SAMPLE_COMPANY_L1 구조(또는 실데이터).
    """
    data = data or {}
    cfg = level_config(level)
    blocks = [("profile", {"_company": data, "_level": level})]
    return blocks, cfg["doc_type"]
