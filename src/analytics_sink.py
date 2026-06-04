"""
analytics_sink.py — Pluggable analytics sinks for call-outcome events.

Provides a Protocol-based AnalyticsSink interface and two implementations:
  - MemorySink: in-memory list (great for tests and demos)
  - SQLiteSink: durable SQLite-backed storage (stdlib only, no extra deps)
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Protocol

from models import CallOutcomeEvent, Route, Tier


class AnalyticsSink(Protocol):
    def record(self, event: CallOutcomeEvent) -> None: ...
    def all_events(self) -> list[CallOutcomeEvent]: ...


class MemorySink:
    """Stores events in a plain list — fast, ephemeral, zero dependencies."""

    def __init__(self) -> None:
        self._events: list[CallOutcomeEvent] = []

    def record(self, event: CallOutcomeEvent) -> None:
        self._events.append(event)

    def all_events(self) -> list[CallOutcomeEvent]:
        return list(self._events)


class SQLiteSink:
    """Persists events to a SQLite database (stdlib sqlite3 only)."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS call_events (
                timestamp     TEXT    NOT NULL,
                route         TEXT    NOT NULL,
                tier          TEXT,
                score         INTEGER,
                booked        INTEGER NOT NULL,
                alerted_human INTEGER NOT NULL,
                caller_company TEXT
            )
            """
        )
        self._conn.commit()

    def record(self, event: CallOutcomeEvent) -> None:
        self._conn.execute(
            """
            INSERT INTO call_events
                (timestamp, route, tier, score, booked, alerted_human, caller_company)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.timestamp.isoformat(),
                event.route if isinstance(event.route, str) else event.route.value,
                event.tier if isinstance(event.tier, str) else (event.tier.value if event.tier else None),
                event.score,
                int(event.booked),
                int(event.alerted_human),
                event.caller_company,
            ),
        )
        self._conn.commit()

    def all_events(self) -> list[CallOutcomeEvent]:
        rows = self._conn.execute(
            "SELECT timestamp, route, tier, score, booked, alerted_human, caller_company FROM call_events"
        ).fetchall()
        events: list[CallOutcomeEvent] = []
        for ts, route, tier, score, booked, alerted_human, company in rows:
            events.append(
                CallOutcomeEvent(
                    timestamp=datetime.fromisoformat(ts),
                    route=Route(route),
                    tier=Tier(tier) if tier else None,
                    score=score,
                    booked=bool(booked),
                    alerted_human=bool(alerted_human),
                    caller_company=company,
                )
            )
        return events
