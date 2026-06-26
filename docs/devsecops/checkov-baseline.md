# Checkov Baseline

> Issue: jmservera/SquadScope#541 (Phase A) · jmservera/SquadScope#543 (Phase B fixes)
> Epic: jmservera/SquadScope-Coordinator#33
> Status: **Phase B complete** — 0 failed checks (4 justified `checkov:skip`).

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
- **github_actions (current):** 604 passed, **0 failed**, 4 skipped
- **CRITICAL/HIGH:** 0

### Phase A findings (resolved in Phase B)

| Count | Check ID | Description | Phase B resolution |
|------:|----------|-------------|--------------------|
| 4 | CKV_GHA_7 | `workflow_dispatch` inputs should be empty (SLSA build-integrity) | Justified `# checkov:skip=CKV_GHA_7:...` inline comments |

The four affected workflows are operational/dispatch workflows (not release
builds); their inputs select an operational target (week, run-id, manifest,
dry-run toggle) and do not alter published build artifacts, so a justified skip
is the correct disposition:

- `.github/workflows/restore-publish-backup.yml`
- `.github/workflows/squad-promote.yml`
- `.github/workflows/trigger-podcast.yml`
- `.github/workflows/podcaster-handoff-smoke.yml`

> Each skip carries an inline justification next to the `workflow_dispatch`
> block. Re-run `checkov` after any workflow change to confirm 0 failures.

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

- **Phase A:** baseline + non-blocking CI + SARIF upload. ✅
- **Phase B:** triage findings; justified suppressions or fixes. ✅ 0 failed (4 justified skips).
- **Phase C:** blocking required status check (#545) for new misconfigurations.
