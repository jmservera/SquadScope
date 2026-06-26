# Checkov Baseline (Phase A — warning-only)

> Issue: jmservera/SquadScope#541 · Epic: jmservera/SquadScope-Coordinator#33
> Mode: **warning-only / non-blocking** (`--soft-fail`). Do not fix (Phase B) or enforce (Phase C) yet.

Checkov scans IaC, container, and GitHub Actions configuration for
misconfigurations. SquadScope currently has **no Dockerfiles, Terraform/Bicep,
docker-compose, or k8s manifests** — the only in-scope targets today are the
GitHub Actions workflows under `.github/workflows/`. The CI job is wired to also
cover `dockerfile` and `secrets` frameworks so coverage extends automatically
when container/IaC files are added.

## CI behaviour

`.github/workflows/checkov.yml` runs Checkov with `--soft-fail` and
`continue-on-error: true` (non-blocking), uploads SARIF to GitHub Code Scanning,
and attaches the SARIF as a build artifact.

## Baseline snapshot

- **Tool:** checkov 3.2.533
- **Date:** 2026-06-26
- **Frameworks:** github_actions, dockerfile, secrets
- **github_actions:** 540 passed, **4 failed**, 0 skipped
- **CRITICAL/HIGH:** 0 (the failing GHA checks carry no CRITICAL/HIGH severity tag)

### Failing checks (counts by check ID)

| Count | Check ID | Description |
|------:|----------|-------------|
| 4 | CKV_GHA_7 | `workflow_dispatch` inputs should be empty (build output must not be affected by user parameters) |

Affected workflows (deferred to Phase B):

- `.github/workflows/restore-publish-backup.yml`
- `.github/workflows/squad-promote.yml`
- `.github/workflows/trigger-podcast.yml`
- `.github/workflows/podcaster-handoff-smoke.yml`

> Note: CKV_GHA_7 flags any `workflow_dispatch` with inputs. These workflows use
> inputs intentionally; triage and any suppressions belong to Phase B.

## Running locally

```bash
# Install (pinned to match CI)
pip install checkov==3.2.533

# Scan the whole repo (report only)
checkov --directory . \
  --framework github_actions dockerfile secrets \
  --skip-path node_modules --skip-path .venv \
  --skip-path public --skip-path resources --skip-path themes \
  --compact --soft-fail

# Scan a single file/dir
checkov --file .github/workflows/ci.yml
```

## Phase plan

- **Phase A (now):** baseline + non-blocking CI + SARIF upload. ← this PR
- **Phase B:** triage findings; add justified suppressions or fixes.
- **Phase C:** blocking required status check for new misconfigurations.
