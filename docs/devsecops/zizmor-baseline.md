# Zizmor Baseline (Phase A — warning-only)

> Issue: jmservera/SquadScope#542 · Epic: jmservera/SquadScope-Coordinator#33
> Mode: **warning-only / non-blocking**. Do not fix (Phase B) or enforce (Phase C) yet.

[zizmor](https://github.com/zizmorcore/zizmor) audits GitHub Actions workflows
for supply-chain risks (template injection, dangerous triggers, unpinned actions,
excessive permissions). It **already exists** in
`.github/workflows/security-scanning.yml` (`zizmorcore/zizmor-action`). This task
normalizes it to the Phase-A contract — it does **not** recreate the job.

## CI wiring (confirmed)

- **Job:** `zizmor-scan` in `.github/workflows/security-scanning.yml`.
- **Triggers:** push + pull_request to `main`/`dev` — so it runs on any change to
  `.github/workflows/`.
- **Non-blocking:** `continue-on-error: true` (Phase A warning-only).
- **SARIF / annotations:** `advanced-security: true` uploads SARIF to GitHub Code
  Scanning automatically.
- **Scope:** all repository-owned workflows, excluding generated `squad-*` and
  `sync-squad-labels` files.

## Baseline snapshot

- **Tool:** zizmor 1.25.2
- **Date:** 2026-06-26
- **Scope:** repo-owned workflows (Squad-generated files excluded)

### Default (`regular`) persona — what CI surfaces today

**0 actionable findings** (7 ignored, 42 suppressed). The Phase-A gate is green
on the default persona; the action focuses on P0 findings (template-injection,
dangerous-triggers), of which there are none.

### Deep (`pedantic`) persona — full backlog for Phase B

Total: **36** findings.

| Count | Rule | Severity |
|------:|------|----------|
| 15 | anonymous-definition | Informational |
| 14 | undocumented-permissions | Low |
| 4 | excessive-permissions | High |
| 3 | concurrency-limits | Low |

By severity: High 4 · Low 17 · Informational 15.

> The 4 `excessive-permissions` (High) findings are the priority items for
> Phase B. The remainder are documentation/informational hardening.

## Running locally

```bash
# Install (matches the action's toolchain family)
pipx install zizmor      # or: pip install zizmor

# Default persona (what CI reports)
zizmor .github/workflows/

# Deeper audit used to build the Phase-B backlog
zizmor --persona pedantic .github/workflows/

# Mirror the CI input set (exclude generated Squad workflows)
zizmor $(find .github/workflows -maxdepth 1 -type f \
  \( -name "*.yml" -o -name "*.yaml" \) \
  ! -name "squad-*.yml" ! -name "sync-squad-labels.yml" | sort)
```

## Findings deferred to Phase B

- `excessive-permissions` (High ×4) — tighten job/workflow `permissions:` blocks.
- `undocumented-permissions` (Low ×14) — add explicit minimal permissions.
- `concurrency-limits` (Low ×3) — add `concurrency:` groups where missing.
- `anonymous-definition` (Informational ×15) — name unnamed steps/definitions.

## Phase plan

- **Phase A (now):** confirm non-blocking + SARIF wiring; record baseline. ← this PR
- **Phase B:** fix High-severity excessive-permissions, then Low/Informational.
- **Phase C:** blocking enforcement (drop `continue-on-error`).
