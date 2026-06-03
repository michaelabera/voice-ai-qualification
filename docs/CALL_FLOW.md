# Call Flow

The agent handles every inbound call through one of five routes. This document
walks each one. See `config/agent_config.yaml` for the machine-readable version.

## Route selection

```
is returning client?      → Route D
else is partner/referrer? → Route C
else wants secondary?     → Route B
else has buying intent?   → Route A
else                      → Route E
```

Returning clients and partners are checked first so they are never forced through
new-prospect intake.

---

## Route A — Primary Service

The core buyer path.

1. Confirm what the caller is trying to accomplish.
2. Run the qualification checklist.
3. Score against the tier matrix.
4. Tier 1 → alert a human immediately + book + SMS.
   Tier 2 → book + SMS.
   Tier 3 → capture + nurture SMS.
   Tier 4 → capture only (+ SMS).

## Route B — Secondary Service

Same shape as Route A, pointed at the adjacent offering. Qualify, then book if
ready or capture for nurture.

## Route C — Partner Program

The caller is a potential partner or referrer, not a buyer.

1. Do **not** run buyer qualification — it would be irrelevant and off-putting.
2. Capture their details.
3. Route to the partner track and send partner-specific follow-up.

## Route D — Returning Client

The caller is already in the system.

1. Skip standard qualification entirely.
2. Fast-path: offer to connect them to their contact, or book directly.
3. Never make them repeat full intake.

## Route E — Other / Triage

Intent is unclear or off-menu.

1. Ask one clarifying question.
2. If it maps to A–D, switch routes.
3. If not, capture full contact info and hand to a human.
4. **Never deprioritize** — an unclear caller may be the most valuable one.

---

## Universal end-of-call behavior

Regardless of route or outcome:

- An SMS with the calendar link is always sent.
- Voicemail callers get the same SMS after leaving a message.
- The call closes with warmth and exactly one clear next step.
- If the agent doesn't know an answer, it says so and routes to a human — it
  never invents.
