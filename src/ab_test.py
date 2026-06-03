"""
ab_test.py — Compare two scoring-weight configurations on the same caller set.

Lets you answer "would shifting weight from intent toward timeline book more of
the right callers?" without guessing. Deterministic and offline: feed it callers
and two weight maps, get back tier distributions and a side-by-side diff.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from router import Caller, tier_for


def score_with_weights(caller: Caller, weights: dict[str, int]) -> int:
    total = 0.0
    for criterion, weight in weights.items():
        signal = max(0.0, min(1.0, caller.signals.get(criterion, 0.0)))
        total += signal * weight
    return round(total)


@dataclass
class Variant:
    name: str
    weights: dict[str, int]


def run_ab(callers: list[Caller], a: Variant, b: Variant) -> dict:
    def distribution(weights):
        tiers = Counter()
        for c in callers:
            # Returning clients / partners skip scoring; only score buyer routes.
            if c.is_returning_client or c.is_partner:
                continue
            tiers[tier_for(score_with_weights(c, weights))[0]] += 1
        return dict(tiers)

    dist_a = distribution(a.weights)
    dist_b = distribution(b.weights)
    all_tiers = set(dist_a) | set(dist_b)
    diff = {t: dist_b.get(t, 0) - dist_a.get(t, 0) for t in all_tiers}

    return {
        "variant_a": {"name": a.name, "distribution": dist_a},
        "variant_b": {"name": b.name, "distribution": dist_b},
        "delta_b_minus_a": diff,
    }


def _demo() -> None:
    import json
    import random

    random.seed(42)
    callers = [
        Caller(signals={
            "intent_clarity": random.random(),
            "fit_threshold": random.random(),
            "timeline": random.random(),
            "decision_power": random.random(),
        })
        for _ in range(200)
    ]
    control = Variant("control", {"intent_clarity": 25, "fit_threshold": 30, "timeline": 25, "decision_power": 20})
    timeline_heavy = Variant("timeline_heavy", {"intent_clarity": 20, "fit_threshold": 25, "timeline": 35, "decision_power": 20})
    print(json.dumps(run_ab(callers, control, timeline_heavy), indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="A/B test scoring weights.")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        _demo()
    else:
        print("Use --demo to compare two weight variants on synthetic callers.")
