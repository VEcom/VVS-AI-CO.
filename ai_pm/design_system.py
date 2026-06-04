"""ai_pm/design_system.py — 디자인 시스템 15.2 (Burning Orange · Industrial Editorial).

브랜딩 고도화의 시각 토큰. ③ 이미지 고도화(SVG/HTML→PNG)와 렌더러가 공유한다.
확산모델을 쓰지 않으므로 모든 색/타이포/간격은 결정론 토큰이다.

핵심 팔레트:
  - Burning Orange (강조/액션)
  - Industrial Navy/Ink (본문/헤더)
  - Editorial 그레이 스케일 (배경/표)
한글 폰트: NanumGothic(보존) — Pretendard/Noto 가용 시 우선.
"""

from __future__ import annotations

# ── 색 (RGB) ──
ORANGE = (0xFF, 0x5A, 0x1F)        # Burning Orange (primary accent)
ORANGE_DEEP = (0xD9, 0x45, 0x10)
NAVY = (0x1A, 0x22, 0x33)          # Industrial Ink (헤더/본문 강조)
INK = (0x23, 0x2A, 0x36)
GRAY = (0x55, 0x5A, 0x66)          # 본문
GRAY_LIGHT = (0xE9, 0xEC, 0xF1)    # 표 교차배경
PAPER = (0xFB, 0xFA, 0xF7)         # Editorial 따뜻한 화이트
LINE = (0xCE, 0xD4, 0xDE)          # 테두리

# ── 타이포 ──
FONT_KR = "NanumGothic"            # 한글 (assets/fonts 보존)
FONT_KR_BOLD = "NanumGothic-Bold"
HEAD_SIZE = 30
H2_SIZE = 17
BODY_SIZE = 11
CAPTION_SIZE = 8.5
LINE_HEIGHT = 1.5
LETTER_SPACING = 0.2               # 자간(em 비율 근사)

# ── 간격 (mm/px 공용 스케일) ──
MARGIN = 15
GUTTER = 8
BAR_WIDTH = 6                       # 좌측 액센트 바


def rgb_hex(c: tuple) -> str:
    return "#%02X%02X%02X" % c


# 디자인 시스템 식별 (채점·검수용)
NAME = "VVS Design System 15.2"
STYLE = "Burning Orange · Industrial Editorial"


def tokens() -> dict:
    """디자인 토큰 딕셔너리 (Gemini 프롬프트·검수에 주입)."""
    return {
        "name": NAME,
        "style": STYLE,
        "palette": {
            "orange": rgb_hex(ORANGE),
            "orange_deep": rgb_hex(ORANGE_DEEP),
            "navy": rgb_hex(NAVY),
            "ink": rgb_hex(INK),
            "gray": rgb_hex(GRAY),
            "gray_light": rgb_hex(GRAY_LIGHT),
            "paper": rgb_hex(PAPER),
            "line": rgb_hex(LINE),
        },
        "type": {
            "font_kr": FONT_KR,
            "head": HEAD_SIZE,
            "h2": H2_SIZE,
            "body": BODY_SIZE,
            "line_height": LINE_HEIGHT,
            "letter_spacing": LETTER_SPACING,
        },
        "spacing": {"margin": MARGIN, "gutter": GUTTER, "bar": BAR_WIDTH},
    }
