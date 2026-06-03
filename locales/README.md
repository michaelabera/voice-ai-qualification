# Locales

Caller-facing language strings, separated from logic so the same routing and
scoring works in any language. Add a new language by copying `en.yaml` and
translating the values. Keys must match across all locale files.

The agent selects a locale at call start (e.g. from the caller's number region
or an explicit menu) and pulls all spoken lines from the matching file. The
decision logic in `src/` never changes.
