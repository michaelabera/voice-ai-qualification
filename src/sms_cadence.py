"""
sms_cadence.py — Follow-up cadence engine for the qualification flow.

Implements the 0h -> 24h -> 72h follow-up sequence with exit conditions, mirroring
the `sms` block in config/agent_config.yaml. Framework-agnostic: it produces the
scheduled messages and exit logic; wire `send()` to your messaging provider.

Run a demo:
    python src/sms_cadence.py --demo
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class CadenceStep:
    offset_hours: int
    template_key: str
    only_if_no_booking: bool = False
    optional: bool = False


CADENCE = [
    CadenceStep(0, "immediate", only_if_no_booking=False),
    CadenceStep(24, "followup_24h", only_if_no_booking=True),
    CadenceStep(72, "followup_72h", only_if_no_booking=True, optional=True),
]

TEMPLATES = {
    "immediate": (
        "Hi {name}, this is {agent} at {company}.\n"
        "📅 Schedule your {length}-minute call: {calendar}\n"
        "🎥 Quick overview: {video}\n"
        "Looking forward to connecting you."
    ),
    "followup_24h": (
        "Hi {name}, just checking in from {company}. Whenever you're ready, "
        "you can schedule here: {calendar}. No rush."
    ),
    "followup_72h": (
        "Hey {name}, wanted to make sure this didn't slip through. A few "
        "openings are available this week: {calendar}"
    ),
}


def plan_cadence(booking_confirmed: bool, include_optional: bool = True) -> list[CadenceStep]:
    """Return the steps that should fire given booking state."""
    steps = []
    for step in CADENCE:
        if step.optional and not include_optional:
            continue
        if step.only_if_no_booking and booking_confirmed:
            continue
        steps.append(step)
    return steps


def render(template_key: str, ctx: dict) -> str:
    return TEMPLATES[template_key].format(**ctx)


def _demo() -> None:
    ctx = {
        "name": "Jordan",
        "agent": "{{AGENT_NAME}}",
        "company": "{{COMPANY_NAME}}",
        "length": "15",
        "calendar": "{{CALENDAR_LINK}}",
        "video": "{{OVERVIEW_VIDEO_LINK}}",
    }
    for booked in (False, True):
        label = "BOOKED" if booked else "NOT BOOKED"
        print(f"\n=== Cadence when {label} ===")
        for step in plan_cadence(booking_confirmed=booked):
            print(f"\n[+{step.offset_hours}h]")
            print(render(step.template_key, ctx))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMS follow-up cadence engine (reference).")
    parser.add_argument("--demo", action="store_true", help="Print the cadence for booked vs not-booked.")
    args = parser.parse_args()
    if args.demo:
        _demo()
    else:
        print("Use --demo to see the cadence in action.")
