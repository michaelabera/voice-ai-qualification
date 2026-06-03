"""Tests for the qualification router, scorer, and SMS cadence."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from router import Caller, Route, handle, route_call, score, tier_for  # noqa: E402
from sms_cadence import plan_cadence, render  # noqa: E402


# ---- routing ---------------------------------------------------------------

def test_returning_client_is_fast_pathed_before_qualification():
    c = Caller(is_returning_client=True, signals={"intent_clarity": 1.0})
    assert route_call(c) is Route.RETURNING
    result = handle(c)
    assert result["score"] is None
    assert "fast_path_human" in result["actions"]


def test_partner_routes_to_partner_track():
    c = Caller(is_partner=True)
    assert route_call(c) is Route.PARTNER
    assert "capture_partner" in handle(c)["actions"]


def test_secondary_service_route():
    assert route_call(Caller(wants_secondary=True)) is Route.SECONDARY


def test_buying_intent_routes_to_primary():
    assert route_call(Caller(signals={"intent_clarity": 0.5})) is Route.PRIMARY


def test_unclear_intent_falls_to_triage():
    assert route_call(Caller()) is Route.TRIAGE


# ---- scoring ---------------------------------------------------------------

def test_score_is_bounded_0_to_100():
    perfect = Caller(signals={k: 1.0 for k in ["intent_clarity", "fit_threshold", "timeline", "decision_power"]})
    assert score(perfect) == 100
    assert score(Caller()) == 0


def test_score_clamps_out_of_range_signals():
    c = Caller(signals={"intent_clarity": 5.0, "fit_threshold": -2.0})
    assert 0 <= score(c) <= 100


@pytest.mark.parametrize(
    "points,expected_tier",
    [(100, "tier_1_high_intent"), (80, "tier_1_high_intent"),
     (79, "tier_2_qualified"), (50, "tier_2_qualified"),
     (49, "tier_3_nurture"), (20, "tier_3_nurture"),
     (19, "tier_4_capture"), (0, "tier_4_capture")],
)
def test_tier_thresholds(points, expected_tier):
    assert tier_for(points)[0] == expected_tier


# ---- end-to-end actions ----------------------------------------------------

def test_high_intent_fires_human_alert():
    c = Caller(signals={k: 1.0 for k in ["intent_clarity", "fit_threshold", "timeline", "decision_power"]})
    result = handle(c)
    assert result["alert_human"] is True
    assert "alert_human" in result["actions"]


def test_no_caller_is_a_dead_end_sms_always_present():
    # Even the lowest-scoring caller still gets an SMS.
    result = handle(Caller())
    joined = " ".join(result["actions"])
    assert "sms" in joined


# ---- cadence ---------------------------------------------------------------

def test_cadence_full_when_not_booked():
    steps = plan_cadence(booking_confirmed=False)
    offsets = [s.offset_hours for s in steps]
    assert offsets == [0, 24, 72]


def test_cadence_stops_followups_when_booked():
    steps = plan_cadence(booking_confirmed=True)
    offsets = [s.offset_hours for s in steps]
    assert offsets == [0]  # only the immediate confirmation goes out


def test_optional_72h_can_be_excluded():
    steps = plan_cadence(booking_confirmed=False, include_optional=False)
    offsets = [s.offset_hours for s in steps]
    assert offsets == [0, 24]


def test_render_fills_placeholders():
    msg = render("followup_24h", {"name": "Jordan", "company": "Acme", "calendar": "X"})
    assert "Jordan" in msg and "Acme" in msg


# ---- schema integrity ------------------------------------------------------

def test_schema_is_valid_json_and_has_four_tiers():
    schema_path = Path(__file__).resolve().parents[1] / "config" / "qualification_schema.json"
    data = json.loads(schema_path.read_text())
    tiers = data["properties"]["tiers"]["properties"]
    assert len(tiers) == 4
