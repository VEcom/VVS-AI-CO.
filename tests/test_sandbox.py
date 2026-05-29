"""ai_pm/sandbox.py 단위 검증 — B-0 토대 모듈.

절대선 #2(격리)·합성 검증·경로 탈출 차단의 핵심 계약을 검증한다.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_pm.sandbox import (  # noqa: E402
    SYNTHETIC_MARK,
    ExternalSendBlocked,
    InvalidIdentifierError,
    Sandbox,
    SandboxEscapeError,
    SyntheticMarkingError,
    assert_invalid_identifier,
    has_production_access,
    is_obviously_invalid,
    no_external_send,
    require_synthetic,
    validate_synthetic,
)


def test_no_production_access():
    # 절대선 — Phase 0 production 절대 미접근
    assert has_production_access() is False


def test_no_external_send_blocked():
    # 절대선 #2 — 외부 발송 차단
    with pytest.raises(ExternalSendBlocked):
        no_external_send("anything")


def test_invalid_identifier_detection():
    assert is_obviously_invalid("000-00") is True
    assert is_obviously_invalid("---") is True
    assert is_obviously_invalid("") is False
    assert is_obviously_invalid("123-45") is False


def test_assert_invalid_identifier():
    assert_invalid_identifier("000-00")  # 통과
    with pytest.raises(InvalidIdentifierError):
        assert_invalid_identifier("123-45")


def test_validate_synthetic_ok():
    validate_synthetic({"synthetic": True, "marking": SYNTHETIC_MARK})


@pytest.mark.parametrize(
    "obj",
    [
        "not a dict",
        {"synthetic": False, "marking": SYNTHETIC_MARK},
        {"synthetic": True},
        {"synthetic": True, "marking": "nope"},
    ],
)
def test_validate_synthetic_rejects(obj):
    with pytest.raises(SyntheticMarkingError):
        validate_synthetic(obj)


def test_require_synthetic():
    require_synthetic(f"some text {SYNTHETIC_MARK} here")
    with pytest.raises(SyntheticMarkingError):
        require_synthetic("no marking here")


def test_sandbox_path_within_tree(tmp_path):
    sb = Sandbox(tmp_path / "sbx")
    p = sb.path("a/b/c.txt")
    assert sb.root in p.parents


def test_sandbox_blocks_absolute(tmp_path):
    sb = Sandbox(tmp_path / "sbx")
    with pytest.raises(SandboxEscapeError):
        sb.path("/etc/passwd")


def test_sandbox_blocks_escape(tmp_path):
    sb = Sandbox(tmp_path / "sbx")
    with pytest.raises(SandboxEscapeError):
        sb.path("../../etc/passwd")
