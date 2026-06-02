"""ai_pm/visual_enhance.py — ③ 이미지 기반 브랜딩 고도화 (B-3 빈껍데기 해결).

게이트를 통과한 텍스트(사실 보존) → 디자인 시스템 15.2 SVG 페이지 → 고해상도
PNG → PDF. 확산모델을 쓰지 않으므로 텍스트/숫자가 그대로 보존된다.

B-3 의 빈약함을 해결: 단순 표 나열이 아니라 디자인 시스템(Burning Orange·
Industrial Editorial)을 적용한 표지/섹션 카드/표를 SVG 로 구성한다.

입력은 document_renderer.parse_markdown 의 Document(게이트 통과 텍스트). 즉
②(작성)→게이트→③(고도화) 순서로 사실이 보존된다.
"""

from __future__ import annotations

from pathlib import Path

from . import design_system as ds
from . import document_renderer as dr
from . import svg_render as sr

PAGE_W = 1240          # A4 비율 @150dpi 근사
PAGE_H = 1754
M = 90                 # 페이지 마진(px)


def _wrap(text: str, max_chars: int) -> list:
    """간이 줄바꿈(한글 폭 근사). 단어/공백 단위."""
    out, cur = [], ""
    for token in str(text).split(" "):
        if len(cur) + len(token) + 1 > max_chars:
            if cur:
                out.append(cur)
            cur = token
        else:
            cur = (cur + " " + token).strip()
    if cur:
        out.append(cur)
    return out or [""]


