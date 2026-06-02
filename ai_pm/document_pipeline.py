"""ai_pm/document_pipeline.py — PDF/PPTX 게이트 전달 (B-3 심장).

렌더 산출물(PDF/PPTX)도 텍스트와 **동일하게** 절대선 게이트를 거친다. 렌더물이
게이트를 우회하지 못하도록, 게이트는 렌더 **이전**에 원본 텍스트를 검증한다:

  assemble(text) → guarded_send(게이트) → (통과 시에만) [렌더 → as_document 전달]

핵심 불변식 (B-3 검수):
  - 위반 시 렌더 함수에 도달하지 못하고 as_document 전달도 일어나지 않는다
    → real_fn_called=False (렌더물도). 렌더는 게이트 통과 후에만 실행된다.
  - 게이트가 정제한 텍스트(면책 자동주입 포함)로만 렌더 → 렌더물도 면책 포함.
  - 헤르메스 직접수정 0. 강제는 ai_pm 레이어(production_pipeline 재사용).
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import document_renderer as dr
from .enforcement import AbsoluteLineGate
from .production_pipeline import ProducedDoc, ProductionPipeline


@dataclass
class DocumentDelivery:
    """문서 전달 결과.

    delivered:      as_document 전달 발생 여부
    real_fn_called: 실제 전달 함수 호출 여부 (= delivered)
    rendered:       렌더 발생 여부 (게이트 통과 시에만 True)
    render:         RenderResult (rendered=True 일 때)
    violations:     차단 사유 (delivered=False 일 때)
    flags:          비차단 플래그 (법무 등)
    """

    delivered: bool
    real_fn_called: bool
    rendered: bool
    render: object = None
    violations: list = field(default_factory=list)
    flags: list = field(default_factory=list)
    produced: ProducedDoc | None = None


class DocumentPipeline:
    """텍스트 조립 → 절대선 게이트 → (통과 시) 렌더 → as_document 전달.

    production_pipeline 의 게이트(guarded_send)를 재사용한다. 전달 함수
    (real_send_document)는 게이트 통과 후에만 호출되는 렌더+전달 클로저로 감싼다.
    """

    def __init__(self, gate: AbsoluteLineGate | None = None, *, out_dir: str | Path | None = None):
        self.pipeline = ProductionPipeline(gate=gate)
        self.out_dir = Path(out_dir) if out_dir else None

    def assemble(self, blocks: list, *, doc_type: str = "", claims=None) -> ProducedDoc:
        """텍스트 문서를 조립(PRODUCTION 채널). production_pipeline 위임."""
        return self.pipeline.assemble(blocks, doc_type=doc_type, claims=claims)

    def deliver_as_document(
        self,
        real_send_document,
        doc: ProducedDoc,
        *,
        fmt: str = "pptx",
        level: str = "L1",
        filename: str | None = None,
    ) -> DocumentDelivery:
        """절대선 게이트 통과 시에만 렌더 + as_document 전달.

        real_send_document(path, *, fmt, title, level, **meta) 형태의 실제 전달
        함수. 위반 시 호출되지 않으며 렌더도 일어나지 않는다.
        """
        render_state: dict = {"rendered": False, "result": None}

        def _render_and_send(checked_text, **_kw):
            # ── 이 클로저는 게이트 통과 후에만 호출된다 ──
            # 게이트가 정제한 텍스트(면책 주입 포함)로만 렌더.
            spec = dr.RenderSpec(
                title=_title_from(checked_text, doc),
                sections=dr.split_sections(checked_text),
                level=level,
                text=checked_text,
            )
            out_path = self._out_path(fmt, filename)
            result = dr.render(spec, out_path, fmt)
            render_state["rendered"] = True
            render_state["result"] = result
            # as_document: 원본 그대로 전달 (재압축 X)
            return real_send_document(
                result.path,
                fmt=result.fmt,
                title=result.title,
                level=result.level,
                slide_count=result.slide_count,
            )

        # production_pipeline.deliver → guarded_send 게이트.
        # _render_and_send 가 그 real_send 자리에 들어가 게이트 통과 후에만 도달.
        gate_result = self.pipeline.deliver(_render_and_send, doc)

        delivered = bool(gate_result["delivered"])
        return DocumentDelivery(
            delivered=delivered,
            real_fn_called=bool(gate_result["real_fn_called"]),
            rendered=render_state["rendered"],
            render=render_state["result"],
            violations=gate_result.get("violations", []),
            flags=gate_result.get("flags", []),
            produced=doc,
        )

    def _out_path(self, fmt: str, filename: str | None) -> Path:
        name = filename or f"vvs_doc.{fmt}"
        if not name.endswith(f".{fmt}"):
            name = f"{name}.{fmt}"
        if self.out_dir:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            return self.out_dir / name
        return Path(tempfile.gettempdir()) / name


def _title_from(text: str, doc: ProducedDoc) -> str:
    """본문 첫 머리말을 제목으로. 없으면 doc_type/기본값."""
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("#").strip()
    return doc.doc_type or "VVS"


def render_and_deliver_document(
    real_send_document,
    blocks: list,
    *,
    fmt: str = "pptx",
    level: str = "L1",
    doc_type: str = "",
    claims=None,
    gate: AbsoluteLineGate | None = None,
    out_dir: str | Path | None = None,
    filename: str | None = None,
) -> DocumentDelivery:
    """조립 + 게이트 + (통과 시) 렌더 + as_document 전달 원샷.

    스킬 스크립트(build_pptx/build_pdf)가 호출하는 표준 진입점.
    """
    pipeline = DocumentPipeline(gate=gate, out_dir=out_dir)
    doc = pipeline.assemble(blocks, doc_type=doc_type, claims=claims)
    return pipeline.deliver_as_document(
        real_send_document, doc, fmt=fmt, level=level, filename=filename
    )
