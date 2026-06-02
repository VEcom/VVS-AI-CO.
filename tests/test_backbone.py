"""백본 배치 + 작성≠채점 계열분리 검증 (조직도 v4).

실 API 호출 없이(키 불필요) 배치·계열분리 로직을 검증한다. 라이브 호출
스모크는 scripts/backbone_smoke.py 로 별도 수행(키 필요).
"""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

from ai_pm import backbone as bb  # noqa: E402


# ── 조직도 v4 배치 ──
def test_aipm_is_opus():
    assert bb.resolve(bb.Role.AIPM).model == "claude-opus-4-8"
    assert bb.resolve(bb.Role.AIPM).provider is bb.Provider.ANTHROPIC


def test_scoring_is_gpt_openai():
    s = bb.resolve(bb.Role.SCORING)
    assert s.provider is bb.Provider.OPENAI
    assert s.model.startswith("gpt-5")


def test_design_is_gemini():
    d = bb.resolve(bb.Role.DESIGN)
    assert d.provider is bb.Provider.GOOGLE
    assert "gemini" in d.model


def test_writers_are_claude():
    for role in (bb.Role.WRITER_CORE, bb.Role.WRITER, bb.Role.WRITER_L4, bb.Role.PERSONA):
        assert bb.resolve(role).provider is bb.Provider.ANTHROPIC


def test_writer_core_is_opus():
    assert bb.resolve(bb.Role.WRITER_CORE).model == "claude-opus-4-8"


def test_l4_is_haiku():
    assert "haiku" in bb.resolve(bb.Role.WRITER_L4).model


# ── ★ 작성≠채점 계열분리 강제 ──
def test_separation_ok_default():
    assert bb.separation_ok() is True


def test_writer_vs_scoring_separation_passes():
    # Claude 작성 vs GPT 채점 → 다른 계열 → 통과
    bb.assert_writer_scorer_separation(bb.Role.WRITER, bb.Role.SCORING)


def test_same_family_scoring_blocked(monkeypatch):
    """작성 계열이 채점도 맡으면(편향) 차단."""
    # SCORING 을 Anthropic 으로 위장 → 작성(Claude)과 같은 계열
    orig = dict(bb.ROLE_BACKBONE)
    monkeypatch.setitem(
        bb.ROLE_BACKBONE, bb.Role.SCORING,
        (bb.Provider.ANTHROPIC, "SCORING_MODEL", "claude-opus-4-8"),
    )
    with pytest.raises(bb.BackboneSeparationError):
        bb.assert_writer_scorer_separation(bb.Role.WRITER, bb.Role.SCORING)
    assert bb.separation_ok() is False
    # 복원
    bb.ROLE_BACKBONE.update(orig)


def test_non_scoring_role_rejected_as_scorer():
    with pytest.raises(bb.BackboneSeparationError):
        bb.assert_writer_scorer_separation(bb.Role.WRITER, bb.Role.WRITER_CORE)


# ── .env 로더 ──
def test_load_env_returns_model_ids():
    env = bb.load_env()
    # .env 존재 시 모델 ID 가 읽힘 (CI/무키 환경에서도 기본값으로 resolve 됨)
    assert bb.resolve(bb.Role.AIPM).model  # non-empty