def _cover_svg(doc: dr.Document, level: str) -> str:
    sub = doc.subtitle_lines
    subs = "".join(
        f'<text x="{M}" y="{640 + i*46}" font-family="{ds.FONT_KR}" font-size="24" '
        f'fill="{ds.rgb_hex(ds.GRAY)}">{sr.esc(s)}</text>'
        for i, s in enumerate(sub[:4])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{PAGE_H}">
  <rect width="{PAGE_W}" height="{PAGE_H}" fill="{ds.rgb_hex(ds.PAPER)}"/>
  <rect x="0" y="0" width="{PAGE_W}" height="18" fill="{ds.rgb_hex(ds.ORANGE)}"/>
  <rect x="0" y="430" width="{ds.BAR_WIDTH*16}" height="14" fill="{ds.rgb_hex(ds.ORANGE)}"/>
  <text x="{M}" y="380" font-family="{ds.FONT_KR}" font-size="20"
        fill="{ds.rgb_hex(ds.ORANGE_DEEP)}" letter-spacing="3">VVS · {sr.esc(level)}</text>
  <text x="{M}" y="500" font-family="{ds.FONT_KR}" font-size="66" font-weight="bold"
        fill="{ds.rgb_hex(ds.NAVY)}">{sr.esc(doc.title or "회사소개서")}</text>
  {subs}
  <text x="{M}" y="{PAGE_H-80}" font-family="{ds.FONT_KR}" font-size="16"
        fill="{ds.rgb_hex(ds.GRAY)}">{ds.NAME} · {ds.STYLE}</text>
</svg>'''


def _section_svgs(doc: dr.Document) -> list:
    """섹션별 SVG 페이지 리스트 (카드·표·불릿)."""
    pages = []
    for sec in doc.sections:
        body = []
        y = 300
        for el in sec.elements:
            if el.kind == "table" and el.rows:
                ncols = max(len(r) for r in el.rows)
                colw = (PAGE_W - 2*M) / ncols
                for ri, row in enumerate(el.rows):
                    row = row + [""] * (ncols - len(row))
                    rh = 56
                    fill = (ds.rgb_hex(ds.ORANGE) if ri == 0
                            else (ds.rgb_hex(ds.GRAY_LIGHT) if ri % 2 == 0
                                  else ds.rgb_hex(ds.PAPER)))
                    body.append(f'<rect x="{M}" y="{y}" width="{PAGE_W-2*M}" height="{rh}" '
                                f'fill="{fill}" stroke="{ds.rgb_hex(ds.LINE)}"/>')
                    for ci, cell in enumerate(row):
                        tx = M + ci*colw + 14
                        tc = ("white" if ri == 0 else ds.rgb_hex(ds.INK))
                        fw = "bold" if ri == 0 else "normal"
                        body.append(
                            f'<text x="{tx}" y="{y+36}" font-family="{ds.FONT_KR}" '
                            f'font-size="18" fill="{tc}" font-weight="{fw}">'
                            f'{sr.esc(cell[:38])}</text>')
                    y += rh
                y += 24
            elif el.kind == "bullets":
                for it in el.items:
                    for ln in _wrap(it, 52):
                        body.append(
                            f'<circle cx="{M+8}" cy="{y-6}" r="4" fill="{ds.rgb_hex(ds.ORANGE)}"/>'
                            f'<text x="{M+28}" y="{y}" font-family="{ds.FONT_KR}" '
                            f'font-size="19" fill="{ds.rgb_hex(ds.GRAY)}">{sr.esc(ln)}</text>')
                        y += 36
                y += 16
            elif el.kind == "para":
                for raw in el.text.splitlines():
                    for ln in _wrap(raw, 56):
                        body.append(
                            f'<text x="{M}" y="{y}" font-family="{ds.FONT_KR}" '
                            f'font-size="19" fill="{ds.rgb_hex(ds.GRAY)}">{sr.esc(ln)}</text>')
                        y += 34
                y += 16
            if y > PAGE_H - 140:
                break  # 페이지 넘침 방지(간이)

        heading = sec.heading or ""
        page = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{PAGE_H}">
  <rect width="{PAGE_W}" height="{PAGE_H}" fill="{ds.rgb_hex(ds.PAPER)}"/>
  <rect x="0" y="0" width="{PAGE_W}" height="120" fill="{ds.rgb_hex(ds.NAVY)}"/>
  <rect x="0" y="120" width="{PAGE_W}" height="6" fill="{ds.rgb_hex(ds.ORANGE)}"/>
  <text x="{M}" y="76" font-family="{ds.FONT_KR}" font-size="30" font-weight="bold"
        fill="white">{sr.esc(heading)}</text>
  <text x="{PAGE_W-M}" y="76" text-anchor="end" font-family="{ds.FONT_KR}" font-size="16"
        fill="{ds.rgb_hex(ds.ORANGE)}">VVS</text>
  {''.join(body)}
</svg>'''
        pages.append(page)
    return pages


def enhance_to_png_pages(text: str, out_dir: str | Path, *, level: str = "L1") -> dict:
    """게이트 통과 텍스트 → 디자인 15.2 SVG → 고해상도 PNG 페이지들.

    반환: {"pages": [png경로...], "page_count": n, "design": ds.NAME}
    """
    if not sr.available():
        raise sr.SvgRenderUnavailable("cairosvg required")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = dr.parse_markdown(text)

    svgs = [_cover_svg(doc, level)] + _section_svgs(doc)
    pages = []
    for i, svg in enumerate(svgs):
        p = out_dir / f"page_{i+1:02d}.png"
        sr.render_svg_to_png(svg, p, width=PAGE_W)
        pages.append(str(p))
    return {"pages": pages, "page_count": len(pages), "design": ds.NAME,
            "style": ds.STYLE}


def png_pages_to_pdf(pages: list, out_pdf: str | Path) -> str:
    """PNG 페이지들을 하나의 PDF 로 합본 (reportlab).

    Pillow PDF 저장은 RGB 를 JPEG 로 인코딩하려 해서 일부 빌드(JPEG 미지원)에서
    KeyError 로 실패한다. reportlab 캔버스에 PNG 를 그대로 얹어 합본하면
    무손실·안정적이다.
    """
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    if not pages:
        raise ValueError("no pages")
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_pdf), pagesize=(PAGE_W, PAGE_H))
    for p in pages:
        c.drawImage(ImageReader(str(p)), 0, 0, width=PAGE_W, height=PAGE_H)
        c.showPage()
    c.save()
    return str(out_pdf)


def enhance_to_pdf(text: str, out_dir: str | Path, *, level: str = "L1",
                   pdf_name: str = "enhanced.pdf") -> dict:
    """텍스트 → SVG 디자인 페이지 → PNG → PDF 합본 (원샷)."""
    res = enhance_to_png_pages(text, out_dir, level=level)
    pdf = png_pages_to_pdf(res["pages"], Path(out_dir) / pdf_name)
    res["pdf"] = pdf
    return res
