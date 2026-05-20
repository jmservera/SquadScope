# 2026-05-20: Model resilience for weekly CI

- **Owner:** Farnsworth
- **Date:** 2026-05-20T20:09:26+02:00
- **Status:** Proposed
- **Decision:** The `crawl-and-publish.yml` workflow should never pass a version-pinned `--model` flag to GitHub Copilot CLI. Analysis and reskill should rely on the CLI's platform default model, while GitHub Models fallback remains configurable through `GITHUB_MODELS_MODEL` with `openai/gpt-4o` as the default.
- **Why:** Pinned Copilot CLI model IDs can disappear from the platform and silently degrade the pipeline into fallback or no-AI paths. Letting the CLI choose its current default keeps the primary path available without manual model churn, while the fallback path still has an explicit, overridable model.
- **Implementation notes:**
  - Removed `--model claude-sonnet-4` from Copilot CLI invocations in analysis and reskill.
  - Removed the workflow's pinned preflight model argument and switched cost estimation/usage tracking to a generic `copilot-default` rate profile.
  - Promoted `GITHUB_MODELS_MODEL` to workflow-level env configuration using `${{ vars.GITHUB_MODELS_MODEL || 'openai/gpt-4o' }}`.
- **Scope:** `.github/workflows/crawl-and-publish.yml`, `scripts/preflight_cost_check.py`, `scripts/track_token_usage.py`
