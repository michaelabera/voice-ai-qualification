"""
analytics.py — Aggregate call-outcome events into business metrics.

Consumes CallOutcomeEvent records and produces the numbers a business owner
actually cares about: how calls distribute across tiers, conversion (booking)
rate per tier, and human-alert volume. Pure functions, no external dependencies
beyond the models — easy to test, easy to wire to any sink.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Iterable

from models import CallOutcomeEvent


def summarize(events: Iterable[CallOutcomeEvent]) -> dict:
    events = list(events)
    if not events:
        return {"total_calls": 0}

    by_tier: Counter = Counter()
    by_route: Counter = Counter()
    bookings_by_tier: dict = defaultdict(int)
    scores: list[int] = []
    alerts = 0
    bookings = 0

    for e in events:
        tier = e.tier if isinstance(e.tier, str) else (e.tier.value if e.tier else "untiered")
        route = e.route if isinstance(e.route, str) else e.route.value
        by_tier[tier] += 1
        by_route[route] += 1
        if e.score is not None:
            scores.append(e.score)
        if e.alerted_human:
            alerts += 1
        if e.booked:
            bookings += 1
            bookings_by_tier[tier] += 1

    conversion_by_tier = {
        tier: round(bookings_by_tier[tier] / count, 3)
        for tier, count in by_tier.items()
    }

    return {
        "total_calls": len(events),
        "bookings": bookings,
        "overall_conversion": round(bookings / len(events), 3),
        "human_alerts": alerts,
        "avg_score": round(mean(scores), 1) if scores else None,
        "calls_by_tier": dict(by_tier),
        "calls_by_route": dict(by_route),
        "conversion_by_tier": conversion_by_tier,
    }


def _demo() -> None:
    import json
    from models import Route, Tier

    sample = [
        CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T1, score=92, booked=True, alerted_human=True),
        CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T2, score=64, booked=True),
        CallOutcomeEvent(route=Route.PRIMARY, tier=Tier.T3, score=33, booked=False),
        CallOutcomeEvent(route=Route.SECONDARY, tier=Tier.T2, score=55, booked=False),
        CallOutcomeEvent(route=Route.TRIAGE, tier=Tier.T4, score=10, booked=False),
        CallOutcomeEvent(route=Route.RETURNING, booked=True),
    ]
    print(json.dumps(summarize(sample), indent=2))


if __name__ == "__main__":
    import argparse, sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    parser = argparse.ArgumentParser(description="Call analytics summarizer.")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        _demo()
    else:
        print("Use --demo to see an aggregated summary.")
