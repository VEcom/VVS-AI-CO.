"""B-2 검수 — 제작 스킬 + 절대선 래퍼 런타임 주입.

핵심 증명(★ 주입 최우선):
  제작 스킬 산출물이 **실제 제작 흐름**에서 guarded_send 를 거치며,
  위반 시 real_fn_called=False (계약 테스트가 아닌 실제 흐름).

추가: L1/L2/L4 스킬 산출, persona_generator invariant 가드, 제작채널≠고객채널
(청크 노출 0), 절대선 5개 실제 제작 흐름 작동.
"""

import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

from ai_pm.disclaimer_injector import REQUIRED_DISCLAIMER  # noqa: E402
from ai_pm.persona_generator import (  # noqa: E402
    PersonaInvariantError,
    generate_persona,
)
from ai_pm.production_pipeline import (  # noqa: E402
    ProductionPipeline,
    produce_and_deliver,
)
from ai_pm.sandbox import SYNTHETIC_MARK, InvalidIdentifierError  # noqa: E402


# ── 스킬 assemble 모듈 동적 로드 ──
def _load_skill(name: str):
    path = _REPO / "skills" / name / "scripts" / "assemble.py"
    spec = importlib.util.spec_from_file_location(f"_skill_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L1 = _load_skill("vvs-company-profile")
L2 = _load_skill("vvs-vendor-dossier")
L4 = _load_skill("vvs-onepager")


# ── 실제 송출 함수 스파이 (헤르메스 송출 대역) ──
class SendSpy:
    def __init__(self):
        self.called = False
        self.received = []

    def __call__(self, content, **kw):
        self.called = True
        self.received.append(content)
        return {"ok": True}


def _good_claim(**over):
    base = {
        "synthetic": True,
        "marking": SYNTHETIC_MARK,
        "statement": "협력사 등록 이력 양호",
        "source": "[SYNTHETIC] internal",
    }
    base.update(over)
    return base


def _clean_data(**over):
    data = {
        "title": "VVS 협력사 안내",
        "date": "2026-05-30",
        "company": "VVS",
        "summary": "반도체 협력사입니다.",
        "terms": "표준 거래 조건",
        "contact": "contact@example.com",
    }
    data.update(over)
    return data


# ════════════════════════════════════════════════════════════════════
# ★ 1) 래퍼 런타임 주입: 제작 산출물이 실제로 guarded_send 를 거친다
# ════════════════════════════════════════════════════════════════════
def test_L1_clean_flows_through_gate_and_delivers():
    spy = SendSpy()
    res = L1.run(_clean_data(), spy, claims=[_good_claim()])
    assert res["delivered"] is True
    assert res["real_fn_called"] is True
    assert spy.called is True
    # 게이트가 면책 자동주입 → 실제 송출된 본문에 포함 (게이트 경유 증명)
    assert REQUIRED_DISCLAIMER in spy.received[0]


def test_L2_clean_flows_through_gate_and_delivers():
    spy = SendSpy()
    res = L2.run(_clean_data(), spy, claims=[_good_claim()])
    assert res["delivered"] is True and res["real_fn_called"] is True
    assert REQUIRED_DISCLAIMER in spy.received[0]


def test_L4_clean_flows_through_gate_and_delivers():
    spy = SendSpy()
    res = L4.run(_clean_data(), spy, claims=[_good_claim()])
    assert res["delivered"] is True and res["real_fn_called"] is True


# ════════════════════════════════════════════════════════════════════
# ★ 2) 주입 후에도 real_fn_called=False (실제 제작 흐름, 전 레벨)
# ════════════════════════════════════════════════════════════════════
def test_L1_banned_blocks_real_fn_in_real_flow():
    spy = SendSpy()
    # 회사 소개에 금지표현 주입 → 실제 제작 흐름에서 게이트가 차단
    res = L1.run(_clean_data(company="저희가 무조건 업계 1위입니다"), spy)
    assert res["delivered"] is False
    assert res["real_fn_called"] is False
    assert spy.called is False  # ← 실제 송출 함수 미도달 (실제 흐름)


def test_L2_unverified_fact_blocks_real_fn_in_real_flow():
    spy = SendSpy()
    bad = _good_claim(source="")  # 출처 없음 → 미검증
    res = L2.run(_clean_data(), spy, claims=[bad])
    assert res["real_fn_called"] is False and spy.called is False
    assert any(v["kind"] == "fact" for v in res["violations"])


def test_L4_banned_blocks_real_fn_in_real_flow():
    spy = SendSpy()
    res = L4.run(_clean_data(summary="확실히 100% 보장합니다"), spy)
    assert res["real_fn_called"] is False and spy.called is False


def test_all_levels_block_on_violation():
    """L1/L2/L4 전부 위반 시 고객 전달 0 (실제 흐름)."""
    for skill in (L1, L2, L4):
        spy = SendSpy()
        res = skill.run(_clean_data(company="무조건 최고 절대 보장"), spy)
        assert res["real_fn_called"] is False
        assert spy.called is False


# ════════════════════════════════════════════════════════════════════
# 3) 제작채널 ≠ 고객채널 (청크 노출 0)
# ════════════════════════════════════════════════════════════════════
def test_assembly_stays_in_production_channel_not_customer():
    pipeline = ProductionPipeline()
    doc = pipeline.assemble(
        [("header", {"title": "T", "date": "2026-05-30"})],
        doc_type="회사소개서",
    )
    # 조립물은 PRODUCTION 채널에만, 고객 전달 0
    assert doc.text in pipeline.production_outputs()
    assert pipeline.customer_delivered_count() == 0


def test_llm_bypass_zero_customer_delivery_in_production():
    """LLM 이 assemble 만 하고 deliver 를 호출하지 않으면 고객 전달 0."""
    spy = SendSpy()
    pipeline = ProductionPipeline()
    pipeline.assemble([("header", {"title": "T", "date": "d"})])
    # deliver 미호출 → 고객 전달 0, 송출 함수 미호출
    assert pipeline.customer_delivered_count() == 0
    assert spy.called is False


def test_violating_delivery_keeps_customer_channel_empty():
    spy = SendSpy()
    pipeline = ProductionPipeline()
    doc = pipeline.assemble([("company_intro", {"company": "무조건 1위", "summary": "x"})])
    res = pipeline.deliver(spy, doc)
    assert res["real_fn_called"] is False
    assert pipeline.customer_delivered_count() == 0


# ════════════════════════════════════════════════════════════════════
# 4) persona_generator — invariant 가드
# ════════════════════════════════════════════════════════════════════
def _yesterday() -> date:
    return date.today() - timedelta(days=1)


def test_persona_valid():
    p = generate_persona(
        name="합성-홍길동",
        identifier="000000",
        start=date(2020, 1, 1),
        end=_yesterday(),
        ym=0,
    )
    assert p.synthetic is True and p.marking == SYNTHETIC_MARK
    assert p.as_dict()["ym"] == 0


def test_persona_ym_must_be_0_based():
    with pytest.raises(PersonaInvariantError):
        generate_persona(
            name="x", identifier="000000",
            start=date(2020, 1, 1), end=_yesterday(), ym=12,  # 범위 밖
        )
    with pytest.raises(PersonaInvariantError):
        generate_persona(
            name="x", identifier="000000",
            start=date(2020, 1, 1), end=_yesterday(), ym=-1,
        )


def test_persona_start_must_be_before_end():
    with pytest.raises(PersonaInvariantError):
        generate_persona(
            name="x", identifier="000000",
            start=date(2021, 1, 1), end=date(2020, 1, 1), ym=0,  # 역전
        )
    with pytest.raises(PersonaInvariantError):
        generate_persona(
            name="x", identifier="000000",
            start=date(2020, 1, 1), end=date(2020, 1, 1), ym=0,  # 동일
        )


def test_persona_future_blocked():
    future = date.today() + timedelta(days=10)
    with pytest.raises(PersonaInvariantError):
        generate_persona(
            name="x", identifier="000000",
            start=date(2020, 1, 1), end=future, ym=0,
        )


def test_persona_identifier_must_be_void():
    with pytest.raises(InvalidIdentifierError):
        generate_persona(
            name="x", identifier="901234",  # 유효형 식별자 → 거부
            start=date(2020, 1, 1), end=_yesterday(), ym=0,
        )


# ════════════════════════════════════════════════════════════════════
# 5) 절대선 5개 실제 제작 흐름에서 작동 (produce_and_deliver 직접)
# ════════════════════════════════════════════════════════════════════
def test_gate_disclaimer_autoinject_in_pipeline():
    spy = SendSpy()
    # 면책 없는 깨끗한 본문 → 파이프라인이 자동주입 후 전달
    res = produce_and_deliver(
        spy,
        [("company_intro", {"company": "VVS", "summary": "정상 소개"})],
        doc_type="회사소개서",
    )
    assert res["delivered"] is True
    assert REQUIRED_DISCLAIMER in spy.received[0]


def test_gate_legal_flag_nonblocking_in_pipeline():
    spy = SendSpy()
    res = produce_and_deliver(
        spy,
        [("terms", {"terms": "위약금 조항 포함 " + REQUIRED_DISCLAIMER})],
        doc_type="제안서",
    )
    # 법무 플래그는 비차단 → 전달됨
    assert res["delivered"] is True and res["real_fn_called"] is True
    assert any(f["kind"] == "legal_review_required" for f in res["flags"])


def test_produced_doc_returned_for_inspection():
    spy = SendSpy()
    res = produce_and_deliver(
        spy,
        [("header", {"title": "T", "date": "2026-05-30"})],
    )
    assert "produced" in res
    assert res["produced"].doc_type == ""
    assert "T" in res["produced"].text
