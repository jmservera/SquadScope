# Copilot Instructions for SquadScope

This repository uses the **Squad agent** as the default for all AI-assisted work.

## Default Agent

Always use `--agent squad` when running Copilot CLI on this repository.

## Repository Context

- **Project:** SquadScope (public brand: Claracle) — AI-powered GitHub trend analysis
- **Architecture:** See `architecture.md` in repo root
- **Squad team:** See `.squad/team.md` for current roster

## Key Conventions

- All pipeline scripts are in `scripts/` (Python)
- Content is Hugo markdown in `content/`
- Config shared with Podcaster lives in `config/podcast.json`
- Changes to `config/podcast.json` MUST be coordinated with SquadScope-Podcaster repo
- Never commit secrets; use GitHub environment secrets
- PRs required for `main` branch (branch protection enabled)
- CI must be correct, not just green — verify rendered output for site changes

## Cross-Repo Impact

Changes to these files affect the Podcaster repo:

- `config/podcast.json` — Podcaster reads this config for episode generation
- `scripts/podcaster_handoff.py` — defines the handoff payload contract

## Testing

- Run `pytest tests/` for unit tests
- Hugo build: `hugo --minify` must succeed
- Handoff smoke: `.github/workflows/podcaster-handoff-smoke.yml`

## DevSecOps Guardrails

Part of the DevSecOps Guardrails epic (jmservera/SquadScope-Coordinator#33).
Baselines and per-tool docs live in `docs/devsecops/`. Phase A tooling is
**warning-only / non-blocking** today; do not weaken or skip a real gate to make
CI pass — CI must be correct, not just green.

### Before you push (always)

- Run the local tests: `pytest tests/`.
- If you changed a `Dockerfile`/`Containerfile`: run `docker build` locally.
- Lint/format Python with **ruff**.
- If you changed IaC or container files: run **checkov**.
- If you changed anything under `.github/workflows/`: run **zizmor**.

### Tooling (run manually)

```bash
# Python lint/format — ruff (config in pyproject.toml; see docs/devsecops/ruff-baseline.md)
pip install ruff==0.15.7
ruff check .            # lint (report)
ruff check . --fix      # apply safe fixes
ruff format .           # format

# IaC / container / Actions scan — checkov (see docs/devsecops/checkov-baseline.md)
pip install checkov==3.2.533
checkov --directory . --framework github_actions dockerfile secrets \
  --skip-path node_modules --skip-path .venv --compact --soft-fail

# GitHub Actions security — zizmor (see docs/devsecops/zizmor-baseline.md)
pipx install zizmor
zizmor .github/workflows/
```

### Git hooks

Local pre-commit/pre-push hooks live in `.pre-commit-config.yaml` (ruff,
checkov, pytest, docker build). Install them once and keep tool versions in
sync with CI — see `docs/devsecops/pre-commit.md`:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
```

**Emergency skip:** `git commit --no-verify` / `git push --no-verify` bypasses
local hooks — use only for genuine emergencies and follow up by fixing the
skipped findings. Never disable the CI gates themselves to land a change.

### Ownership

- **URL** (DevSecOps Specialist) owns the guardrail pipeline, tooling, hooks,
  dependency scanning, and secret detection.
- **Hermes** (Security & Threat Analyst) owns security review, threat modeling,
  and alert triage.
- Infra, `Dockerfile`/`Containerfile`, and workflow changes should be reviewed by
  URL (pipeline impact) and Hermes (security).
