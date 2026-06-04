# Usage Guide

## Prerequisites

- Python 3.10+
- pip

## Installation

```bash
git clone https://github.com/michaelabera/voice-ai-qualification.git
cd voice-ai-qualification
pip install -r requirements.txt        # runtime only
pip install -r requirements-dev.txt    # includes pytest + httpx for testing
```

## Running the Server

### Locally

```bash
uvicorn server:app --app-dir src --port 8000
```

With auto-reload during development:

```bash
uvicorn server:app --app-dir src --port 8000 --reload
```

### With Docker

```bash
docker compose up --build
```

The server starts on port **8000**.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness/readiness probe |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/v1/qualify` | Run the qualification pipeline on a caller |
| `GET` | `/v1/analytics` | Aggregated call-outcome summary |

### Qualify a caller

```bash
curl -X POST http://localhost:8000/v1/qualify \
  -H 'content-type: application/json' \
  -d '{
    "signals": {
      "intent_clarity": 1.0,
      "fit_threshold": 1.0,
      "timeline": 1.0,
      "decision_power": 1.0
    }
  }'
```

Response:

```json
{
  "route": "A_primary_service",
  "score": 100,
  "tier": "tier_1_high_intent",
  "actions": ["alert_human", "book", "sms"],
  "alert_human": true
}
```

### Optional caller fields

The `/v1/qualify` payload accepts these additional fields:

```json
{
  "name": "Jordan",
  "phone": "+15551234567",
  "company": "Acme Corp",
  "is_returning_client": false,
  "is_partner": false,
  "wants_secondary": false,
  "signals": { ... }
}
```

Setting `is_returning_client`, `is_partner`, or `wants_secondary` changes the routing path (see the five-route architecture in `README.md`).

### Check analytics

```bash
curl http://localhost:8000/v1/analytics
```

Returns total calls, bookings, conversion rates by tier, score distribution, and human-alert count.

## Persistent Analytics with SQLite

By default, call events are stored in memory and lost on restart. To persist them, set the `VAQ_DB` environment variable to a SQLite database path:

```bash
VAQ_DB=./data/calls.db uvicorn server:app --app-dir src --port 8000
```

Or in Docker:

```yaml
# docker-compose.yml
services:
  qualification-engine:
    environment:
      - VAQ_DB=/app/data/calls.db
    volumes:
      - ./data:/app/data
```

## CLI Demos

Run the core logic without starting the server:

```bash
# Qualification router — routes and scores sample callers
python src/router.py --demo

# SMS cadence — prints follow-up sequences for booked vs. not-booked
python src/sms_cadence.py --demo

# Analytics — aggregates sample call outcomes
python src/analytics.py --demo

# A/B test — compares two scoring-weight variants on synthetic callers
python src/ab_test.py --demo
```

## Config Validation

Validate your agent config before deploying:

```bash
# Basic validation (structure + routes)
python src/validate_config.py config/agent_config.yaml

# Strict mode — also fails on unfilled {{PLACEHOLDER}} tokens
python src/validate_config.py config/agent_config.local.yaml --strict
```

## Config Builder (No-Code)

Open `tools/config-builder/index.html` in a browser to generate a valid `agent_config.yaml` interactively. Nothing leaves the browser.

## Customizing the Config

1. Copy the template:
   ```bash
   cp config/agent_config.yaml config/agent_config.local.yaml
   ```
2. Replace every `{{PLACEHOLDER}}` with your values.
3. Validate with `--strict` before deploying.

`config/*.local.yaml` is gitignored so secrets are never committed.

## Vertical Presets

Pre-built presets are available in `presets/`:

- `healthcare_intake.yaml`
- `home_services.yaml`
- `real_estate.yaml`

These overlay the base config with vertical-specific route definitions and scoring criteria.

## Locales

Caller-facing strings are in `locales/` (`en.yaml`, `es.yaml`). The decision logic is language-agnostic — swap the locale without changing routing or scoring.

## Running Tests

```bash
pytest -q
```

Tests cover routing, scoring, SMS cadence, analytics, server endpoints, config validation, presets, PII redaction, and the analytics sink.

## Integrating with a Voice Platform

Point your voice platform's webhook (Vapi, Retell, Bland, Synthflow, Twilio, etc.) at `POST /v1/qualify`. For calendar, CRM, SMS, and email integration details, see [`docs/INTEGRATIONS.md`](./docs/INTEGRATIONS.md).
