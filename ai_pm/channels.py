"""ai_pm/channels.py — 제작채널 ≠ 고객채널 (코드+설정 강제).

절대선 산출물은 **PM 전용(production) 세션**으로만 나간다. 고객 전달은
`send_message` 게이트를 통한 **명시 호출**로만 가능하다. 따라서 LLM 이 도구를
호출하지 않으면(우회) 고객 전달은 0 이다.

핵심 불변식:
  - 에이전트의 기본 산출물 → production sink (고객 미도달).
  - 고객 sink 로 가는 유일한 경로 = `deliver_to_customer`(절대선 게이트 경유).
"""

from __future__ import annotations

from .enforcement import AbsoluteLineGate, guarded_send

PRODUCTION = "production"  # PM 전용 제작 채널
CUSTOMER = "customer"      # 고객 전달 채널


class ChannelRouter:
    """제작/고객 채널 분리 라우터.

    - emit_agent_output: 기본 산출물을 production sink 로만 보낸다(고객 미도달).
    - deliver_to_customer: 절대선 게이트를 통과한 경우에만 customer sink 로.
    """

    def __init__(self, gate: AbsoluteLineGate | None = None):
        self.gate = gate or AbsoluteLineGate()
        self.production_sink: list = []
        self.customer_sink: list = []

    def emit_agent_output(self, content) -> dict:
        """에이전트 기본 산출물 → production 채널 전용. 고객 미도달."""
        self.production_sink.append(content)
        return {"channel": PRODUCTION, "customer_delivered": False}

    def deliver_to_customer(
        self, real_send, content, *, doc_type: str = "", claims=None, **kw
    ) -> dict:
        """고객 전달 — 유일한 고객 경로. 절대선 게이트 경유.

        게이트 차단 시 real_send 미호출 + customer_sink 불변.
        """
        result = guarded_send(
            real_send,
            content,
            doc_type=doc_type,
            claims=claims,
            gate=self.gate,
            **kw,
        )
        if result["delivered"]:
            self.customer_sink.append(result["content"])
        return result

    def customer_delivered_count(self) -> int:
        return len(self.customer_sink)
