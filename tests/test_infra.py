"""인프라 9개 단위테스트.

sqlite_db · pattern_db · token_cost_monitor · quote_gp_calculator ·
icp_screener · scope_freeze_checker · privacy_data_gatekeeper ·
delivery_start_gate · incident_logger.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_pm import (  # noqa: E402
    delivery_start_gate,
    icp_screener,
    incident_logger,
    pattern_db,
    privacy_data_gatekeeper,
    quote_gp_calculator,
    scope_freeze_checker,
    sqlite_db,
    token_cost_monitor,
)
from ai_pm.sandbox import SandboxEscapeError  # noqa: E402


@pytest.fixture
def conn(tmp_path):
    c = sqlite_db.open_sandboxed("test.db", sandbox_root=str(tmp_path))
    sqlite_db.init_schema(c)
    yield c
    c.close()


# ── sqlite_db ──
def test_sqlite_schema(conn):
    tables = {
        r["name"]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"documents", "patterns", "incidents"} <= tables


def test_sqlite_escape_blocked(tmp_path):
    with pytest.raises(SandboxEscapeError):
        sqlite_db.open_sandboxed("../../evil.db", sandbox_root=str(tmp_path))


# ── pattern_db ──
def test_pattern_save_find(conn):
    pid = pattern_db.save_pattern(
        conn, {"doc_type": "견적서", "pattern": {"blocks": ["header"]}, "score": 90}
    )
    assert pid > 0
    found = pattern_db.find_patterns(conn, "견적서")
    assert len(found) == 1 and found[0]["pattern"]["blocks"] == ["header"]


def test_pattern_requires_doc_type(conn):
    with pytest.raises(ValueError):
        pattern_db.save_pattern(conn, {"pattern": {}})


# ── token_cost_monitor ──
def test_token_track():
    token_cost_monitor.reset()
    token_cost_monitor.track(1000, "gpt-4")
    total = token_cost_monitor.get_total()
    assert total["tokens"] == 1000 and total["cost_usd"] == 0.03


# ── quote_gp_calculator ──
def test_gp_positive():
    r = quote_gp_calculator.calc_gp(cost=70, price=100)
    assert r["gp_amount"] == 30 and r["gp_rate"] == 0.3 and r["warning"] is None


def test_gp_negative_warns():
    r = quote_gp_calculator.calc_gp(cost=120, price=100)
    assert r["gp_amount"] == -20 and r["warning"]


def test_gp_zero_price():
    with pytest.raises(ValueError):
        quote_gp_calculator.calc_gp(cost=1, price=0)


# ── icp_screener ──
def test_icp_match():
    r = icp_screener.screen(
        {"industry": "반도체", "is_supplier": True, "employees": 120, "certs": ["ISO9001"]}
    )
    assert r["is_icp"] is True and r["score"] == 100


def test_icp_no_match():
    r = icp_screener.screen({"industry": "요식업", "employees": 3})
    assert r["is_icp"] is False


# ── scope_freeze_checker ──
def test_scope_frozen():
    r = scope_freeze_checker.check_scope({"a": 1}, {"a": 1})
    assert r["frozen"] is True and r["changes"] == []


def test_scope_changed():
    r = scope_freeze_checker.check_scope({"a": 1, "b": 2}, {"a": 9, "c": 3})
    types = {c["type"] for c in r["changes"]}
    assert r["frozen"] is False and types == {"modified", "removed", "added"}


# ── privacy_data_gatekeeper ──
def test_pii_detect():
    r = privacy_data_gatekeeper.scan("연락처 010-1234-5678, a@b.com, 900101-1234567")
    assert r["has_pii"] is True
    assert set(r["types"]) == {"phone", "email", "rrn"}


def test_pii_clean():
    assert privacy_data_gatekeeper.scan("개인정보 없는 문장")["has_pii"] is False


# ── delivery_start_gate ──
def test_gate_blocked():
    r = delivery_start_gate.can_start({"scope_frozen": True})
    assert r["can_start"] is False and "legal_cleared" in r["blockers"]


def test_gate_open():
    r = delivery_start_gate.can_start(
        {
            "scope_frozen": True,
            "legal_cleared": True,
            "absolute_line_passed": True,
            "customer_approved": True,
        }
    )
    assert r["can_start"] is True and r["blockers"] == []


# ── incident_logger ──
def test_incident_log_get(conn):
    iid = incident_logger.log_incident(
        conn, {"kind": "absolute_line_violation", "detail": "banned: 절대", "severity": "high"}
    )
    assert iid > 0
    items = incident_logger.get_incidents(conn)
    assert len(items) == 1 and items[0]["kind"] == "absolute_line_violation"


def test_incident_requires_kind(conn):
    with pytest.raises(ValueError):
        incident_logger.log_incident(conn, {"detail": "x"})
