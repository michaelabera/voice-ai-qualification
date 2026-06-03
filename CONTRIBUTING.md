# Contributing

Thanks for your interest in improving the Voice AI Qualification Engine.

## Ground rules

- **Keep it generic.** This repo is a vendor-neutral pattern. Don't add
  company-specific content, real scripts, client data, or proprietary material
  to any contribution. Use `{{PLACEHOLDER}}` tokens.
- **Tests pass.** Run `pytest -q` before opening a PR. Add tests for new logic.
- **Config stays valid.** `agent_config.yaml` must parse as YAML;
  `qualification_schema.json` must be valid JSON. CI checks both.

## How to contribute

1. Fork and create a branch: `git checkout -b feature/your-idea`
2. Make your change. Add or update tests in `tests/`.
3. Run `pytest -q` and the demos.
4. Open a PR describing the change and the use case it serves.

## Ideas that are welcome

- New vertical examples (route + scoring presets for an industry)
- Additional reference integrations in `docs/INTEGRATIONS.md`
- Stronger scoring models or alternative tier strategies
- Validation tooling for the config

## Reporting issues

Use the issue templates. For anything security- or privacy-related, please note
it clearly so it can be prioritized.
