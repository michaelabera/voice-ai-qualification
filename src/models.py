"""
models.py — Type-safe data models for the qualification engine (Pydantic v2).

These models are the single source of truth for the shapes that flow through the
system: a caller, the qualification signals, the routing/scoring result, and a
standardized call-outcome event for analytics. Everything else types against them.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Route(str, Enum):
    PRIMARY = "A_primary_service"
    SECONDARY = "B_secondary_service"
    PARTNER = "C_partner_program"
    RETURNING = "D_returning_client"
    TRIAGE = "E_other_triage"


class Tier(str, Enum):
    T1 = "tier_1_high_intent"
    T2 = "tier_2_qualified"
    T3 = "tier_3_nurture"
    T4 = "tier_4_capture"


class Signals(BaseModel):
    """Real-time 0.0-1.0 signals captured during the call. Values are clamped."""
    intent_clarity: float = 0.0
    fit_threshold: float = 0.0
    timeline: float = 0.0
    decision_power: float = 0.0

    @field_validator("*", mode="before")
    @classmethod
    def _clamp(cls, v: float) -> float:
        try:
            v = float(v)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, v))


class Caller(BaseModel):
    """An inbound caller. PII fields are optional and redaction-aware."""
    name: str = ""
    phone: str = ""
    company: str = ""
    is_returning_client: bool = False
    is_partner: bool = False
    wants_secondary: bool = False
    signals: Signals = Field(default_factory=Signals)


class Decision(BaseModel):
    """The output of the routing + scoring pipeline."""
    route: Route
    score: Optional[int] = None
    tier: Optional[Tier] = None
    actions: list[str] = Field(default_factory=list)
    alert_human: bool = False


class CallOutcomeEvent(BaseModel):
    """Standardized analytics event emitted once per handled call.

    Contains NO raw PII by default — only hashed/derived fields — so it is safe
    to ship to an analytics sink. Set include_pii=True only for trusted internal use.
    """
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    route: Route
    tier: Optional[Tier] = None
    score: Optional[int] = None
    booked: bool = False
    alerted_human: bool = False
    caller_company: Optional[str] = None  # non-PII, useful for B2B analytics

    model_config = {"use_enum_values": True}
