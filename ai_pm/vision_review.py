"""ai_pm/vision_review.py — 렌더 산출물 디자인 검수 (점수 산출).

렌더된 PDF/PPTX 의 디자인 품질을 4기준(가독성·정렬·여백·브랜딩, 각 25점)으로
채점한다. B-4 학습에서 rubric 의 visual 항목으로 연결된다.

두 경로:
  1. 결정론 휴리스틱 (기본, 테스트 가능): 렌더 메타(슬라이드 수·텍스트 밀도·
     브랜딩 적용)로 점수를 산출한다. 네트워크/모델 불필요.
  2. 실제 비전 (선택, B-4): 헤르메스 tools/vision_tools.vision_analyze_tool 를
     주입(vision_fn)하면 썸네일을 모델로 분석한다. 미주입 시 휴리스틱만 사용.

헤르메스를 직접 수정하지 않는다 — vision_fn 을 주입받는 구조.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# 디자인 채점 기준 (각 25점, 합 100)
DESIGN_RUBRIC: dict[str, int] = {
    "readability": 25,   # 가독성 (슬라이드당 텍스트 밀도 적정)
    "alignment": 25,     # 정렬 (액센트 바/일관 레이아웃)
    "whitespace": 25,    # 여백 (과밀/과소 회피)
    "branding": 25,      # 브랜딩 (VVS 팔레트/레벨 표기)
}

PASS_THRESHOLD = 70

# 슬라이드당 적정 문자 수(가독성·여백 휴리스틱 기준)
_MIN_CHARS_PER_SLIDE = 20
_MAX_CHARS_PER_SLIDE = 1200
_IDEAL_CHARS_PER_SLIDE = 400


@dataclass
class DesignReview:
    total: int
    breakdown: dict
    passed: bool
    notes: list = field(default_factory=list)
    vision_used: bool = False


def _score_readability(render, text: str) -> int:
    slides = max(1, getattr(render, "slide_count", 1))
    per = len(text or "") / slides
    if per < _MIN_CHARS_PER_SLIDE:
        return round(DESIGN_RUBRIC["readability"] * 0.4)  # 너무 비어 가독성↓
    if per > _MAX_CHARS_PER_SLIDE:
        return round(DESIGN_RUBRIC["readability"] * 0.5)  # 과밀
    # 이상치에 가까울수록 만점
    dist = abs(per - _IDEAL_CHARS_PER_SLIDE) / _IDEAL_CHARS_PER_SLIDE
    factor = max(0.6, 1.0 - min(dist, 1.0) * 0.4)
    return round(DESIGN_RUBRIC["readability"] * factor)


def _score_alignment(render) -> int:
    # 렌더러가 일관 레이아웃(액센트 바·고정 마진)을 보장 → 만점 기준.
    # 슬라이드/페이지가 1개뿐이면 정렬 평가 근거 약함 → 소폭 감점.
    slides = getattr(render, "slide_count", 1)
    return DESIGN_RUBRIC["alignment"] if slides >= 2 else round(DESIGN_RUBRIC["alignment"] * 0.8)


def _score_whitespace(render, text: str) -> int:
    slides = max(1, getattr(render, "slide_count", 1))
    per = len(text or "") / slides
    if per > _MAX_CHARS_PER_SLIDE:
        return round(DESIGN_RUBRIC["whitespace"] * 0.4)  # 여백 부족
    if per < _MIN_CHARS_PER_SLIDE:
        return round(DESIGN_RUBRIC["whitespace"] * 0.7)  # 과한 여백
    return DESIGN_RUBRIC["whitespace"]


def _score_branding(render) -> int:
    # 렌더 결과에 레벨 표기 + VVS 브랜드 바 적용됨(렌더러 보장).
    # 메타에 title/level 이 있으면 브랜딩 충족.
    has_title = bool(getattr(render, "title", ""))
    has_level = bool(getattr(render, "level", ""))
    score = DESIGN_RUBRIC["branding"]
    if not has_title:
        score -= 12
    if not has_level:
        score -= 13
    return max(0, score)


def review_design(render, *, text: str = "", vision_fn=None) -> DesignReview:
    """렌더 산출물을 디자인 채점한다.

    render:    document_renderer.RenderResult (slide_count/title/level/...)
    text:      원본 본문 (가독성·여백 휴리스틱용)
    vision_fn: 선택. callable(render) -> dict{breakdown 보정/notes} (B-4 연결).

    반환: DesignReview(total, breakdown, passed, notes, vision_used)
    """
    text = text or getattr(render, "text", "") or ""
    breakdown = {
        "readability": _score_readability(render, text),
        "alignment": _score_alignment(render),
        "whitespace": _score_whitespace(render, text),
        "branding": _score_branding(render),
    }
    notes: list = []
    vision_used = False

    # 선택: 실제 비전 분석 주입 시 보정 (헤르메스 vision_analyze 등)
    if vision_fn is not None:
        try:
            adj = vision_fn(render) or {}
            for k, v in (adj.get("breakdown") or {}).items():
                if k in breakdown:
                    breakdown[k] = max(0, min(DESIGN_RUBRIC[k], int(v)))
            notes.extend(adj.get("notes") or [])
            vision_used = True
        except Exception as exc:  # 비전 실패는 휴리스틱으로 우아 강등
            notes.append(f"vision_fn failed, heuristic only: {exc}")

    total = sum(breakdown.values())
    if total < PASS_THRESHOLD:
        notes.append(f"design score {total} < {PASS_THRESHOLD} (개선 필요)")
    return DesignReview(
        total=total,
        breakdown=breakdown,
        passed=total >= PASS_THRESHOLD,
        notes=notes,
        vision_used=vision_used,
    )
