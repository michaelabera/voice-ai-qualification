# FAQ

Honest answers to the questions a business owner, a developer, or a hiring
manager actually asks before relying on this. No overselling — where something
isn't built yet, it says so.

---

## For business owners

**What does this actually do for my business?**

It's the decision layer for an inbound voice AI agent. When a call comes in, it
figures out *why* the person is calling, qualifies them in real time, and decides
what to do — book the good ones, alert you to the hot ones, capture the rest so
none slip away. The practical win: a call that used to hit voicemail after hours
becomes a qualified, booked meeting instead.

Important: this is the *brain*, not the phone system. It decides; a voice
platform (Vapi, Retell, Twilio, etc.) does the actual talking.

**Do I need to be technical to use this?**

Partly. The included no-code config builder lets you set up the agent's behavior
without code. But connecting it to a real phone line and your other tools needs a
developer or a technical contractor. It is not yet plug-and-play.

**What will it cost me to run?**

The software here is free (MIT licensed). Your real costs are third-party,
usage-based services you'd need regardless:
- A voice platform (Vapi/Retell/Bland/Twilio) — typically per-minute pricing.
- A phone number — usually a few dollars a month.
- SMS for follow-ups — per-message.
- Hosting for the server — can be a few dollars a month on a small host.

These vary by provider and volume; check current pricing with whichever you pick.

**How long until it's answering my phone?**

The decision logic is ready today. The variable is integration. A developer
typically needs several weeks to wire it to your phone system, calendar, CRM, and
messaging (see the deployment scope below).

---

## For developers / technical evaluators

**Does it actually run, or is it just a demo?**

Both, and it's labeled honestly:
- The decision engine and API are real and tested — 41 tests, CI green across
  Python 3.10–3.12 plus a Docker build.
- Analytics persistence is real (SQLite via the `VAQ_DB` env var).
- The vendor *integrations* are documented recipes, not finished SDKs.

**How does it connect to a phone system?**

Via webhook. The voice platform sends call data to `POST /v1/qualify`; the
service returns route, score, tier, and the actions to take. See
[`docs/INTEGRATIONS.md`](./docs/INTEGRATIONS.md).

**Is it production-hardened?**

Not fully, and here's the honest list of what a production deployment still
needs:
- Webhook authentication / signature verification (none yet).
- Access control on `/metrics` and `/v1/analytics` (currently open).
- Rate limiting and request-size limits.
- Confidence thresholds and graceful fallback when the agent is unsure.

These are deliberate scope boundaries, not oversights — this repo is the decision
architecture, and these are the deployment concerns layered on top.

**What happens when the agent doesn't understand a caller?**

By design, unclear callers route to triage and a human handoff — no caller is a
dead end. That routing exists; automated confidence-scoring and fallback are
documented intent, not enforced code yet.

**How do the `signals` get produced?**

This is the biggest integration lift to understand. The system scores callers
from 0.0–1.0 `signals` (intent, fit, timeline, decision power). This repo
*consumes* those signals; in a live deployment, your voice agent has to *extract*
them from the conversation. That extraction is the main thing a developer builds
on top.

---

## For everyone

**Why use this instead of Vapi/Retell directly?**

Those platforms give you the runtime — the ability to run an agent. They don't
give you an opinionated qualification architecture: the routing order, the tiered
scoring, the no-dead-ends principle, the human-alert trigger, the follow-up
cadence. That's the part teams usually rebuild from scratch. This sits on top of
any of them.

**Can it integrate with my CRM / Zapier / Make / n8n?**

The server is a standard webhook, so automation platforms (Zapier, Make, n8n) can
call it and act on its output today. Deeper CRM integration — like looking up a
caller by phone/email and updating them by tag instead of creating a duplicate
lead — is a natural extension a developer can add; the architecture supports it
but it's not built in yet.

**Who built it and can they support it?**

Built by [@michaelabera](https://github.com/michaelabera). Open an issue for
questions.

---

## Deployment scope — what a developer adds to go live

Honest estimate to take this from "runs in a demo" to "running a real business's
inbound calls": roughly **6–12 weeks** for a competent developer, depending on
the business's existing stack and whether the knowledge base is included.

| Work | Rough effort | Notes |
|------|-------------|-------|
| Voice platform wiring + signal extraction | 1–2 weeks | The biggest lift — turning live conversation into the 0–1 signals |
| CRM integration with tag-aware lookup | 1–2 weeks per CRM | Avoids duplicate leads; updates existing prospects by tag |
| Knowledge base / mid-call Q&A | 2–4 weeks | A retrieval system (vector store); optional, can be cut |
| Production hardening (auth, rate limits) | ~1 week | The security items listed above |
| Action wiring (calendar, SMS, transfer, alerts) | 1–2 weeks | Booking, hot transfer, Slack/email alerts |

**What's already done (the hard part):** the decision architecture — routing,
scoring, tiering, follow-up cadence, data models, API, persistent analytics, and
tests. A developer doesn't rebuild any of that; they integrate around it.

---

## Roadmap (honest)

Things the architecture supports and that would extend it naturally, not yet
built:
- CRM tag-aware caller lookup before routing.
- Time-aware "hot routing" — live transfer or instant SMS during business hours.
- A pluggable knowledge-base interface for mid-call Q&A.
- Webhook auth and endpoint access control.

Contributions welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md).
