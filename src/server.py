"""
server.py — FastAPI webhook server that runs the qualification decision live.

This turns the pattern from "reference code" into a real, callable service. Point
your voice platform's webhook at POST /v1/qualify and it returns the routing,
scoring, tier, and actions for the caller in real time.

Endpoints:
    GET  /health      -> liveness/readiness probe
    GET  /metrics     -> Prometheus metrics
    POST /v1/qualify  -> run the decision pipeline on a caller payload

Run locally:
    uvicorn server:app --reload --app-dir src
    # then: curl -X POST localhost:8000/v1/qualify -H 'content-type: application/json' \
    #         -d '{"signals": {"intent_clarity": 1, "fit_threshold": 1, "timeline": 1, "decision_power": 1}}'
"""

from __future__ import annotations

from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

import os

from models import Caller, Decision, CallOutcomeEvent, Route, Tier
from router import Caller as RouterCaller, handle
from logging_utils import get_logger, log_event
from analytics_sink import MemorySink, SQLiteSink

app = FastAPI(
    title="Voice AI Qualification Engine",
    description="Live decision endpoint for inbound voice-AI qualification.",
    version="1.0.0",
)
log = get_logger("voice_ai.server")

# ---- Prometheus metrics ----------------------------------------------------
CALLS = Counter("vaq_calls_total", "Total qualification calls", ["route", "tier"])
ALERTS = Counter("vaq_human_alerts_total", "High-intent human alerts fired")
SCORE_HIST = Histogram("vaq_score", "Distribution of qualification scores",
                       buckets=[0, 20, 50, 80, 100])

# Pluggable analytics sink: set VAQ_DB for durable SQLite, else in-memory.
_db = os.environ.get("VAQ_DB")
_SINK = SQLiteSink(_db) if _db else MemorySink()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "voice-ai-qualification", "version": "1.0.0"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/qualify", response_model=Decision)
def qualify(caller: Caller) -> Decision:
    # Bridge the typed Caller into the reference router's dataclass.
    rc = RouterCaller(
        name=caller.name,
        phone=caller.phone,
        company=caller.company,
        is_returning_client=caller.is_returning_client,
        is_partner=caller.is_partner,
        wants_secondary=caller.wants_secondary,
        signals=caller.signals.model_dump(),
    )
    result = handle(rc)

    decision = Decision(
        route=Route(result["route"]),
        score=result.get("score"),
        tier=Tier(result["tier"]) if result.get("tier") else None,
        actions=result.get("actions", []),
        alert_human=result.get("alert_human", False),
    )

    # Metrics + structured (redacted) log + analytics event.
    CALLS.labels(route=decision.route.value,
                 tier=decision.tier.value if decision.tier else "none").inc()
    if decision.score is not None:
        SCORE_HIST.observe(decision.score)
    if decision.alert_human:
        ALERTS.inc()

    _SINK.record(CallOutcomeEvent(
        route=decision.route,
        tier=decision.tier,
        score=decision.score,
        booked="book" in decision.actions,
        alerted_human=decision.alert_human,
        caller_company=caller.company or None,
    ))
    log_event(log, "qualify", route=decision.route.value,
              tier=decision.tier.value if decision.tier else None,
              score=decision.score, phone=caller.phone, name=caller.name)

    return decision


@app.get("/v1/analytics")
def analytics_summary() -> dict:
    from analytics import summarize
    return summarize(_SINK.all_events())
