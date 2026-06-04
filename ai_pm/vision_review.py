"""ai_pm/vision_review.py — 렌더 산출물 디자인+내용 검수 (점수 산출).

렌더된 PDF/PPTX 의 품질을 4기준(가독성·정렬·여백·브랜딩, 각 25점)으로 채점한다.
**내용 품질**을 반영한다: 빈 페이지/뼈대만 있는 산출물은 저점을 받는다(과거
빈 문서가 91점을 받던 오류 수정). 채점은 renderer 가 노출하는 콘텐츠 메트릭
(섹션·표·행·불릿·정보량)에 기반한다.

두 경로:
  1. 결정론 휴리스틱 (기본, 테스트 가능): 콘텐츠 메트릭으로 점수 산출.
  2. 실제 비전 (선택, B-4): vision_fn 주입 시 썸네일 모델 분석으로 보정.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DESIGN_RUBRIC: dict[str, int] = {
    "readability": 25,
    "alignment": 25,
    "whitespace": 25,
    "branding": 25,
}

PASS_THRESHOLD = 70

_MIN_SECTIONS = 3
_GOOD_SECTIONS = 6
_MIN_CONTENT_CHARS = 250
_GOOD_CONTENT_CHARS = 900
_IDEAL_CHARS_PER_PAGE = 700
_MAX_CHARS_PER_PAGE = 2200


@dataclass
class DesignReview:
    total: int
    breakdown: dict
    passed: bool
    notes: list = field(default_factory=list)
    vision_used: bool = False
    metrics: dict = field(default_factory=dict)


def _m(render, key, default=0):
    return getattr(render, key, default) or default


def _content_richness(render) -> float:
    sections = _m(render, "section_count")
    chars = _m(render, "content_chars")
    structure = _m(render, "table_rows") + _m(render, "bullet_count")
    sec_f = min(1.0, sections / _GOOD_SECTIONS) if sections else 0.0
    char_f = min(1.0, chars / _GOOD_CONTENT_CHARS) if chars else 0.0
    str_f = min(1.0, structure / 12.0)
    return 0.4 * char_f + 0.35 * sec_f + 0.25 * str_f


def _score_readability(render) -> int:
    sections = _m(render, "section_count")
    chars = _m(render, "content_chars")
    if chars < _MIN_CONTENT_CHARS or sections < _MIN_SECTIONS:
        base = 0.25
    else:
        base = 0.6 + 0.4 * _content_richness(render)
    return round(DESIGN_RUBRIC["readability"] * min(1.0, base))


def _score_alignment(render) -> int:
    sections = _m(render, "section_count")
    structured = _m(render, "table_count") + (1 if _m(render, "bullet_count") else 0)
    if sections < _MIN_SECTIONS:
        return round(DESIGN_RUBRIC["alignment"] * 0.3)
    factor = 0.6 + 0.4 * min(1.0, structured / 4.0)
    return round(DESIGN_RUBRIC["alignment"] * factor)


def _score_whitespace(render) -> int:
    pages = max(1, _m(render, "slide_count", 1))
    chars = _m(render, "content_chars")
    if chars < _MIN_CONTENT_CHARS:
        return round(DESIGN_RUBRIC["whitespace"] * 0.3)
    per = chars / pages
    if per > _MAX_CHARS_PER_PAGE:
        return round(DESIGN_RUBRIC["whitespace"] * 0.55)
    dist = abs(per - _IDEAL_CHARS_PER_PAGE) / _IDEAL_CHARS_PER_PAGE
    factor = max(0.6, 1.0 - min(dist, 1.0) * 0.4)
    return round(DESIGN_RUBRIC["whitespace"] * factor)


def _score_branding(render) -> int:
    score = DESIGN_RUBRIC["branding"]
    if not _m(render, "title", ""):
        score -= 10
    if not getattr(render, "level", ""):
        score -= 8
    if _m(render, "section_count") < _MIN_SECTIONS:
        score -= 7
    return max(0, score)


def review_design(render, *, text: str = "", vision_fn=None) -> DesignReview:
    """렌더 산출물을 디자인+내용 채점."""
    breakdown = {
        "readability": _score_readability(render),
        "alignment": _score_alignment(render),
        "whitespace": _score_whitespace(render),
        "branding": _score_branding(render),
    }
    notes: list = []
    vision_used = False

    if vision_fn is not None:
        try:
            adj = vision_fn(render) or {}
            for k, v in (adj.get("breakdown") or {}).items():
                if k in breakdown:
                    breakdown[k] = max(0, min(DESIGN_RUBRIC[k], int(v)))
            notes.extend(adj.get("notes") or [])
            vision_used = True
        except Exception as exc:
            notes.append(f"vision_fn failed, heuristic only: {exc}")

    metrics = {
        "section_count": _m(render, "section_count"),
        "table_count": _m(render, "table_count"),
        "table_rows": _m(render, "table_rows"),
        "bullet_count": _m(render, "bullet_count"),
        "content_chars": _m(render, "content_chars"),
        "pages": _m(render, "slide_count", 1),
    }
    total = sum(breakdown.values())
    if metrics["content_chars"] < _MIN_CONTENT_CHARS:
        notes.append("내용 빈약(빈 페이지/뼈대) — 콘텐츠 보강 필요")
    if total < PASS_THRESHOLD:
        notes.append(f"품질 점수 {total} < {PASS_THRESHOLD} (개선 필요)")
    return DesignReview(
        total=total, breakdown=breakdown, passed=total >= PASS_THRESHOLD,
        notes=notes, vision_used=vision_used, metrics=metrics,
    )
