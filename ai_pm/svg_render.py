"""ai_pm/svg_render.py — SVG → 고해상도 PNG (확산모델 금지, 순수 벡터).

cairosvg 로 SVG 문자열/HTML을 PNG 로 래스터화한다. 확산모델(생성형 이미지)을
일절 쓰지 않으므로 텍스트/숫자 사실이 보존된다(환각 없음).

라이브러리 부재 시 SvgRenderUnavailable. PIL 로 워터마크/검증 보조.
"""

from __future__ import annotations

import html
import importlib.util
from pathlib import Path


class SvgRenderUnavailable(RuntimeError):
    """cairosvg 미설치."""


def available() -> bool:
    return importlib.util.find_spec("cairosvg") is not None


def render_svg_to_png(svg: str, out_path: str | Path, *, width: int = 1600,
                      height: int | None = None) -> str:
    """SVG 문자열을 PNG 로 렌더. 확산모델 미사용(벡터 래스터화만)."""
    if not available():
        raise SvgRenderUnavailable("cairosvg not installed")
    import cairosvg

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"bytestring": svg.encode("utf-8"), "write_to": str(out_path),
              "output_width": width}
    if height:
        kwargs["output_height"] = height
    cairosvg.svg2png(**kwargs)
    return str(out_path)


def esc(s) -> str:
    """SVG/XML 텍스트 이스케이프."""
    return html.escape(str(s), quote=True)
