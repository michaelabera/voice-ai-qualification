# Sample Call — Annotated

An annotated walkthrough of a Tier 1 call through Route A. Caller-facing language
on the left; internal system behavior in the `>` notes.

---

**Agent:** Thanks for calling {{COMPANY_NAME}}, this is {{AGENT_NAME}}. What can I help you with today?

> Route not yet determined. Listening for intent.

**Caller:** Hi, I run a logistics company and we're trying to figure out our options for growth capital.

> Buying intent detected, not a returning client or partner → **Route A**.
> Begin qualification checklist.

**Agent:** Happy to help with that. So I can point you in the right direction — roughly what does your monthly revenue look like, and how soon are you hoping to move?

> Capturing `fit_threshold` and `timeline` signals.

**Caller:** We're doing about $400K a month and we'd want to move in the next few weeks.

> fit_threshold ≈ high, timeline ≈ high.

**Agent:** Got it. And are you the one making this decision, or would others be involved?

> Capturing `decision_power`.

**Caller:** It's me and my business partner, but I lead it.

> decision_power ≈ high. Score crosses Tier 1 threshold.
> **Fire high-intent alert to a human now**, regardless of booking.

**Agent:** Perfect. You're exactly the kind of business we work well with. I'd like to get you on a quick {{CALL_LENGTH}}-minute call with one of our advisors — I'll text you a link right now so you can grab a time that works.

> Booking attempt + immediate SMS queued.

**Caller:** Sounds good.

**Agent:** Done — check your texts for the calendar link and a short overview video. We're looking forward to it.

> SMS sent (0h). Booking pending. If not confirmed, 24h + 72h follow-ups will fire.
> Note: internal revenue mechanics were never mentioned — only the caller's benefit.
