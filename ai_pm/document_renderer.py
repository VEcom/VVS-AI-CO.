"""ai_pm/document_renderer.py — 마크다운 본문 → PDF/PPTX 렌더 (순수 렌더, 한글).

게이트를 거친(=정제된) 마크다운 텍스트만 렌더한다. 이 모듈은 절대선 검사를
하지 않는다 — 검사는 document_pipeline 이 렌더 **이전**에 강제한다(렌더물이
게이트를 우회하지 못하도록, 렌더는 게이트 통과 후에만 도달).

기능:
  - 한글 폰트(NanumGothic) 임베드 → PDF 한글 정상(■■■ 해결).
  - 마크다운 파싱(제목/표/불릿/문단) → PDF 표·PPTX 네이티브 표로 렌더.
  - RenderResult 에 콘텐츠 메트릭(표·문단·정보량) 노출 → 내용 품질 채점 근거.

라이브러리 부재 시 RendererUnavailable 로 우아 비활성화(게이트는 무영향).
"""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import fonts

# VVS 브랜드 팔레트 (RGB)
BRAND_NAVY = (0x1F, 0x2A, 0x44)
BRAND_ACCENT = (0x2E, 0x5A, 0xAC)
BRAND_GRAY = (0x55, 0x5A, 0x66)
BRAND_LIGHT = (0xED, 0xF1, 0xF8)


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
    """렌더 입력. document_pipeline 이 게이트 통과 텍스트로 구성한다."""

    title: str
    sections: list = field(default_factory=list)  # 하위호환
    level: str = "L1"
    text: str = ""


@dataclass
class RenderResult:
    """렌더 산출물 메타 (비전 검수·전달용)."""

    path: str
    fmt: str
    level: str
    slide_count: int
    title: str
    bytes: int
    section_count: int = 0
    table_count: int = 0
    table_rows: int = 0
    bullet_count: int = 0
    paragraph_count: int = 0
    content_chars: int = 0


# ════════════════════════════════════════════════════════════════════
# 마크다운 파서
# ════════════════════════════════════════════════════════════════════
@dataclass
class Element:
    kind: str               # "para" | "table" | "bullets"
    text: str = ""
    rows: list = field(default_factory=list)
    items: list = field(default_factory=list)


@dataclass
class Section:
    heading: str
    elements: list = field(default_factory=list)


@dataclass
class Document:
    title: str
    subtitle_lines: list
    sections: list


_TABLE_SEP = re.compile(r"^\s*[|]?\s*:?-{2,}.*$")


