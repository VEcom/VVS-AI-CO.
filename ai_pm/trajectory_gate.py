"""ai_pm/trajectory_gate.py — batch_runner _finalize 학습 궤적 게이트.

배치 학습 궤적을 확정(_finalize)하기 전, 결정론 게이트 체인으로 **환각 궤적을
제외**한다. 환각 신호 = 미검증 주장(fact 위반) 또는 금지 표현(banned).

Hermes `batch_runner.BatchRunner.run()`/`main()` 의 finalize 시점에서
`finalize_trajectories` 를 호출해, 절대선 위반 궤적이 학습 데이터에 들어가지
못하게 한다.
"""

from __future__ import annotations

from .enforcement import AbsoluteLineGate


def _learning_gate(gate: AbsoluteLineGate | None) -> AbsoluteLineGate:
    # 학습 궤적은 fact/banned 만 강제 (면책/법무는 전달 단계 관심사).
    return gate or AbsoluteLineGate(enforce=("fact", "banned"))


def is_hallucinated(trajectory: dict, gate: AbsoluteLineGate | None = None) -> bool:
    """궤적이 환각(절대선 위반)인지 결정론적으로 판정.

    trajectory 예: {"output": "...", "claims": [...], "doc_type": "..."}
    """
    gate = _learning_gate(gate)
    trajectory = trajectory or {}
    verdict = gate.check(
        trajectory.get("output", ""),
        doc_type=trajectory.get("doc_type", ""),
        claims=trajectory.get("claims", []),
    )
    return not verdict.passed


def finalize_trajectories(trajectories, gate: AbsoluteLineGate | None = None) -> dict:
    """환각 궤적을 제외하고 학습용 궤적만 남긴다.

    반환: {"kept": [...], "excluded": [{"trajectory": t, "violations": [...]}, ...]}
    """
    gate = _learning_gate(gate)
    kept: list = []
    excluded: list = []
    for traj in trajectories or []:
        verdict = gate.check(
            (traj or {}).get("output", ""),
            doc_type=(traj or {}).get("doc_type", ""),
            claims=(traj or {}).get("claims", []),
        )
        if verdict.passed:
            kept.append(traj)
        else:
            excluded.append({"trajectory": traj, "violations": verdict.violations})
    return {"kept": kept, "excluded": excluded}
