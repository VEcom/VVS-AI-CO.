"""ai_pm/production_pipeline.py — 제작 산출물 → 절대선 게이트 주입 레이어 (B-2 심장).

B-1 의 강제점 래퍼(enforcement/channels)를 **실제 제작 흐름에 주입**한다. 제작
스킬은 송출 함수를 직접 호출하지 않는다. 대신 block_library 로 문서를 조립한 뒤
반드시 이 파이프라인을 거치며, 파이프라인이 ChannelRouter→guarded_send 로 절대선
게이트를 강제한다.

핵심 불변식 (B-2 검수):
  - 제작 산출물이 고객에게 가는 유일한 경로 = deliver(). 그 안에서 guarded_send
    호출이 단 하나뿐이며 게이트 통과 후에만 도달한다 → 위반 시 real_fn_called=False.
  - 헤르메스를 직접 수정하지 않는다(bootstrap 재현 유지). 강제는 ai_pm 레이어에서.
  - 제작(조립)은 PRODUCTION 채널, 고객 전달은 CUSTOMER 채널로만(채널 분리).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import block_library
from .channels import ChannelRouter
from .enforcement import AbsoluteLineGate


@dataclass
class ProducedDoc:
    """제작 파이프라인이 조립한 산출물(아직 고객 미전달).

    text:    조립된 문서 본문 (PRODUCTION 채널에만 존재)
    doc_type: 문서 유형 (legal 라우팅용)
    claims:  fact 검증 대상 주장들
    sections: 섹션별 텍스트 (rubric/완전성용)
    """

    text: str
    doc_type: str = ""
    claims: list = field(default_factory=list)
    sections: dict = field(default_factory=dict)


class ProductionPipeline:
    """제작 스킬과 절대선 게이트 사이의 단일 강제 지점.

    assemble(): block_library 로 문서를 조립 → PRODUCTION 채널에만 적재(고객 미도달).
    deliver():  명시 호출 시에만, guarded_send 게이트를 통과한 경우 고객 전달.
    """

    def __init__(self, gate: AbsoluteLineGate | None = None):
        # 고객 전달용 게이트는 기본(면책 자동주입). 라우터가 guarded_send 를 소유.
        self.router = ChannelRouter(gate=gate or AbsoluteLineGate())

    # ── 제작(조립): PRODUCTION 채널 전용, 고객 미도달 ──
    def assemble(self, blocks: list, *, doc_type: str = "", claims=None) -> ProducedDoc:
        """block_library 블록 스펙으로 문서를 조립한다.

        blocks: [(block_id, data_dict), ...]
        조립 결과는 production sink 에만 들어간다(emit_agent_output) — 고객 미도달.
        """
        rendered = []
        sections: dict = {}
        for block_id, data in blocks:
            piece = block_library.render_block(block_id, data)
            rendered.append(piece)
            sections[block_id] = piece
        text = "\n\n".join(rendered)

        # 제작 산출물은 PRODUCTION 채널에만. (청크/중간물 고객 노출 0)
        self.router.emit_agent_output(text)

        return ProducedDoc(
            text=text,
            doc_type=doc_type,
            claims=list(claims or []),
            sections=sections,
        )

    # ── 고객 전달: 유일 경로. 절대선 게이트 강제 주입 ──
    def deliver(self, real_send, doc: ProducedDoc, **send_kwargs) -> dict:
        """제작 산출물을 고객에게 전달한다 — 절대선 게이트를 반드시 거친다.

        위반 시 real_send 는 호출되지 않는다(real_fn_called=False). 이 메서드 안에서
        고객 전달은 router.deliver_to_customer(=guarded_send) 단 한 경로뿐이다.
        """
        return self.router.deliver_to_customer(
            real_send,
            doc.text,
            doc_type=doc.doc_type,
            claims=doc.claims,
            **send_kwargs,
        )

    def customer_delivered_count(self) -> int:
        return self.router.customer_delivered_count()

    def production_outputs(self) -> list:
        """PRODUCTION 채널에 적재된 제작물(고객 미도달) 목록."""
        return list(self.router.production_sink)


def produce_and_deliver(
    real_send,
    blocks: list,
    *,
    doc_type: str = "",
    claims=None,
    gate: AbsoluteLineGate | None = None,
    **send_kwargs,
) -> dict:
    """조립 + 전달 원샷. 스킬 스크립트가 호출하는 표준 진입점.

    반환: ProductionPipeline.deliver 결과 dict
          {"delivered": bool, "real_fn_called": bool, "violations": [...], ...}
    + "produced": ProducedDoc 를 함께 담아 반환.
    """
    pipeline = ProductionPipeline(gate=gate)
    doc = pipeline.assemble(blocks, doc_type=doc_type, claims=claims)
    result = pipeline.deliver(real_send, doc, **send_kwargs)
    result["produced"] = doc
    return result
