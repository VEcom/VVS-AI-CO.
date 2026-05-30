"""ai_pm/document_renderer.py — 텍스트 산출물 → PDF/PPTX 렌더 (순수 렌더).

게이트를 거친(=정제된) 텍스트만 렌더한다. 이 모듈 자체는 절대선 검사를 하지
않는다 — 검사는 document_pipeline 이 렌더 **이전**에 강제한다(렌더물이 게이트를
우회하지 못하도록, 렌더는 게이트 통과 후에만 도달).

렌더 라이브러리(python-pptx / reportlab) 부재 시 RendererUnavailable 를 던져
우아하게 비활성화한다. 절대선 게이트(텍스트 검증)는 이 모듈에 의존하지 않는다.

브랜딩: VVS 기본 팔레트(네이비/그레이)와 레벨별 레이아웃을 적용한다.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path

# VVS 브랜드 팔레트 (RGB)
BRAND_NAVY = (0x1F, 0x2A, 0x44)
BRAND_ACCENT = (0x2E, 0x5A, 0xAC)
BRAND_GRAY = (0x55, 0x5A, 0x66)


class RendererUnavailable(RuntimeError):
    """렌더 라이브러리 부재."""


def _have(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def pptx_available() -> bool:
    return _have("pptx")


def pdf_available() -> bool:
    return _have("reportlab")


@dataclass
class RenderSpec:
    """렌더 입력. document_pipeline 이 게이트 통과 텍스트로 구성한다.

    title:    표지/머리말 제목
    sections: [(heading, body), ...] 순서대로 슬라이드/문단
    level:    L1/L2/L4 (레이아웃 힌트)
    text:     전체 본문(메타/검수용)
    """

    title: str
    sections: list = field(default_factory=list)
    level: str = "L1"
    text: str = ""


@dataclass
class RenderResult:
    """렌더 산출물 메타 (비전 검수·전달용)."""

    path: str
    fmt: str               # "pptx" | "pdf"
    level: str
    slide_count: int       # PPTX 슬라이드 수 / PDF 페이지 수
    title: str
    bytes: int


# ── 본문 → 섹션 분해 (heading/body) ──
def split_sections(text: str) -> list:
    """마크다운형 본문을 (heading, body) 리스트로 분해.

    '#'/'##' 머리말을 heading 으로, 이후 줄을 body 로 묶는다.
    heading 이 없으면 전체를 단일 무제목 섹션으로 둔다.
    """
    sections: list = []
    cur_head = ""
    cur_body: list = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if cur_head or cur_body:
                sections.append((cur_head, "\n".join(cur_body).strip()))
            cur_head = stripped.lstrip("#").strip()
            cur_body = []
        else:
            cur_body.append(line)
    if cur_head or cur_body:
        sections.append((cur_head, "\n".join(cur_body).strip()))
    return sections or [("", text or "")]


# ── PPTX 렌더 ──
def render_pptx(spec: RenderSpec, out_path: str | Path) -> RenderResult:
    """RenderSpec 을 .pptx 로 렌더한다. python-pptx 필요."""
    if not pptx_available():
        raise RendererUnavailable("python-pptx not installed")
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    sections = spec.sections or [("", spec.text)]

    # 표지 슬라이드
    cover = prs.slides.add_slide(blank)
    box = cover.shapes.add_textbox(Inches(0.8), Inches(2.6), Inches(11.7), Inches(2.0))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = spec.title or "VVS"
    run.font.size = Pt(40)
    run.font.bold = True
    run.font.color.rgb = RGBColor(*BRAND_NAVY)
    sub = tf.add_paragraph()
    srun = sub.add_run()
    srun.text = f"VVS · {spec.level}"
    srun.font.size = Pt(18)
    srun.font.color.rgb = RGBColor(*BRAND_ACCENT)

    # 내용 슬라이드 (섹션별)
    for heading, body in sections:
        slide = prs.slides.add_slide(blank)
        # 좌측 액센트 바 (브랜딩/정렬)
        bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.25), Inches(7.5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = RGBColor(*BRAND_ACCENT)
        bar.line.fill.background()
        # 제목
        htbox = slide.shapes.add_textbox(Inches(0.7), Inches(0.5), Inches(12.0), Inches(1.0))
        hp = htbox.text_frame.paragraphs[0]
        hr = hp.add_run()
        hr.text = heading or spec.title
        hr.font.size = Pt(28)
        hr.font.bold = True
        hr.font.color.rgb = RGBColor(*BRAND_NAVY)
        # 본문
        btbox = slide.shapes.add_textbox(Inches(0.7), Inches(1.7), Inches(12.0), Inches(5.2))
        btf = btbox.text_frame
        btf.word_wrap = True
        for i, ln in enumerate((body or "").splitlines() or [""]):
            para = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            r = para.add_run()
            r.text = ln
            r.font.size = Pt(16)
            r.font.color.rgb = RGBColor(*BRAND_GRAY)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    return RenderResult(
        path=str(out_path),
        fmt="pptx",
        level=spec.level,
        slide_count=len(prs.slides._sldIdLst),
        title=spec.title,
        bytes=out_path.stat().st_size,
    )


# ── PDF 렌더 ──
def render_pdf(spec: RenderSpec, out_path: str | Path) -> RenderResult:
    """RenderSpec 을 .pdf 로 렌더한다. reportlab 필요."""
    if not pdf_available():
        raise RendererUnavailable("reportlab not installed")
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    pages = 0

    def _new_page_header(title: str) -> float:
        nonlocal pages
        pages += 1
        # 상단 브랜드 바
        c.setFillColorRGB(*[v / 255 for v in BRAND_NAVY])
        c.rect(0, height - 18 * mm, width, 18 * mm, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(15 * mm, height - 12 * mm, f"VVS · {spec.level}")
        c.setFillColorRGB(*[v / 255 for v in BRAND_NAVY])
        c.setFont("Helvetica-Bold", 18)
        c.drawString(15 * mm, height - 30 * mm, title[:80])
        return height - 40 * mm

    sections = spec.sections or [("", spec.text)]
    y = _new_page_header(spec.title or "VVS")
    c.setFillColorRGB(*[v / 255 for v in BRAND_GRAY])
    c.setFont("Helvetica", 11)

    for heading, body in sections:
        if y < 30 * mm:
            c.showPage()
            y = _new_page_header(spec.title or "VVS")
            c.setFillColorRGB(*[v / 255 for v in BRAND_GRAY])
        if heading:
            c.setFont("Helvetica-Bold", 13)
            c.setFillColorRGB(*[v / 255 for v in BRAND_ACCENT])
            c.drawString(15 * mm, y, heading[:90])
            y -= 7 * mm
            c.setFont("Helvetica", 11)
            c.setFillColorRGB(*[v / 255 for v in BRAND_GRAY])
        for ln in (body or "").splitlines():
            if y < 20 * mm:
                c.showPage()
                y = _new_page_header(spec.title or "VVS")
                c.setFillColorRGB(*[v / 255 for v in BRAND_GRAY])
                c.setFont("Helvetica", 11)
            c.drawString(18 * mm, y, ln[:95])
            y -= 6 * mm
        y -= 4 * mm

    c.showPage()
    c.save()
    return RenderResult(
        path=str(out_path),
        fmt="pdf",
        level=spec.level,
        slide_count=pages,
        title=spec.title,
        bytes=out_path.stat().st_size,
    )


def render(spec: RenderSpec, out_path: str | Path, fmt: str) -> RenderResult:
    """fmt('pptx'|'pdf')에 맞춰 렌더한다."""
    fmt = fmt.lower()
    if fmt == "pptx":
        return render_pptx(spec, out_path)
    if fmt == "pdf":
        return render_pdf(spec, out_path)
    raise ValueError(f"unsupported fmt: {fmt!r}")
