# Pre-commit / pre-push hooks (local enforcement)

> Issue: jmservera/SquadScope#544 · Epic: jmservera/SquadScope-Coordinator#33
> Phase C — local enforcement. Mirrors the CI guardrails so violations are
> caught before they reach a PR.

The repo ships a [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) that
runs the same guardrails as CI:

| Hook | Stage | Mirrors |
|------|-------|---------|
| `ruff` (lint, `--fix`) | commit | Lint workflow (`ruff check .`) |
| `ruff-format` | commit | Lint workflow (`ruff format --check .`) |
| `checkov` | push | Checkov workflow (IaC / Actions scan) |
| `pytest` | push | CI test job (`pytest tests/`) |
| `docker-build` | push | builds a `Containerfile`/`Dockerfile` when present (no-op today) |

Fast checks (ruff) run on every **commit**; slower checks (checkov, pytest,
docker build) run on **push** to keep the commit loop quick.

## Install (one-time)

```bash
pip install pre-commit
# Install both hook types so commit-stage and push-stage hooks are wired up:
pre-commit install --hook-type pre-commit --hook-type pre-push
```

To run everything on demand (e.g. before opening a PR):

```bash
pre-commit run --all-files
```

## Tool versions

Hook versions are **pinned to match CI** so local and CI results agree:

- `ruff` → `0.15.7` (`rev: v0.15.7`)
- `checkov` → `3.2.533` (`rev: "3.2.533"`)

`pytest` and the `docker-build` check are `local` hooks that use the
repo-installed tooling (`pip install -r requirements.txt` plus `pytest`). When
you bump a tool version in CI, bump the matching `rev`/dependency in
`.pre-commit-config.yaml` too.

## Emergency bypass (hotfixes only)

```bash
git commit --no-verify
git push   --no-verify
```

`--no-verify` skips **local** hooks only — the CI gates still run on the PR.
Use it only for genuine emergencies and follow up by fixing any skipped
findings. Never weaken or disable a CI gate to land a change: CI must be
correct, not just green.

## Notes

- The `docker-build` hook is a no-op until a `Containerfile`/`Dockerfile` is
  added at the repo root, after which it builds the image on push.
- The `checkov` hook only triggers on changes to `.github/workflows/**` or
  container files, but always scans the whole repo (`checkov -d .`) to mirror CI.
