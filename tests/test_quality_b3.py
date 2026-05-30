"""B-3 재작업 검수 — 산출물 품질 (한글·내용·채점).

핵심:
  - 한글 폰트가 PDF 에 임베드되어 깨지지 않음(■■■ 해결).
  - 8섹션 실제 콘텐츠(표 포함)가 렌더됨(더미 아님).
  - 채점이 내용 품질 반영: 빈/뼈대 문서는 저점, 충실한 문서는 고점.
  - 합성 데이터 [SYNTHETIC] 유지.
"""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

from ai_pm import document_renderer as dr  # noqa: E402
from ai_pm import fonts  # noqa: E402
from ai_pm.profile_blocks import build_profile  # noqa: E402
from ai_pm.sample_data import SAMPLE_COMPANY_L1, sample_company  # noqa: E402
from ai_pm.sandbox import SYNTHETIC_MARK, validate_synthetic  # noqa: E402
from ai_pm.vision_review import PASS_THRESHOLD, review_design  # noqa: E402

pdf_only = pytest.mark.skipif(not dr.pdf_available(), reason="reportlab missing")
pptx_only = pytest.mark.skipif(not dr.pptx_available(), reason="python-pptx missing")


# ── 1) 한글 폰트 ──
def test_korean_font_available():
    assert fonts.fonts_available() is True
    assert Path(fonts.font_path()).exists()
    assert Path(fonts.font_path(bold=True)).exists()


def test_reportlab_korean_font_registers():
    reg, bold = fonts.register_reportlab()
    assert reg == fonts.FONT_REGULAR and bold == fonts.FONT_BOLD


@pdf_only
def test_pdf_contains_embedded_korean_font(tmp_path):
    """렌더된 PDF 에 한글 폰트가 임베드(서브셋)되어 ■■■ 아님."""
    md = build_profile(sample_company("L1"), "L1")
    res = dr.render(dr.RenderSpec(title="회사소개서", level="L1", text=md),
                    tmp_path / "k.pdf", "pdf")
    raw = Path(res.path).read_bytes()
    assert res.bytes > 3000
    # 임베드 폰트명(서브셋 접두 포함)으로 NanumGothic 노출
    assert b"NanumGothic" in raw


# ── 2) 실제 콘텐츠 (8섹션, 표) ──
def test_profile_has_eight_sections():
    md = build_profile(sample_company("L1"), "L1")
    assert md.count("## ") == 8
    for kw in ["회사 개요", "연혁", "조직", "주요 실적", "인력", "장비", "안전", "연락처"]:
        assert kw in md


@pptx_only
def test_pptx_renders_tables_and_sections(tmp_path):
    md = build_profile(sample_company("L1"), "L1")
    res = dr.render(dr.RenderSpec(title="회사소개서", level="L1", text=md),
                    tmp_path / "p.pptx", "pptx")
    assert res.section_count == 8
    assert res.table_count >= 4
    assert res.table_rows >= 15
    assert res.slide_count >= 8


@pdf_only
def test_pdf_metrics_reflect_content(tmp_path):
    md = build_profile(sample_company("L1"), "L1")
    res = dr.render(dr.RenderSpec(title="회사소개서", level="L1", text=md),
                    tmp_path / "c.pdf", "pdf")
    assert res.content_chars > 600
    assert res.table_count >= 4
    assert res.bullet_count >= 5


# ── 3) 채점이 내용 품질 반영 (빈 페이지 저점) ──
@pdf_only
def test_empty_doc_scores_low(tmp_path):
    res = dr.render(dr.RenderSpec(title="빈문서", level="L1", text="# 제목\n한 줄."),
                    tmp_path / "e.pdf", "pdf")
    review = review_design(res)
    assert review.total < PASS_THRESHOLD
    assert review.passed is False
    assert any("빈약" in n or "보강" in n for n in review.notes)


@pdf_only
def test_rich_doc_scores_high(tmp_path):
    md = build_profile(sample_company("L1"), "L1")
    res = dr.render(dr.RenderSpec(title="회사소개서", level="L1", text=md),
                    tmp_path / "r.pdf", "pdf")
    review = review_design(res)
    assert review.total >= 80
    assert review.passed is True


@pdf_only
def test_rich_scores_higher_than_empty(tmp_path):
    md = build_profile(sample_company("L1"), "L1")
    rich = review_design(dr.render(dr.RenderSpec(title="t", level="L1", text=md),
                                   tmp_path / "rr.pdf", "pdf"))
    empty = review_design(dr.render(dr.RenderSpec(title="t", level="L1", text="# t\nx."),
                                    tmp_path / "ee.pdf", "pdf"))
    assert rich.total > empty.total + 30


# ── 4) 합성 데이터 [SYNTHETIC] 유지 ──
def test_sample_data_is_synthetic():
    validate_synthetic(SAMPLE_COMPANY_L1)
    md = build_profile(sample_company("L1"), "L1")
    assert SYNTHETIC_MARK in md


def test_sample_identifier_is_void():
    assert "000-00-00000" in SAMPLE_COMPANY_L1["overview"]["사업자등록번호"]


# ── 5) 레벨별 섹션 차등 ──
def test_level_section_counts():
    l1 = build_profile(sample_company(), "L1").count("## ")
    l2 = build_profile(sample_company(), "L2").count("## ")
    l4 = build_profile(sample_company(), "L4").count("## ")
    assert l1 == 8
    assert l2 < l1 and l4 < l2
    assert l4 >= 2
