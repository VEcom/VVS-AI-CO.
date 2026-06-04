"""절대선 5개 — 헌법 단위테스트.

fact_verifier · banned_phrase_filter · disclaimer_injector · legal_safety_router
(+ banned_phrases 목록). 정확성이 절대적이므로 계약을 엄격히 검증한다.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_pm import (  # noqa: E402
    banned_phrases,
    banned_phrase_filter,
    disclaimer_injector,
    fact_verifier,
    legal_safety_router,
)
from ai_pm.banned_phrase_filter import BannedPhraseError  # noqa: E402
from ai_pm.disclaimer_injector import REQUIRED_DISCLAIMER  # noqa: E402
from ai_pm.sandbox import SYNTHETIC_MARK  # noqa: E402


# ── 절대선 #1: fact_verifier ──
def _good_claim(**over):
    base = {
        "synthetic": True,
        "marking": SYNTHETIC_MARK,
        "statement": "협력사 만족도가 높음",
        "source": "[SYNTHETIC] survey",
    }
    base.update(over)
    return base


def test_fact_verify_ok():
    assert fact_verifier.verify_fact(_good_claim())["verified"] is True


def test_fact_verify_rejects_non_synthetic():
    claim = _good_claim()
    claim["synthetic"] = False
    assert fact_verifier.verify_fact(claim)["verified"] is False


def test_fact_verify_requires_source():
    claim = _good_claim(source="")
    r = fact_verifier.verify_fact(claim)
    assert r["verified"] is False and "source" in r["reason"]


def test_fact_verify_numeric_requires_evidence():
    claim = _good_claim(statement="매출 30% 증가", value=30)
    assert fact_verifier.verify_fact(claim)["verified"] is False
    claim["evidence"] = "[SYNTHETIC] report p.3"
    assert fact_verifier.verify_fact(claim)["verified"] is True


def test_fact_verify_non_dict():
    assert fact_verifier.verify_fact("nope")["verified"] is False


# ── 절대선 #2 토대는 test_sandbox.py 에서 검증 ──


# ── 절대선 #3: banned_phrases + filter ──
def test_banned_list_exact():
    assert banned_phrases.get_banned() == [
        "100% 보장", "절대", "확실히", "무조건", "최고", "1위", "유일한",
    ]


def test_filter_detects():
    r = banned_phrase_filter.filter_text("저희가 100% 보장 합니다")
    assert r["clean"] is False and "100% 보장" in r["violations"]


def test_filter_clean():
    assert banned_phrase_filter.filter_text("합리적인 제안입니다")["clean"] is True


def test_check_and_raise():
    with pytest.raises(BannedPhraseError):
        banned_phrase_filter.check_and_raise("무조건 최고입니다")
    banned_phrase_filter.check_and_raise("괜찮은 문서")  # 통과


# ── 절대선 #4: disclaimer_injector ──
def test_disclaimer_inject_and_detect():
    doc = "견적 내용"
    assert disclaimer_injector.has_disclaimer(doc) is False
    out = disclaimer_injector.inject(doc)
    assert disclaimer_injector.has_disclaimer(out) is True
    assert REQUIRED_DISCLAIMER in out


def test_disclaimer_idempotent():
    once = disclaimer_injector.inject("문서")
    twice = disclaimer_injector.inject(once)
    assert once == twice


# ── 절대선 #5: legal_safety_router ──
def test_legal_router_contract_type():
    r = legal_safety_router.route("계약서", "내용")
    assert r["requires_legal"] is True


def test_legal_router_content_trigger():
    r = legal_safety_router.route("제안서", "위약금 조항 포함")
    assert r["requires_legal"] is True


def test_legal_router_clean():
    r = legal_safety_router.route("견적서", "단가 안내")
    assert r["requires_legal"] is False
