# Checkov Baseline

> Issue: jmservera/SquadScope#541 (Phase A) · jmservera/SquadScope#543 (Phase B fixes)
> Epic: jmservera/SquadScope-Coordinator#33
> Status: **Phase C enforced** — 0 failed checks; justified `checkov:skip`
> suppressions are honored by the blocking CLI gate and removed from uploaded
> SARIF before GitHub Code Scanning ingestion.

Checkov scans IaC, container, and GitHub Actions configuration for
misconfigurations. SquadScope currently has **no Dockerfiles, Terraform/Bicep,
docker-compose, or k8s manifests** — the only in-scope targets today are the
GitHub Actions workflows under `.github/workflows/`. The CI job is wired to also
cover `dockerfile` and `secrets` frameworks so coverage extends automatically
when container/IaC files are added.

## CI behaviour

`.github/workflows/checkov.yml` runs Checkov as a blocking gate, uploads SARIF
to GitHub Code Scanning, and attaches the SARIF as a build artifact. The CLI
report remains the enforcement source. Before upload, the workflow runs
`scripts/filter_checkov_sarif.py` to remove only results that Checkov already
marked with in-source suppressions from justified inline `checkov:skip`
comments. Unsuppressed findings remain in SARIF and fail the Checkov step.

## Baseline snapshot

- **Tool:** checkov 3.2.533
- **Date:** 2026-09-28
- **Frameworks:** github_actions, dockerfile, secrets
- **github_actions (current):** local targeted CKV_GHA_7 scan reports
  20 passed, **0 failed**, 7 skipped
- **CRITICAL/HIGH:** 0

### Accepted CKV_GHA_7 findings

| Count | Check ID | Description | Resolution |
|------:|----------|-------------|--------------------|
| 7 | CKV_GHA_7 | `workflow_dispatch` inputs should be empty (SLSA build-integrity) | Justified `# checkov:skip=CKV_GHA_7:...` inline comments; suppressed SARIF results filtered before Code Scanning upload |

The affected workflows are operational/dispatch workflows (not release builds);
their inputs select retained operational evidence (including the required
Podcaster publish run ID), immutable reviewed SHAs, a manifest, observe-only
mode, bounded smoke-test limits, or a dry-run mode. They do not alter build
output, so a justified skip is the correct disposition when inputs are validated:

- `.github/workflows/auto-podcast-dispatch.yml`
- `.github/workflows/build-cost-experiment.yml`
- `.github/workflows/podcaster-handoff-smoke.yml`
- `.github/workflows/repo-identity-backfill.yml`
- `.github/workflows/restore-publish-backup.yml`
- `.github/workflows/squad-promote.yml`
- `.github/workflows/trigger-podcast.yml`

> Each skip carries an inline justification next to the `workflow_dispatch`
> block. Re-run `checkov` after any workflow change to confirm 0 failures.
> Re-run the Checkov workflow to confirm uploaded SARIF no longer contains
> accepted in-source suppressions as open Code Scanning alerts.

The real Podcaster workflow binds credentials to the
`podcaster-real-generation` environment. Repository administrators must create
that environment, restrict it to `main`, configure required review and prevent
self-review, and store the endpoint variable and API key there before dispatch.

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
- **Phase C:** blocking CI gate (#545). ✅ The Checkov job dropped `--soft-fail`
  + `continue-on-error`; new misconfigurations fail the build. Mark it required.
