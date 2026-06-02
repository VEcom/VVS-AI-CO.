"""ai_pm/fonts.py — 한글 폰트 등록/해상 헬퍼.

PDF(reportlab)·이미지(PIL) 렌더에서 한글이 깨지지 않도록(■■■ 방지) NanumGothic
폰트를 등록한다. 폰트는 repo 의 assets/fonts/ 에 보존되어 ephemeral 컨테이너
에서도 재현된다(네트워크 불필요).

NanumGothic 은 SIL Open Font License(OFL) 로 재배포 가능하다.
PPTX 는 텍스트를 유니코드로 저장하므로 폰트명만 지정하면 뷰어가 렌더한다.
PDF(reportlab)는 기본 Helvetica 가 한글을 ■■■ 로 표시하므로 TTF 등록이 필수다.
"""

from __future__ import annotations

from pathlib import Path

_ASSETS = Path(__file__).resolve().parents[1] / "assets" / "fonts"
REGULAR_PATH = _ASSETS / "NanumGothic.ttf"
BOLD_PATH = _ASSETS / "NanumGothicBold.ttf"

FONT_REGULAR = "NanumGothic"
FONT_BOLD = "NanumGothic-Bold"

_registered = False


class KoreanFontUnavailable(RuntimeError):
    """한글 폰트 파일 부재."""


def fonts_available() -> bool:
    return REGULAR_PATH.exists() and BOLD_PATH.exists()


def font_path(bold: bool = False) -> str:
    """폰트 TTF 절대경로. 부재 시 KoreanFontUnavailable."""
    p = BOLD_PATH if bold else REGULAR_PATH
    if not p.exists():
        raise KoreanFontUnavailable(f"Korean font missing: {p}")
    return str(p)


def register_reportlab() -> tuple[str, str]:
    """reportlab 에 한글 폰트를 등록한다.

    반환: (regular_name, bold_name). 폰트 부재 시 KoreanFontUnavailable.
    """
    global _registered
    if not fonts_available():
        raise KoreanFontUnavailable(
            f"Korean fonts not found under {_ASSETS}. run scripts/setup_fonts.sh"
        )
    if not _registered:
        from reportlab.lib.fonts import addMapping
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(REGULAR_PATH)))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(BOLD_PATH)))
        addMapping(FONT_REGULAR, 0, 0, FONT_REGULAR)
        addMapping(FONT_REGULAR, 1, 0, FONT_BOLD)
        _registered = True
    return FONT_REGULAR, FONT_BOLD
