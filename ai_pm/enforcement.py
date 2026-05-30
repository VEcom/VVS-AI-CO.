"""ai_pm/enforcement.py — 절대선 강제점 (헌법의 심장, H-3 패턴).

Hermes 의 실제 송출 함수를 래핑해, **위반 산출물이 실제 송출 함수에 도달하지
못하도록** 막는다. 게이트는 VVS-AI-CO 안에 있으므로 영구 보존되며, 구조적으로
`real_fn_called=False` 를 보장한다(차단 시 real_send 호출문에 도달 불가).

강제하는 절대선:
  #1 fact     : fact_verifier 미통과(미검증 주장) → 차단
  #3 banned   : banned_phrase_filter hard hit → 차단
  #3 disclaimer: 면책 부재 → 자동주입(기본) 또는 차단(strict)
  #4 legal    : legal_safety_router 트리거 → 플래그(비차단)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .banned_phrase_filter import filter_text
from .disclaimer_injector import has_disclaimer, inject
from .fact_verifier import verify_fact
from .legal_safety_router import route

# 강제 가능한 검사 항목
ALL_CHECKS = ("fact", "banned", "disclaimer", "legal")


@dataclass
class Verdict:
    """게이트 판정 결과."""

    passed: bool
    content: str
    violations: list = field(default_factory=list)  # 차단 사유 (헌법 위반)
    flags: list = field(default_factory=list)        # 비차단 플래그 (법무 등)
    checks: dict = field(default_factory=dict)        # 항목별 통과 여부


class AbsoluteLineGate:
    """절대선 게이트. content/claims 를 검사해 Verdict 를 낸다.

    disclaimer_mode:
      - "inject": 면책 누락 시 자동 주입 후 통과 (기본, 고객 전달용)
      - "block" : 면책 누락 시 차단 (엄격)
    enforce: 강제할 검사 항목 부분집합 (학습 궤적은 fact/banned 만 등).
    """

    def __init__(self, disclaimer_mode: str = "inject", enforce=ALL_CHECKS):
        if disclaimer_mode not in ("inject", "block"):
            raise ValueError("disclaimer_mode must be 'inject' or 'block'")
        self.disclaimer_mode = disclaimer_mode
        self.enforce = tuple(enforce)

    def check(self, content, *, doc_type: str = "", claims=None) -> Verdict:
        content = "" if content is None else str(content)
        claims = claims or []
        violations: list = []
        flags: list = []
        checks: dict = {}

        # #1 fact — 미검증 주장이 하나라도 있으면 차단
        if "fact" in self.enforce:
            unverified = []
            for claim in claims:
                r = verify_fact(claim)
                if not r["verified"]:
                    unverified.append(r["reason"])
            checks["fact"] = not unverified
            if unverified:
                violations.append({"line": 1, "kind": "fact", "detail": unverified})

        # #3 banned — 금지 표현 hard hit → 차단
        if "banned" in self.enforce:
            bp = filter_text(content)
            checks["banned"] = bp["clean"]
            if not bp["clean"]:
                violations.append(
                    {"line": 3, "kind": "banned_phrase", "detail": bp["violations"]}
                )

        # #3 disclaimer — 부재 시 자동주입(기본) 또는 차단(strict)
        if "disclaimer" in self.enforce:
            if has_disclaimer(content):
                checks["disclaimer"] = True
            elif self.disclaimer_mode == "inject":
                content = inject(content)
                checks["disclaimer"] = True
                flags.append({"line": 3, "kind": "disclaimer_injected"})
            else:  # block
                checks["disclaimer"] = False
                violations.append({"line": 3, "kind": "disclaimer_missing"})

        # #4 legal — 비차단 플래그
        if "legal" in self.enforce:
            lr = route(doc_type, content)
            checks["legal"] = True
            if lr["requires_legal"]:
                flags.append(
                    {"line": 4, "kind": "legal_review_required", "detail": lr["reason"]}
                )

        return Verdict(
            passed=not violations,
            content=content,
            violations=violations,
            flags=flags,
            checks=checks,
        )


def guarded_send(
    real_send,
    content,
    *,
    doc_type: str = "",
    claims=None,
    gate: AbsoluteLineGate | None = None,
    **send_kwargs,
) -> dict:
    """H-3 게이트: real_send 를 절대선 통과 시에만 호출한다.

    위반 시 real_send 는 **호출되지 않는다** (이 함수에서 real_send 호출문은
    `verdict.passed` 통과 이후 단 한 곳뿐).

    반환:
      차단: {"delivered": False, "real_fn_called": False, "violations": [...], "flags": [...]}
      전달: {"delivered": True,  "real_fn_called": True, "result": ..., "content": ..., "flags": [...]}
    """
    gate = gate or AbsoluteLineGate()
    verdict = gate.check(content, doc_type=doc_type, claims=claims)

    if not verdict.passed:
        # 차단 — real_send 에 도달하지 못한다.
        return {
            "delivered": False,
            "real_fn_called": False,
            "violations": verdict.violations,
            "flags": verdict.flags,
            "checks": verdict.checks,
        }

    # 통과 — 정제된(면책 주입된) content 로만 실제 송출.
    result = real_send(verdict.content, **send_kwargs)
    return {
        "delivered": True,
        "real_fn_called": True,
        "result": result,
        "content": verdict.content,
        "flags": verdict.flags,
        "checks": verdict.checks,
    }


def wrap_send(real_send, *, gate: AbsoluteLineGate | None = None):
    """real_send 를 게이트로 감싼 호출가능 객체를 반환 (데코레이터 형태)."""

    def guarded(content, *, doc_type: str = "", claims=None, **send_kwargs):
        return guarded_send(
            real_send,
            content,
            doc_type=doc_type,
            claims=claims,
            gate=gate,
            **send_kwargs,
        )

    return guarded


def guard_send_message_tool(real_tool, args: dict, *, gate=None, **kw) -> dict:
    """Hermes `send_message_tool(args, **kw)` 형태 진입점을 게이트로 감싼다.

    args 에서 content/doc_type/claims 를 추출해 검사하고, 통과 시에만
    real_tool(정제된 args, **kw) 를 호출한다.
    """
    args = dict(args or {})
    content = args.get("content", "")
    doc_type = args.get("doc_type", "")
    claims = args.get("claims", [])

    def _real(checked_content, **send_kwargs):
        forwarded = dict(args)
        forwarded["content"] = checked_content
        return real_tool(forwarded, **send_kwargs)

    return guarded_send(
        _real, content, doc_type=doc_type, claims=claims, gate=gate, **kw
    )
