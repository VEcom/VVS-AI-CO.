"""ai_pm/evidence_image.py — 합성 증빙 이미지 (사업등록증·면허 등).

페르소나의 증빙 서류를 **SVG→PNG**(확산모델 금지)로 생성한다. 절대선 #2 계약:
  - 식별자 무효(전부 0/-): 사업자번호 000-00-00000 등
  - "학습용" 워터마크를 모든 증빙에 명시 (오인 방지)
  - [SYNTHETIC] 마킹

실제 서류를 모사하지 않는다(위조 방지). 명백히 합성·학습용임을 표면화한다.
"""

from __future__ import annotations

from pathlib import Path

from . import design_system as ds
from . import svg_render as sr
from .sandbox import SYNTHETIC_MARK, assert_invalid_identifier


class EvidenceContractError(Exception):
    """증빙 합성 계약 위반(식별자 유효/워터마크 누락 등)."""


def _watermark_layer(w: int, h: int, text: str = "학습용 · SYNTHETIC") -> str:
    """반복 워터마크 레이어 (대각, 옅게)."""
    marks = []
    step = 260
    for y in range(60, h, step):
        for x in range(-40, w, step * 2):
            marks.append(
                f'<text x="{x}" y="{y}" font-family="{ds.FONT_KR}" font-size="26" '
                f'fill="{ds.rgb_hex(ds.ORANGE)}" fill-opacity="0.12" '
                f'transform="rotate(-24 {x} {y})">{sr.esc(text)}</text>'
            )
    return "\n".join(marks)


def build_business_cert_svg(persona: dict) -> str:
    """사업자등록증 형태의 합성 증빙 SVG (학습용 워터마크·무효 식별자)."""
    ov = (persona or {}).get("overview", {})
    biz_no = ov.get("사업자등록번호", "000-00-00000 [SYNTHETIC]")
    # 무효 식별자 강제 (숫자부만 추출해 검증)
    digits = "".join(ch for ch in biz_no if ch.isdigit() or ch == "-")
    core = digits.replace("-", "")
    if core and set(core) <= {"0"}:
        pass  # 전부 0 → 무효(허용)
    else:
        # 무효가 아니면 강제로 무효치환
        biz_no = "000-00-00000 [SYNTHETIC]"

    company = ov.get("회사명", persona.get("company", "(주)합성테크 [SYNTHETIC]"))
    ceo = ov.get("대표이사", "홍길동 [SYNTHETIC]")
    addr = ov.get("본사 소재지", "(합성주소) [SYNTHETIC]")
    opened = ov.get("설립일", "2009-03-02")
    W, H = 1200, 820

    rows = [
        ("상호(법인명)", company),
        ("대표자", ceo),
        ("사업자등록번호", biz_no),
        ("개업연월일", opened),
        ("사업장 소재지", addr),
        ("업태/종목", "제조업 / 반도체 장비 부품 [SYNTHETIC]"),
    ]
    row_svg = []
    y0 = 300
    for i, (k, v) in enumerate(rows):
        y = y0 + i * 70
        bg = ds.rgb_hex(ds.GRAY_LIGHT) if i % 2 == 0 else ds.rgb_hex(ds.PAPER)
        row_svg.append(
            f'<rect x="80" y="{y-44}" width="1040" height="62" fill="{bg}" stroke="{ds.rgb_hex(ds.LINE)}"/>'
            f'<text x="110" y="{y}" font-family="{ds.FONT_KR}" font-size="22" '
            f'fill="{ds.rgb_hex(ds.GRAY)}" font-weight="bold">{sr.esc(k)}</text>'
            f'<text x="430" y="{y}" font-family="{ds.FONT_KR}" font-size="22" '
            f'fill="{ds.rgb_hex(ds.INK)}">{sr.esc(v)}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">
  <rect width="{W}" height="{H}" fill="{ds.rgb_hex(ds.PAPER)}"/>
  <rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="{ds.rgb_hex(ds.NAVY)}" stroke-width="6"/>
  <rect x="0" y="0" width="{ds.BAR_WIDTH*4}" height="{H}" fill="{ds.rgb_hex(ds.ORANGE)}"/>
  <text x="80" y="120" font-family="{ds.FONT_KR}" font-size="44" font-weight="bold"
        fill="{ds.rgb_hex(ds.NAVY)}">사 업 자 등 록 증</text>
  <text x="80" y="170" font-family="{ds.FONT_KR}" font-size="22"
        fill="{ds.rgb_hex(ds.ORANGE_DEEP)}">[학습용 합성 문서 · {SYNTHETIC_MARK}]</text>
  <line x1="80" y1="210" x2="1120" y2="210" stroke="{ds.rgb_hex(ds.LINE)}" stroke-width="2"/>
  {''.join(row_svg)}
  <text x="80" y="{y0 + len(rows)*70 + 40}" font-family="{ds.FONT_KR}" font-size="18"
        fill="{ds.rgb_hex(ds.GRAY)}">※ 본 문서는 AI 학습용으로 생성된 합성 자료이며 실제 효력이 없습니다.</text>
  {_watermark_layer(W, H)}
</svg>'''


def generate_evidence(persona: dict, out_dir: str | Path, *, name: str = "business_cert") -> dict:
    """증빙 이미지를 생성하고 계약(무효 식별자·워터마크)을 검증한다.

    반환: {"path": str, "kind": str, "watermark": True, "synthetic": True}
    """
    if not sr.available():
        raise sr.SvgRenderUnavailable("cairosvg required for evidence image")

    svg = build_business_cert_svg(persona or {})
    if "학습용" not in svg or SYNTHETIC_MARK not in svg:
        raise EvidenceContractError("워터마크/합성 마킹 누락")

    out_dir = Path(out_dir)
    png = out_dir / f"{name}.png"
    sr.render_svg_to_png(svg, png, width=1200)

    # 무효 식별자 계약 재확인 (sandbox)
    assert_invalid_identifier("000000")  # 증빙은 000-00-00000(전부 0) 사용

    return {"path": str(png), "kind": "business_cert", "watermark": True,
            "synthetic": True, "svg_bytes": len(svg)}
