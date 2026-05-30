"""ai_pm/sandbox.py — 절대선 #2 격리 + [SYNTHETIC] 검증.

betplay vvs-platform/ai_pm/sandbox.py 의 이식본.

핵심만 우선 구현하며, B-1에서 헤르메스 HERMES_HOME 격리와 통합/강화한다.
- Phase 0(학습 단계): production 절대 미접근 + 외부 발송 금지(절대선 #2).
- 합성 데이터는 반드시 [SYNTHETIC] 마킹 + synthetic=True.
- 합성 식별자는 무효(전부 0/-)여야 한다.

새 세션 생성 메모: fact_verifier·persona_generator 가
    from ai_pm.sandbox import validate_synthetic, SYNTHETIC_MARK, assert_invalid_identifier
sqlite_db.open_sandboxed 가 sandbox.path(relpath) 를 사용한다.
"""

from __future__ import annotations

from pathlib import Path

SYNTHETIC_MARK = "[SYNTHETIC]"


class SyntheticMarkingError(Exception):
    """합성 데이터 마킹 누락/오류."""


class InvalidIdentifierError(Exception):
    """합성 식별자가 무효 형식이 아님."""


class ExternalSendBlocked(Exception):
    """Phase 0 학습 단계에서 외부 발송 차단 (절대선 #2)."""


class SandboxEscapeError(Exception):
    """sandbox 트리 밖으로의 경로 탈출 시도."""


def has_production_access() -> bool:
    return False  # 하드코딩 — Phase 0 절대 production 미접근


def no_external_send(*a, **k):
    # 절대선 #2 — 외부 발송 금지
    raise ExternalSendBlocked("외부 발송은 Phase 0 학습 단계에서 금지됩니다.")


def is_obviously_invalid(value: str) -> bool:
    value = str(value)
    return bool(value) and set(value) <= {"0", "-"}  # 전부 0/- = 무효 식별자


def assert_invalid_identifier(value: str) -> None:
    if not is_obviously_invalid(value):
        raise InvalidIdentifierError(
            f"synthetic identifier must be void, got {value!r}"
        )


def validate_synthetic(obj) -> None:
    if not isinstance(obj, dict):
        raise SyntheticMarkingError("expected dict")
    if obj.get("synthetic") is not True:
        raise SyntheticMarkingError("missing synthetic=True")
    if obj.get("marking") != SYNTHETIC_MARK:
        raise SyntheticMarkingError("missing [SYNTHETIC]")


def require_synthetic(data) -> None:
    text = data if isinstance(data, str) else str(data)
    if SYNTHETIC_MARK not in text:
        raise SyntheticMarkingError("missing [SYNTHETIC]")


class Sandbox:
    """파일 경로 격리 — production/ 탈출 차단 + sandbox 트리 내로만 resolve.

    sqlite_db.open_sandboxed 가 sandbox.path(relpath) 로 사용한다.
    B-1 에서 헤르메스 HERMES_HOME 격리와 통합한다.

    원본 전체 사양은 betplay vvs-platform/ai_pm/sandbox.py.
    여기서는 핸드오프에 명시된 계약(탈출 차단 + 트리 내 resolve)만 구현한다.
    """

    def __init__(self, root: str | Path):
        # sandbox 트리 베이스. 절대 경로로 고정한다.
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, relpath: str | Path) -> Path:
        """relpath 를 sandbox 트리 내부 경로로 resolve. 탈출 시 차단."""
        rel = Path(relpath)
        if rel.is_absolute():
            raise SandboxEscapeError(
                f"absolute path not allowed inside sandbox: {relpath!r}"
            )
        resolved = (self.root / rel).resolve()
        # production/ 탈출 등 sandbox 트리 밖으로의 이탈 차단
        if resolved != self.root and self.root not in resolved.parents:
            raise SandboxEscapeError(
                f"path escapes sandbox tree: {relpath!r} -> {resolved}"
            )
        return resolved