def _split_row(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_markdown(text: str) -> Document:
    """마크다운 본문을 Document(표지 + 섹션[요소]) 로 파싱."""
    lines = (text or "").splitlines()
    title = ""
    subtitle: list = []
    sections: list = []
    cur: Section | None = None

    i = 0
    n = len(lines)
    # 표지
    while i < n:
        s = lines[i].strip()
        if s.startswith("# ") and not s.startswith("## "):
            title = s[2:].strip()
            i += 1
            while i < n and not lines[i].strip().startswith("## "):
                t = lines[i].strip()
                if t and t != "---":
                    subtitle.append(t)
                i += 1
            break
        i += 1

    para_buf: list = []

    def _flush_para():
        nonlocal cur
        body = "\n".join(para_buf).strip()
        if body:
            if cur is None:
                cur = Section(heading="")
            cur.elements.append(Element(kind="para", text=body))

    while i < n:
        raw = lines[i]
        s = raw.strip()
        if s.startswith("## "):
            _flush_para(); para_buf.clear()
            if cur is not None:
                sections.append(cur)
            cur = Section(heading=s[3:].strip())
            i += 1
            continue
        if s.startswith("|"):
            _flush_para(); para_buf.clear()
            tbl: list = []
            while i < n and lines[i].strip().startswith("|"):
                ln = lines[i].strip()
                if _TABLE_SEP.match(ln):
                    i += 1
                    continue
                tbl.append(_split_row(ln))
                i += 1
            if cur is None:
                cur = Section(heading="")
            cur.elements.append(Element(kind="table", rows=tbl))
            continue
        if s.startswith("- "):
            _flush_para(); para_buf.clear()
            items: list = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            if cur is None:
                cur = Section(heading="")
            cur.elements.append(Element(kind="bullets", items=items))
            continue
        if s == "" or s == "---":
            _flush_para(); para_buf.clear()
            i += 1
            continue
        para_buf.append(raw)
        i += 1

    _flush_para()
    if cur is not None:
        sections.append(cur)
    return Document(title=title or "", subtitle_lines=subtitle, sections=sections)


def _metrics(doc: Document) -> dict:
    tables = rows = bullets = paras = chars = 0
    for sec in doc.sections:
        chars += len(sec.heading)
        for el in sec.elements:
            if el.kind == "table":
                tables += 1
                rows += max(0, len(el.rows) - 1)
                chars += sum(len(c) for r in el.rows for c in r)
            elif el.kind == "bullets":
                bullets += len(el.items)
                chars += sum(len(x) for x in el.items)
            else:
                paras += 1
                chars += len(el.text)
    return {
        "section_count": len(doc.sections),
        "table_count": tables,
        "table_rows": rows,
        "bullet_count": bullets,
        "paragraph_count": paras,
        "content_chars": chars,
    }


def split_sections(text: str) -> list:
    """하위호환: (heading, body) 리스트."""
    doc = parse_markdown(text)
    out = []
    for sec in doc.sections:
        body = []
        for el in sec.elements:
            if el.kind == "para":
                body.append(el.text)
            elif el.kind == "bullets":
                body.extend(f"- {x}" for x in el.items)
            elif el.kind == "table":
                for r in el.rows:
                    body.append(" | ".join(r))
        out.append((sec.heading, "\n".join(body).strip()))
    return out or [("", text or "")]


# ════════════════════════════════════════════════════════════════════
# PDF 렌더 (reportlab Platypus, 한글)
# ════════════════════════════════════════════════════════════════════
def render_pdf(spec: RenderSpec, out_path: str | Path) -> RenderResult:
    if not pdf_available():
        raise RendererUnavailable("reportlab not installed")
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        ListFlowable,
        ListItem,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    reg, bold = fonts.register_reportlab()
    doc_model = parse_markdown(spec.text)
    metrics = _metrics(doc_model)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    navy = colors.Color(*[v / 255 for v in BRAND_NAVY])
    accent = colors.Color(*[v / 255 for v in BRAND_ACCENT])
    gray = colors.Color(*[v / 255 for v in BRAND_GRAY])
    light = colors.Color(*[v / 255 for v in BRAND_LIGHT])

    title_style = ParagraphStyle("t", fontName=bold, fontSize=26, textColor=navy,
                                 leading=32, spaceAfter=6)
    sub_style = ParagraphStyle("s", fontName=reg, fontSize=12, textColor=accent, leading=18)
    h2_style = ParagraphStyle("h2", fontName=bold, fontSize=15, textColor=navy,
                              leading=20, spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("b", fontName=reg, fontSize=10.5, textColor=gray,
                                leading=16, alignment=TA_LEFT)
    cell_style = ParagraphStyle("c", fontName=reg, fontSize=9.5, textColor=gray, leading=13)
    cellh_style = ParagraphStyle("ch", fontName=bold, fontSize=9.5,
                                 textColor=colors.white, leading=13)

    page_w, page_h = A4

    def _on_page(canvas, _doc):
        canvas.saveState()
        canvas.setFillColor(navy)
        canvas.rect(0, page_h - 14 * mm, page_w, 14 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(bold, 11)
        canvas.drawString(15 * mm, page_h - 9.5 * mm, f"VVS · {spec.level}")
        canvas.setFont(reg, 9)
        canvas.drawRightString(page_w - 15 * mm, page_h - 9.5 * mm,
                               spec.title or doc_model.title)
        canvas.setFillColor(gray)
        canvas.setFont(reg, 8)
        canvas.drawCentredString(page_w / 2, 10 * mm, f"- {canvas.getPageNumber()} -")
        canvas.restoreState()

    flow: list = []
    flow.append(Spacer(1, 30 * mm))
    flow.append(Paragraph(doc_model.title or spec.title or "VVS", title_style))
    for line in doc_model.subtitle_lines:
        flow.append(Paragraph(line, sub_style))
    flow.append(Spacer(1, 8 * mm))

    avail_w = page_w - 30 * mm
    for sec in doc_model.sections:
        if sec.heading:
            flow.append(Paragraph(sec.heading, h2_style))
        for el in sec.elements:
            if el.kind == "para":
                flow.append(Paragraph(el.text.replace("\n", "<br/>"), body_style))
            elif el.kind == "bullets":
                items = [ListItem(Paragraph(x, body_style), leftIndent=6) for x in el.items]
                flow.append(ListFlowable(items, bulletType="bullet",
                                         bulletColor=accent, start="•"))
            elif el.kind == "table" and el.rows:
                ncols = max(len(r) for r in el.rows)
                col_w = avail_w / ncols
                data = []
                for ri, r in enumerate(el.rows):
                    r = r + [""] * (ncols - len(r))
                    sty = cellh_style if ri == 0 else cell_style
                    data.append([Paragraph(c, sty) for c in r])
                t = Table(data, colWidths=[col_w] * ncols, hAlign="LEFT")
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), accent),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light]),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.Color(0.8, 0.83, 0.88)),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                flow.append(Spacer(1, 2 * mm))
                flow.append(t)
                flow.append(Spacer(1, 3 * mm))

    pdfdoc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=20 * mm, bottomMargin=16 * mm,
        title=spec.title or doc_model.title,
    )
    page_count = {"n": 0}

    def _count(canvas, d):
        page_count["n"] += 1
        _on_page(canvas, d)

    pdfdoc.build(flow, onFirstPage=_count, onLaterPages=_count)
    return RenderResult(
        path=str(out_path), fmt="pdf", level=spec.level,
        slide_count=page_count["n"], title=spec.title or doc_model.title,
        bytes=out_path.stat().st_size, **metrics,
    )


