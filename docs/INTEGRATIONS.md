# Integrations

This pattern is the *brain*. It assumes you bring the *body*: a telephony /
voice platform, a calendar, a CRM, and a messaging provider. This document maps
the config's abstract actions to real services.

> Nothing here endorses or depends on a specific vendor. These are common,
> interchangeable choices. Pick what fits your stack.

## The pieces

| Layer | What it does | Common options |
|-------|--------------|----------------|
| Voice platform | Answers the call, runs STT/LLM/TTS, executes the config | Vapi, Retell, Bland, Synthflow, Twilio + LLM |
| Calendar | Holds the bookable slots; produces the link | Calendly, Google Calendar, Cal.com |
| CRM | Stores the caller record and tier | GoHighLevel, HubSpot, Salesforce |
| Messaging | Sends the 0h/24h/72h SMS | Twilio, the voice platform's native SMS |
| Email | Delivers the voicemail transcript + lead alert | Gmail/Workspace, SendGrid |
| Glue (optional) | Connects everything without code | Zapier, Make, n8n |

## Wiring the config actions

The `handle()` function returns an `actions` list per caller. Map each action:

| Action | Wire it to |
|--------|-----------|
| `alert_human` | Send the `high_intent_alert.notification_template` to your phone/Slack/CRM task |
| `book` | Text the `{{CALENDAR_LINK}}`; optionally create a hold via the calendar API |
| `sms` / `sms_nurture` | Fire the matching `sms.cadence` template through your messaging provider |
| `capture` / `capture_only` | Upsert the caller record into your CRM |
| `fast_path_human` | Warm-transfer or notify the assigned owner |
| `capture_partner` | Tag the record to the partner pipeline |

## A common off-hours flow

A frequent reason teams deploy this: a missed call after hours used to become a
dead voicemail. With this pattern, the missed call instead:

1. Is answered by the agent, which qualifies and answers FAQs.
2. Books the caller via the calendar link (texted during the call).
3. Sends you an email with the transcript and a lead summary.
4. Enters the SMS cadence if no booking is confirmed.

A no-code glue tool (Zapier / Make / n8n) is usually enough to connect the voice
platform's webhook to your calendar, CRM, and email — no backend required.

## Compliance notes

- **Recording consent**: many jurisdictions require disclosing that a call is
  recorded or AI-handled. Add a disclosure line to the agent's greeting.
- **PHI / healthcare**: if callers may share protected health information,
  request a BAA from your voice platform and confirm scope before going live.
- **SMS regulations**: follow the messaging rules for your region (consent,
  opt-out language) when wiring the cadence.

This is general guidance, not legal advice. Confirm requirements for your
jurisdiction and industry.
