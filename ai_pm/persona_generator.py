"""ai_pm/persona_generator.py — 합성 페르소나 생성 (invariant 가드 포함).

학습(B-4) 준비용 합성 페르소나를 생성한다. 모든 산출물은 합성(sandbox 계약)
이며, 시간 관련 invariant 가드를 강제한다:

  - 0-based _ym: 월 인덱스는 0~11 (0=1월). 범위 밖이면 거부.
  - 날짜: 시작 < 종료 (같거나 역전 거부).
  - 미래 차단: 종료가 기준일(today) 이후면 거부.

페르소나 식별자는 무효(전부 0/-)여야 한다(sandbox.assert_invalid_identifier).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .sandbox import (
    SYNTHETIC_MARK,
    assert_invalid_identifier,
    validate_synthetic,
)


class PersonaInvariantError(ValueError):
    """페르소나 시간 invariant 위반."""


def _check_ym(ym: int) -> None:
    """0-based 월 인덱스 검증 (0~11)."""
    if not isinstance(ym, int) or isinstance(ym, bool):
        raise PersonaInvariantError(f"_ym must be int, got {ym!r}")
    if ym < 0 or ym > 11:
        raise PersonaInvariantError(f"_ym must be 0-based 0..11, got {ym}")


def _check_date_window(start: date, end: date, *, today: date | None = None) -> None:
    """시작<종료 + 미래 차단."""
    if not isinstance(start, date) or not isinstance(end, date):
        raise PersonaInvariantError("start/end must be date objects")
    if not (start < end):
        raise PersonaInvariantError(f"start must be < end (start={start}, end={end})")
    today = today or date.today()
    if end > today:
        raise PersonaInvariantError(f"end must not be in the future (end={end}, today={today})")


@dataclass
class Persona:
    """합성 페르소나. 항상 synthetic=True + [SYNTHETIC] 마킹."""

    name: str
    identifier: str            # 무효 식별자(전부 0/-)
    start: date
    end: date
    ym: int                    # 0-based 월 인덱스
    synthetic: bool = True
    marking: str = SYNTHETIC_MARK
    attrs: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "identifier": self.identifier,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "ym": self.ym,
            "synthetic": self.synthetic,
            "marking": self.marking,
            "attrs": dict(self.attrs),
        }


def generate_persona(
    *,
    name: str,
    identifier: str,
    start: date,
    end: date,
    ym: int,
    today: date | None = None,
    attrs: dict | None = None,
) -> Persona:
    """invariant 가드를 모두 통과한 합성 페르소나를 생성한다.

    위반 시 PersonaInvariantError(시간) 또는 InvalidIdentifierError(식별자)/
    SyntheticMarkingError(합성) 를 던진다.
    """
    # 시간 invariant
    _check_ym(ym)
    _check_date_window(start, end, today=today)

    # 식별자는 무효(합성)여야 함
    assert_invalid_identifier(identifier)

    persona = Persona(
        name=name,
        identifier=identifier,
        start=start,
        end=end,
        ym=ym,
        attrs=dict(attrs or {}),
    )

    # 합성 계약 재확인 (synthetic=True + [SYNTHETIC])
    validate_synthetic(persona.as_dict())
    return persona
