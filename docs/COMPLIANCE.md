# Compliance

Voice AI that handles real calls touches three regulated areas: call recording,
SMS messaging, and (in some verticals) protected health information. This is
general guidance to help you deploy responsibly. **It is not legal advice.**
Confirm requirements for your jurisdiction and industry with qualified counsel.

## 1. Recording & AI disclosure

Many jurisdictions require disclosing that a call is recorded and/or handled by
an automated system. Some require two-party consent. Add a disclosure to the
agent's greeting.

**Template (caller-facing):**
> "Just so you know, this call may be recorded and is handled by an automated
> assistant. You can ask to speak with a person at any time."

Set this in your locale file and ensure it plays before any data is collected.

## 2. SMS / messaging consent

The 0h / 24h / 72h cadence sends text messages. Messaging regulations generally
require prior consent and a clear opt-out.

**Opt-out language (append to the first SMS):**
> "Reply STOP to opt out at any time."

**Implementation checklist:**
- [ ] Capture consent before the first non-transactional message.
- [ ] Honor STOP/UNSUBSCRIBE immediately and suppress the rest of the cadence.
- [ ] Keep an auditable record of consent and opt-outs.
- [ ] Respect quiet hours where required.

## 3. PHI / healthcare (if applicable)

If callers may share protected health information:
- [ ] Request a Business Associate Agreement (BAA) from your voice platform and
      messaging provider, and confirm scope.
- [ ] Minimize what you store; prefer derived/qualification fields over raw PHI.
- [ ] Ensure logs are redacted (this repo's `logging_utils.py` does this by
      default for phone/email/name fields).

## 4. Data handling in this repo

- The reference `logging_utils.py` redacts phone numbers, emails, and PII-named
  fields before logs leave the process.
- `CallOutcomeEvent` carries no raw PII by default — only derived fields safe for
  analytics sinks.
- `config/*.local.yaml` (where you put real values) is gitignored.

## 5. Consent flow (recommended order)

1. Greeting + recording/AI disclosure.
2. Identify intent and route.
3. Collect only what qualification needs.
4. Obtain SMS consent before sending the cadence.
5. Provide opt-out and honor it.

Again: this is a practical starting checklist, not legal advice. Regulations vary
by country, state, and industry and change over time.
