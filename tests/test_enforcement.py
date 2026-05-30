"""B-1 절대선 강제점 — 가장 엄격한 검수.

핵심 증명: **위반 산출물이 실제 송출 함수에 도달하지 못한다 (real_fn_called=False).**
또한 LLM 우회(도구 미호출) 시 고객 전달 0, 외부발송 차단, 환각 궤적 제외,
제작채널≠고객채널 강제, 절대선 5개 게이트 각각 작동을 검증한다.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_pm.channels import ChannelRouter  # noqa: E402
from ai_pm.disclaimer_injector import REQUIRED_DISCLAIMER  # noqa: E402
from ai_pm.enforcement import (  # noqa: E402
    AbsoluteLineGate,
    guard_send_message_tool,
    guarded_send,
    wrap_send,
)
from ai_pm.external_send_guard import (  # noqa: E402
    GuardedExternalSendMixin,
    guard_external_send,
)
from ai_pm.sandbox import SYNTHETIC_MARK  # noqa: E402
from ai_pm.trajectory_gate import finalize_trajectories, is_hallucinated  # noqa: E402


# ── 송출 스파이: real_fn_called 추적 ──
class SendSpy:
    """실제 송출 함수 대역. 호출되면 called=True 로 기록."""

    def __init__(self):
        self.called = False
        self.received = []

    def __call__(self, content, **kw):
        self.called = True
        self.received.append(content)
        return {"ok": True, "sent": content}


def _good_claim(**over):
    base = {
        "synthetic": True,
        "marking": SYNTHETIC_MARK,
        "statement": "협력사 만족도 양호",
        "source": "[SYNTHETIC] survey",
    }
    base.update(over)
    return base


# ════════════════════════════════════════════════════════════════════
# 1) send_message 래퍼: 위반 산출물 real_fn_called=False
# ════════════════════════════════════════════════════════════════════
def test_banned_blocks_real_fn_not_called():
    spy = SendSpy()
    res = guarded_send(spy, "저희가 무조건 최고입니다")  # 금지표현 2개
    assert res["delivered"] is False
    assert res["real_fn_called"] is False
    assert spy.called is False  # ← 실제 송출 함수 미도달 증명
    assert any(v["kind"] == "banned_phrase" for v in res["violations"])


def test_fact_unverified_blocks_real_fn_not_called():
    spy = SendSpy()
    bad_claim = _good_claim(source="")  # 출처 없음 → 미검증
    res = guarded_send(
        spy,
        "합리적 제안입니다. " + REQUIRED_DISCLAIMER,
        claims=[bad_claim],
    )
    assert res["delivered"] is False
    assert res["real_fn_called"] is False
    assert spy.called is False
    assert any(v["kind"] == "fact" for v in res["violations"])


def test_clean_content_delivers_and_calls_real_fn():
    spy = SendSpy()
    res = guarded_send(
        spy,
        "합리적인 제안 드립니다.",
        claims=[_good_claim()],
    )
    assert res["delivered"] is True
    assert res["real_fn_called"] is True
    assert spy.called is True
    # 면책 자동주입되어 실제 송출된 content 에 포함
    assert REQUIRED_DISCLAIMER in spy.received[0]


def test_wrap_send_decorator_blocks():
    spy = SendSpy()
    guarded = wrap_send(spy)
    res = guarded("확실히 1위 입니다")  # 금지표현
    assert res["real_fn_called"] is False and spy.called is False


def test_guard_send_message_tool_shape():
    spy_tool_called = {"v": False}

    def real_tool(args, **kw):
        spy_tool_called["v"] = True
        return {"sent": args["content"]}

    # 위반 → real_tool 미호출
    blocked = guard_send_message_tool(real_tool, {"content": "무조건 보장"})
    assert blocked["real_fn_called"] is False and spy_tool_called["v"] is False

    # 정상 → real_tool 호출 (면책 주입된 content 전달)
    ok = guard_send_message_tool(
        real_tool, {"content": "안내드립니다", "claims": [_good_claim()]}
    )
    assert ok["real_fn_called"] is True and spy_tool_called["v"] is True


# ════════════════════════════════════════════════════════════════════
# 2) LLM 우회 (도구 안 불러도) 고객 전달 0
# ════════════════════════════════════════════════════════════════════
def test_llm_bypass_zero_customer_delivery():
    spy = SendSpy()
    router = ChannelRouter()
    # LLM 이 산출물만 내고 send_message(deliver_to_customer)를 호출하지 않음
    out = router.emit_agent_output("고객에게 보이면 안 되는 제작 산출물")
    assert out["customer_delivered"] is False
    assert router.customer_delivered_count() == 0  # ← 고객 전달 0
    assert spy.called is False


def test_customer_delivery_only_via_gated_send():
    spy = SendSpy()
    router = ChannelRouter()
    # 명시 호출 + 위반 → 고객 전달 0, real_fn 미호출
    blocked = router.deliver_to_customer(spy, "절대 무조건")
    assert blocked["delivered"] is False and spy.called is False
    assert router.customer_delivered_count() == 0
    # 명시 호출 + 정상 → 고객 전달 1
    ok = router.deliver_to_customer(spy, "정상 안내", claims=[_good_claim()])
    assert ok["delivered"] is True and spy.called is True
    assert router.customer_delivered_count() == 1


# ════════════════════════════════════════════════════════════════════
# 3) base.send 서브클래스: 외부발송 차단 (#2)
# ════════════════════════════════════════════════════════════════════
def test_external_send_func_blocked_in_learning():
    spy = SendSpy()

    def real_send(chat_id, content, **kw):
        spy.called = True
        return {"sent": content}

    res = guard_external_send(real_send, "chat1", "hello", learning_mode=True)
    assert res["sent"] is False
    assert res["real_fn_called"] is False
    assert spy.called is False  # ← 외부 send 미도달


def test_external_send_func_allowed_when_not_learning():
    spy = SendSpy()

    def real_send(chat_id, content, **kw):
        spy.called = True
        return {"sent": content}

    res = guard_external_send(real_send, "chat1", "hi", learning_mode=False)
    assert res["sent"] is True and spy.called is True


def test_guarded_mixin_blocks_super_send():
    import asyncio

    real_called = {"v": False}

    class FakeAdapter:
        async def send(self, chat_id, content, metadata=None, **kwargs):
            real_called["v"] = True
            return {"sent": content}

    class Guarded(GuardedExternalSendMixin, FakeAdapter):
        learning_mode = True

    adapter = Guarded()
    from ai_pm.sandbox import ExternalSendBlocked

    with pytest.raises(ExternalSendBlocked):
        asyncio.run(adapter.send("c1", "hello"))
    assert real_called["v"] is False  # ← super().send 미도달

    # 학습 모드 해제 시 통과
    adapter.learning_mode = False
    assert asyncio.run(adapter.send("c1", "hello"))["sent"] == "hello"
    assert real_called["v"] is True


# ════════════════════════════════════════════════════════════════════
# 4) batch_runner _finalize: 환각 궤적 제외
# ════════════════════════════════════════════════════════════════════
def test_trajectory_hallucination_detection():
    clean = {"output": "정상 산출물", "claims": [_good_claim()]}
    banned = {"output": "무조건 최고", "claims": [_good_claim()]}
    bad_fact = {"output": "정상", "claims": [_good_claim(source="")]}
    assert is_hallucinated(clean) is False
    assert is_hallucinated(banned) is True
    assert is_hallucinated(bad_fact) is True


def test_finalize_excludes_hallucinated():
    trajs = [
        {"output": "정상1", "claims": [_good_claim()]},
        {"output": "절대 보장", "claims": [_good_claim()]},          # banned
        {"output": "정상2", "claims": [_good_claim(source="")]},      # bad fact
        {"output": "정상3", "claims": []},
    ]
    result = finalize_trajectories(trajs)
    assert len(result["kept"]) == 2
    assert len(result["excluded"]) == 2
    kept_outputs = {t["output"] for t in result["kept"]}
    assert kept_outputs == {"정상1", "정상3"}


# ════════════════════════════════════════════════════════════════════
# 5) 절대선 5개 게이트 각각 작동
# ════════════════════════════════════════════════════════════════════
def test_gate_fact_line1():
    g = AbsoluteLineGate()
    v = g.check("내용 " + REQUIRED_DISCLAIMER, claims=[_good_claim(source="")])
    assert v.passed is False and v.checks["fact"] is False


def test_gate_banned_line3():
    g = AbsoluteLineGate()
    v = g.check("무조건 " + REQUIRED_DISCLAIMER)
    assert v.passed is False and v.checks["banned"] is False


def test_gate_disclaimer_inject_vs_block():
    inject_gate = AbsoluteLineGate(disclaimer_mode="inject")
    v1 = inject_gate.check("면책 없는 정상 문구")
    assert v1.passed is True and REQUIRED_DISCLAIMER in v1.content

    block_gate = AbsoluteLineGate(disclaimer_mode="block")
    v2 = block_gate.check("면책 없는 정상 문구")
    assert v2.passed is False
    assert any(x["kind"] == "disclaimer_missing" for x in v2.violations)


def test_gate_legal_line4_nonblocking():
    g = AbsoluteLineGate()
    v = g.check("위약금 조항 안내 " + REQUIRED_DISCLAIMER, doc_type="제안서")
    # 법무는 플래그(비차단)
    assert v.passed is True
    assert any(f["kind"] == "legal_review_required" for f in v.flags)


def test_gate_all_pass():
    g = AbsoluteLineGate()
    v = g.check("정상 안내문 " + REQUIRED_DISCLAIMER, claims=[_good_claim()])
    assert v.passed is True and not v.violations
