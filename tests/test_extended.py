"""Tests for the extended modules: models, server, analytics, validation,
presets, A/B harness, and logging redaction."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from models import Caller, Signals, CallOutcomeEvent, Route, Tier  # noqa: E402
from analytics import summarize  # noqa: E402
from ab_test import Variant, run_ab, score_with_weights  # noqa: E402
from router import Caller as RouterCaller  # noqa: E402
from logging_utils import redact, _redact_text  # noqa: E402
from validate_config import validate_yaml_config, validate_json_schema  # noqa: E402
import presets as presets_mod  # noqa: E402


# ---- models ----------------------------------------------------------------

def test_signals_clamp_out_of_range():
    s = Signals(intent_clarity=9.0, fit_threshold=-3.0)
    assert s.intent_clarity == 1.0
    assert s.fit_threshold == 0.0


def test_call_outcome_event_has_no_raw_pii_fields():
    e = CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T1, score=90)
    dumped = e.model_dump()
    assert "phone" not in dumped and "name" not in dumped


# ---- analytics -------------------------------------------------------------

def test_summarize_empty():
    assert summarize([])["total_calls"] == 0


def test_summarize_conversion_math():
    events = [
        CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T1, score=90, booked=True),
        CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T1, score=85, booked=False),
    ]
    out = summarize(events)
    assert out["total_calls"] == 2
    assert out["overall_conversion"] == 0.5
    assert out["conversion_by_tier"]["tier_1_high_intent"] == 0.5


# ---- A/B harness -----------------------------------------------------------

def test_ab_weights_change_distribution_predictably():
    callers = [RouterCaller(signals={"intent_clarity": 0.9, "fit_threshold": 0.9,
                                      "timeline": 0.1, "decision_power": 0.1})]
    a = Variant("a", {"intent_clarity": 25, "fit_threshold": 30, "timeline": 25, "decision_power": 20})
    b = Variant("b", {"intent_clarity": 40, "fit_threshold": 40, "timeline": 10, "decision_power": 10})
    out = run_ab(callers, a, b)
    assert "variant_a" in out and "variant_b" in out and "delta_b_minus_a" in out


def test_score_with_weights_bounds():
    c = RouterCaller(signals={"intent_clarity": 1, "fit_threshold": 1, "timeline": 1, "decision_power": 1})
    assert score_with_weights(c, {"intent_clarity": 25, "fit_threshold": 30, "timeline": 25, "decision_power": 20}) == 100


# ---- logging redaction -----------------------------------------------------

def test_redact_scrubs_pii_keys():
    out = redact({"name": "Jane", "phone": "555-123-4567", "score": 90})
    assert out["name"] == "[REDACTED]"
    assert out["phone"] == "[REDACTED]"
    assert out["score"] == 90


def test_redact_text_scrubs_email_and_phone():
    t = _redact_text("reach me at a@b.com or 555-867-5309")
    assert "[REDACTED_EMAIL]" in t and "[REDACTED_PHONE]" in t


# ---- config validation -----------------------------------------------------

def test_base_config_is_valid_nonstrict():
    errors = validate_yaml_config(ROOT / "config" / "agent_config.yaml", strict=False)
    assert errors == []


def test_base_config_flags_placeholders_in_strict():
    errors = validate_yaml_config(ROOT / "config" / "agent_config.yaml", strict=True)
    assert any("placeholder" in e.lower() for e in errors)


def test_schema_validates():
    assert validate_json_schema(ROOT / "config" / "qualification_schema.json") == []


# ---- presets ---------------------------------------------------------------

def test_presets_listed():
    names = presets_mod.list_presets()
    assert {"healthcare_intake", "real_estate", "home_services"}.issubset(set(names))


def test_preset_merge_applies_overlay():
    merged = presets_mod.load_merged("healthcare_intake")
    assert merged["vertical"] == "healthcare_intake"
    # base keys survive the merge
    assert "rules" in merged


def test_missing_preset_raises():
    with pytest.raises(FileNotFoundError):
        presets_mod.load_merged("nonexistent_vertical")


# ---- server (integration) --------------------------------------------------

def test_server_endpoints():
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)

    assert client.get("/health").json()["status"] == "ok"

    r = client.post("/v1/qualify", json={
        "signals": {"intent_clarity": 1, "fit_threshold": 1, "timeline": 1, "decision_power": 1}
    })
    body = r.json()
    assert body["tier"] == "tier_1_high_intent"
    assert body["alert_human"] is True

    assert "vaq_calls_total" in client.get("/metrics").text
    assert client.get("/v1/analytics").json()["total_calls"] >= 1
