# Architecture

This document explains *why* the system is built the way it is. The configuration
in `config/` is the *what*; this is the reasoning a recruiter, engineer, or
operator would want to see.

## The core problem

Inbound voice AI fails in predictable ways:

1. It treats every caller identically, reading a linear script.
2. It can't distinguish a high-value buyer from a tire-kicker.
3. It leaks business logic — telling callers things they shouldn't hear.
4. It loses the lead the moment the call ends.

Each design decision below targets one of these failures.

## Decision 1: Intent routing before qualification

A linear script assumes every caller wants the same thing. Real inbound traffic
is mixed: buyers, returning clients, partners, and people who dialed the wrong
intent. So the first thing the agent does is **route**, not pitch.

The router is ordered deliberately. Returning clients and partners are detected
*first*, because forcing a returning client through new-prospect qualification is
the fastest way to sound like a robot and lose trust. Only after those fast-paths
are ruled out does buyer qualification begin.

## Decision 2: Qualification as a gradient, not a gate

A binary "qualified / not qualified" gate throws away the 60% of callers who
aren't ready *today* but will be in 90 days. Instead, callers are scored on
weighted criteria and bucketed into four tiers, each with a different action.
The lowest tier still captures contact data. **No caller is a dead end.**

The weights live in `qualification_schema.json` so they can be tuned per vertical
without touching code.

## Decision 3: Internal context the agent never speaks

The agent needs to understand the business model to route intelligently — but the
caller should hear only the value to *them*. This is enforced with an
`internal_context` block flagged `visible_to_caller: false` and a hard rule in the
`rules` list. This separation is what keeps the agent sounding like a trusted
advisor rather than a commission-driven salesperson.

## Decision 4: Human-in-the-loop at the high-value moment

Automation's job is not to replace the human — it's to surface the *right* caller
to the human at the *right* time. When a caller scores into Tier 1, an alert fires
immediately, **whether or not they booked.** The highest-value lead is the one a
human calls back in five minutes.

## Decision 5: Follow-up is guaranteed, not hoped for

Every call ends with an SMS. Every un-booked call enters a 24h / 72h cadence with
explicit exit conditions (a confirmed booking cancels the remaining steps). This
converts the single most common failure — "the call ended and nothing happened" —
into a structured, measurable sequence.

## Decision 6: Platform-agnostic by design

The logic lives in config (`agent_config.yaml`), a data schema
(`qualification_schema.json`), and reference code (`src/`). None of it is locked
inside a single vendor's UI. Swap telephony providers and the brain comes with you.

## Why this generalizes

The four-criterion scoring model and five-route structure are not specific to one
industry. The route definitions and qualification signals are the only things that
change per vertical. See the README's "Adapt it to your vertical" section.
