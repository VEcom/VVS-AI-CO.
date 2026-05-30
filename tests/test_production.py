"""제작 모듈 단위테스트: doc_types · block_library · quality_rubric."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_pm import block_library, doc_types, quality_rubric  # noqa: E402
from ai_pm.disclaimer_injector import REQUIRED_DISCLAIMER  # noqa: E402


def test_doc_types_get():
    t = doc_types.get_type("견적서")
    assert t["name"] == "견적서" and "sections" in t


def test_doc_types_contract_requires_legal():
    assert doc_types.get_type("계약서")["requires_legal"] is True


def test_doc_types_unknown():
    with pytest.raises(doc_types.UnknownDocTypeError):
        doc_types.get_type("없는유형")


def test_block_render():
    out = block_library.render_block("header", {"title": "견적서", "date": "2026-05-29"})
    assert "견적서" in out and "2026-05-29" in out


def test_block_missing_field_safe():
    out = block_library.render_block("footer", {})  # contact 누락
    assert "문의:" in out


def test_block_unknown():
    with pytest.raises(block_library.UnknownBlockError):
        block_library.get_block("nope")


def test_rubric_pass():
    doc = {
        "sections": {"a": "x", "b": "y"},
        "required_sections": ["a", "b"],
        "facts": [{"verified": True}],
        "text": "충분히 긴 본문 내용입니다. " * 5 + REQUIRED_DISCLAIMER,
    }
    r = quality_rubric.score(doc)
    assert r["total"] == 100 and r["passed"] is True


def test_rubric_fail_on_banned_and_no_disclaimer():
    doc = {
        "sections": {},
        "required_sections": ["a", "b"],
        "facts": [{"verified": False}],
        "text": "무조건 최고",  # 금지표현 + 면책 없음 + 짧음
    }
    r = quality_rubric.score(doc)
    assert r["passed"] is False and r["total"] < 70