# ════════════════════════════════════════════════════════════════════
# PPTX 렌더 (python-pptx, 한글 폰트명 + 네이티브 표)
# ════════════════════════════════════════════════════════════════════
def render_pptx(spec: RenderSpec, out_path: str | Path) -> RenderResult:
    if not pptx_available():
        raise RendererUnavailable("python-pptx not installed")
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Inches, Pt

    doc_model = parse_markdown(spec.text)
    metrics = _metrics(doc_model)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    navy = RGBColor(*BRAND_NAVY)
    accent = RGBColor(*BRAND_ACCENT)
    gray = RGBColor(*BRAND_GRAY)
    light = RGBColor(*BRAND_LIGHT)
    FONT = fonts.FONT_REGULAR

    def _font(run, size, color, bold=False):
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.bold = bold
        run.font.name = FONT

    # 표지
    cover = prs.slides.add_slide(blank)
    band = cover.shapes.add_shape(1, Inches(0), Inches(2.4), Inches(13.333), Inches(2.6))
    band.fill.solid(); band.fill.fore_color.rgb = navy; band.line.fill.background()
    tb = cover.shapes.add_textbox(Inches(0.9), Inches(2.7), Inches(11.5), Inches(2.0))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = doc_model.title or spec.title or "VVS"
    _font(r, 40, RGBColor(255, 255, 255), bold=True)
    for line in doc_model.subtitle_lines:
        p = tf.add_paragraph(); rr = p.add_run(); rr.text = line
        _font(rr, 16, RGBColor(0xCF, 0xDA, 0xEC))

    def _content_slide(heading):
        slide = prs.slides.add_slide(blank)
        bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.22), Inches(7.5))
        bar.fill.solid(); bar.fill.fore_color.rgb = accent; bar.line.fill.background()
        htb = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.2), Inches(0.9))
        hr = htb.text_frame.paragraphs[0].add_run()
        hr.text = heading or spec.title
        _font(hr, 26, navy, bold=True)
        ln = slide.shapes.add_shape(1, Inches(0.65), Inches(1.25), Inches(3.2), Inches(0.04))
        ln.fill.solid(); ln.fill.fore_color.rgb = accent; ln.line.fill.background()
        return slide

    def _add_table(slide, rows, top):
        nrows = len(rows); ncols = max(len(r) for r in rows)
        gt = slide.shapes.add_table(nrows, ncols, Inches(0.65), Inches(top),
                                    Inches(12.0), Inches(0.4 * nrows)).table
        for ci in range(ncols):
            gt.columns[ci].width = Inches(12.0 / ncols)
        for ri, row in enumerate(rows):
            row = row + [""] * (ncols - len(row))
            for ci, val in enumerate(row):
                cell = gt.cell(ri, ci)
                cell.fill.solid()
                cell.fill.fore_color.rgb = accent if ri == 0 else (
                    light if ri % 2 == 0 else RGBColor(255, 255, 255))
                tfc = cell.text_frame; tfc.word_wrap = True
                rr = tfc.paragraphs[0].add_run(); rr.text = val
                _font(rr, 11, RGBColor(255, 255, 255) if ri == 0 else gray, bold=(ri == 0))

    for sec in doc_model.sections:
        slide = _content_slide(sec.heading)
        top = 1.6
        body_tb = None
        for el in sec.elements:
            if el.kind == "table" and el.rows:
                _add_table(slide, el.rows, top)
                top += 0.42 * len(el.rows) + 0.3
            elif el.kind in ("bullets", "para"):
                if body_tb is None:
                    body_tb = slide.shapes.add_textbox(
                        Inches(0.7), Inches(top), Inches(12.0), Inches(5.0))
                    body_tb.text_frame.word_wrap = True
                tf2 = body_tb.text_frame
                lines = el.items if el.kind == "bullets" else el.text.splitlines()
                for it in lines:
                    p = tf2.add_paragraph(); rr = p.add_run()
                    rr.text = (f"•  {it}" if el.kind == "bullets" else it)
                    _font(rr, 15, gray)
                top += 0.4 * (len(lines) + 1)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    return RenderResult(
        path=str(out_path), fmt="pptx", level=spec.level,
        slide_count=len(prs.slides._sldIdLst),
        title=spec.title or doc_model.title,
        bytes=out_path.stat().st_size, **metrics,
    )


def render(spec: RenderSpec, out_path: str | Path, fmt: str) -> RenderResult:
    fmt = fmt.lower()
    if fmt == "pptx":
        return render_pptx(spec, out_path)
    if fmt == "pdf":
        return render_pdf(spec, out_path)
    raise ValueError(f"unsupported fmt: {fmt!r}")
