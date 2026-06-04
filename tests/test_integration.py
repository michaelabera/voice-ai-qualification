"""Integration tests for analytics sinks and the full FastAPI qualification flow."""

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics_sink import MemorySink, SQLiteSink  # noqa: E402
from models import CallOutcomeEvent, Route, Tier  # noqa: E402


# ---- MemorySink -------------------------------------------------------------

def test_memory_sink_records_events():
    sink = MemorySink()
    ev = CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T1, score=90, booked=True)
    sink.record(ev)
    sink.record(CallOutcomeEvent(route=Route.TRIAGE))
    assert len(sink.all_events()) == 2
    assert sink.all_events()[0].score == 90


# ---- SQLiteSink persistence --------------------------------------------------

def test_sqlite_sink_persists_across_restart(tmp_path):
    db = str(tmp_path / "test.db")
    sink1 = SQLiteSink(db)
    sink1.record(CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T2, score=55, booked=True))
    sink1.record(CallOutcomeEvent(route=Route.TRIAGE, tier=Tier.T4, score=10))
    assert len(sink1.all_events()) == 2

    # Simulate restart: new instance, same file.
    sink2 = SQLiteSink(db)
    events = sink2.all_events()
    assert len(events) == 2
    assert events[0].route == "A_primary_service"
    assert events[1].score == 10


# ---- Field round-trip --------------------------------------------------------

def test_sqlite_sink_field_roundtrip(tmp_path):
    db = str(tmp_path / "rt.db")
    ts = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    original = CallOutcomeEvent(
        timestamp=ts,
        route=Route.PARTNER,
        tier=Tier.T3,
        score=42,
        booked=False,
        alerted_human=True,
        caller_company="Acme Corp",
    )
    sink = SQLiteSink(db)
    sink.record(original)
    restored = sink.all_events()[0]

    assert restored.timestamp == ts
    assert restored.route == "C_partner_program"
    assert restored.tier == "tier_3_nurture"
    assert restored.score == 42
    assert restored.booked is False
    assert restored.alerted_human is True
    assert restored.caller_company == "Acme Corp"


# ---- Full FastAPI flow -------------------------------------------------------

def test_qualify_increments_analytics(monkeypatch):
    """POST /v1/qualify should make /v1/analytics total_calls go up."""
    # Isolate the sink so the test doesn't leak into other tests.
    monkeypatch.delenv("VAQ_DB", raising=False)

    # Re-import server with a fresh MemorySink.
    import importlib
    import server as srv
    srv._SINK = MemorySink()

    from fastapi.testclient import TestClient

    client = TestClient(srv.app)

    # Baseline
    resp = client.get("/v1/analytics")
    assert resp.status_code == 200
    assert resp.json()["total_calls"] == 0

    # Qualify one call
    payload = {
        "signals": {
            "intent_clarity": 1.0,
            "fit_threshold": 1.0,
            "timeline": 1.0,
            "decision_power": 1.0,
        }
    }
    resp = client.post("/v1/qualify", json=payload)
    assert resp.status_code == 200

    # Analytics should reflect the new call
    resp = client.get("/v1/analytics")
    assert resp.status_code == 200
    assert resp.json()["total_calls"] == 1
