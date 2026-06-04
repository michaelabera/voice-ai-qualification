"""
vapi_webhook.py — Example: wiring Vapi (a voice AI platform) to the qualifier.

This shows the one piece a real deployment has to build: translating a voice
platform's webhook payload into the Caller shape this system expects, calling
the decision engine, and turning the result into instructions the platform can
act on. Vapi is the example; Retell, Bland, and Twilio follow the same shape.

Run it:
    uvicorn vapi_webhook:app --port 8001
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from router import Caller, handle

app = FastAPI(title="Vapi to Qualifier example")


def signals_from_vapi(payload: dict) -> dict:
    """Translate a Vapi webhook payload into the 0.0-1.0 signals the scorer uses.

    THIS is the real integration work. The voice platform gives you a transcript
    and structured fields; you decide how to turn those into the four signals.
    """
    data = (payload.get("message", {})
                   .get("analysis", {})
                   .get("structuredData", {})) or {}
    return {
        "intent_clarity": float(data.get("intent_clarity", 0.0)),
        "fit_threshold": float(data.get("fit", 0.0)),
        "timeline": float(data.get("timeline", 0.0)),
        "decision_power": float(data.get("decision_power", 0.0)),
    }


def caller_from_vapi(payload: dict) -> Caller:
    """Build a Caller from a Vapi payload, including who the caller is."""
    customer = (payload.get("message", {}).get("customer", {})) or {}
    return Caller(
        name=customer.get("name", ""),
        phone=customer.get("number", ""),
        signals=signals_from_vapi(payload),
    )


@app.post("/vapi/webhook")
async def vapi_webhook(request: Request) -> dict:
    """Receive a Vapi webhook, qualify the caller, return what to do next."""
    payload = await request.json()
    caller = caller_from_vapi(payload)
    decision = handle(caller)
    return {
        "route": decision["route"],
        "tier": decision.get("tier"),
        "actions": decision.get("actions", []),
        "alert_human": decision.get("alert_human", False),
        "say": _say_for(decision),
    }


def _say_for(decision: dict) -> str:
    """Map a decision to what the agent should say."""
    if decision.get("alert_human"):
        return "You're a great fit. I'm connecting you with someone right now."
    if "book" in decision.get("actions", []):
        return "I'd love to get you on the calendar. I'll text you a link now."
    return "Thanks for calling. I'll send you some information by text."


if __name__ == "__main__":
    import json
    sample = {
        "message": {
            "customer": {"name": "Jordan", "number": "+15555550123"},
            "analysis": {"structuredData": {
                "intent_clarity": 1.0, "fit": 0.9, "timeline": 0.8, "decision_power": 1.0
            }},
        }
    }
    caller = caller_from_vapi(sample)
    print("Mapped caller signals:", caller.signals)
    print("Decision:", json.dumps(handle(caller), indent=2))
