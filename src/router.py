"""
router.py — Reference implementation of the intent router and qualification scorer.

This is a framework-agnostic reference for the logic described in
config/agent_config.yaml and config/qualification_schema.json. It is not wired
to any telephony provider; it demonstrates the decision model so the routing and
scoring behavior is testable and transparent.

Run a demo:
    python src/router.py --demo
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Route(str, Enum):
    PRIMARY = "A_primary_service"
    SECONDARY = "B_secondary_service"
    PARTNER = "C_partner_program"
    RETURNING = "D_returning_client"
    TRIAGE = "E_other_triage"


# Tier thresholds mirror config/qualification_schema.json.
TIERS = [
    (80, "tier_1_high_intent", "alert_human + book + sms"),
    (50, "tier_2_qualified", "book + sms"),
    (20, "tier_3_nurture", "capture + sms_nurture"),
    (0, "tier_4_capture", "capture_only"),
]

# Criterion weights mirror the schema. Each scorer returns 0.0–1.0; the weighted
# sum produces a 0–100 score.
WEIGHTS = {
    "intent_clarity": 25,
    "fit_threshold": 30,
    "timeline": 25,
    "decision_power": 20,
}


@dataclass
class Caller:
    name: str = ""
    phone: str = ""
    company: str = ""
    is_returning_client: bool = False
    is_partner: bool = False
    wants_secondary: bool = False
    # Raw 0.0–1.0 signals captured during the call.
    signals: dict = field(default_factory=dict)


def route_call(caller: Caller) -> Route:
    """Five-way intent router. Order matters: returning clients and partners
    are fast-pathed before buyer qualification."""
    if caller.is_returning_client:
        return Route.RETURNING
    if caller.is_partner:
        return Route.PARTNER
    if caller.wants_secondary:
        return Route.SECONDARY
    if caller.signals.get("intent_clarity", 0) > 0:
        return Route.PRIMARY
    return Route.TRIAGE


def score(caller: Caller) -> int:
    """Weighted qualification score, 0–100."""
    total = 0.0
    for criterion, weight in WEIGHTS.items():
        signal = max(0.0, min(1.0, caller.signals.get(criterion, 0.0)))
        total += signal * weight
    return round(total)


def tier_for(points: int) -> tuple[str, str]:
    for threshold, name, action in TIERS:
        if points >= threshold:
            return name, action
    return TIERS[-1][1], TIERS[-1][2]


def handle(caller: Caller) -> dict:
    """Full decision: route -> score -> tier -> actions."""
    route = route_call(caller)

    # Returning clients and partners skip standard scoring.
    if route in (Route.RETURNING, Route.PARTNER):
        return {
            "route": route.value,
            "score": None,
            "tier": None,
            "actions": ["fast_path_human", "sms"]
            if route is Route.RETURNING
            else ["capture_partner", "partner_followup"],
        }

    points = score(caller)
    tier_name, action = tier_for(points)
    actions = action.split(" + ")

    # No caller is ever a dead end: SMS always fires.
    if "sms" not in " ".join(actions) and "sms_nurture" not in actions:
        actions.append("sms")

    return {
        "route": route.value,
        "score": points,
        "tier": tier_name,
        "actions": actions,
        "alert_human": tier_name == "tier_1_high_intent",
    }


def _demo() -> None:
    samples = [
        Caller(name="High Intent", signals={"intent_clarity": 1.0, "fit_threshold": 1.0, "timeline": 0.9, "decision_power": 1.0}),
        Caller(name="Qualified", signals={"intent_clarity": 0.8, "fit_threshold": 0.6, "timeline": 0.4, "decision_power": 0.6}),
        Caller(name="Nurture", signals={"intent_clarity": 0.5, "fit_threshold": 0.3, "timeline": 0.1, "decision_power": 0.3}),
        Caller(name="Returning", is_returning_client=True),
        Caller(name="Partner", is_partner=True),
        Caller(name="Unclear"),
    ]
    for c in samples:
        result = handle(c)
        print(f"{c.name:14} -> {json.dumps(result)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice AI qualification router (reference).")
    parser.add_argument("--demo", action="store_true", help="Run a demo across sample callers.")
    args = parser.parse_args()
    if args.demo:
        _demo()
    else:
        print("Use --demo to see the router and scorer in action.")
