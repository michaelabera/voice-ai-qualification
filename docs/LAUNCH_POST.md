# LinkedIn Launch Post

Direct, B2B-authority tone. No em dashes, no hype, no guarantees. Copy, adjust the
specifics, post. Swap michaelabera for your handle.

---

**Draft A — the problem-first version (recommended)**

Most businesses lose their best leads the same way: a call comes in after hours, hits voicemail, and nothing happens.

By the time anyone calls back, the prospect already booked with someone else.

I kept seeing this, so I architected a fix and open-sourced the pattern.

It is a decision architecture for inbound voice-AI agents. Bring any platform (Vapi, Retell, Twilio, others). This handles the part that actually matters: how the agent routes a mixed inbound call, scores intent in real time, protects your internal business logic, alerts a human the moment a high-value caller is on the line, and guarantees follow-up so no lead is ever a dead end.

Five caller routes. A tiered qualification model. An SMS cadence with exit conditions. Runnable reference code with tests and CI, not slideware.

It is fully generic and vendor-neutral, so you can adapt it to advisory, home services, healthcare intake, real estate, or agency work by swapping two files.

Repo (MIT licensed): github.com/michaelabera/voice-ai-qualification

If you run a call-heavy business, what happens to your after-hours calls right now? Curious how many people have actually solved this.

---

**Draft B — the builder/technical version**

I open-sourced the decision architecture behind an inbound voice-AI qualification agent.

The voice platforms (Vapi, Retell, Bland, Synthflow) are mature. What is still scarce is the layer that separates a flaky demo from a deployment a business trusts: the routing and qualification logic.

So I built that layer as a clean, vendor-neutral pattern:

- 5-way intent router (buyer, returning client, partner, triage)
- Weighted, tiered qualification scoring (0 to 100, four action tiers)
- Internal-context separation so the agent never leaks business logic to the caller
- Real-time human alerts on high-intent callers
- 0h / 24h / 72h SMS cadence with exit conditions
- pytest suite + GitHub Actions CI + Mermaid architecture diagrams

It runs as config plus reference code, so the logic is portable across any telephony stack.

MIT licensed: github.com/michaelabera/voice-ai-qualification

Feedback and PRs welcome. What would you add to the scoring model?

---

**Posting notes**
- Post once, pick A or B. A pulls founders and recruiters; B pulls engineers.
- First line is the hook; it is what shows before "see more." Keep it sharp.
- Reply to every comment within the first few hours.
- Add the repo to your LinkedIn "Featured" section the same day.
