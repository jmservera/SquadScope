# Hermes Security Review: PR #701 (fix/br009-ledger-commit-path-gap)

## Research Topics/Questions

1. Does uploading/downloading `token-usage-ledger` as a GitHub Actions artifact introduce artifact-poisoning risk, given this workflow's trigger surface?
2. Could `data/metrics/token-usage.jsonl` ever contain secrets/tokens/PII that shouldn't land on the public `publish` branch?
3. Are the new `actions/upload-artifact` / `actions/download-artifact` steps pinned by full commit SHA, consistent with the rest of the file, and do they request excess permissions?
4. What does `zizmor --persona=regular` report for this workflow, and is the finding count/severity unchanged vs. `main`?
5. Overall verdict.

## Findings

### 1. Trigger reachability / artifact-poisoning risk

- Workflow trigger (`.github/workflows/crawl-and-publish.yml:3-59`): `schedule` (cron) and `workflow_dispatch` only. No `pull_request`, `pull_request_target`, or `issue_comment` trigger. This is **not** reachable by an untrusted fork PR — a malicious actor cannot cause this workflow to run against attacker-controlled input; only users with `workflow_dispatch` permission (repo write access) can trigger it, and `schedule` always runs against the default branch.
- Top-level `permissions: contents: read` (line 61-62); `analyze` job elevates to `actions: read, contents: write, issues: write, models: read` (line 338-341); `generate` job uses `actions: read, contents: write` (~line 1056-1058). Both are scoped to this same workflow run — no cross-workflow or cross-repo artifact reference.
- The new artifact (`token-usage-ledger`) is produced and consumed **within the same workflow run** (`analyze` job uploads it, `generate` job — which `needs: analyze` — downloads it). `actions/download-artifact` without an explicit `run-id`/`github-token` input defaults to the *current* run, so there is no possibility of pulling an artifact from a different (attacker-influenced) run.
- Because the trigger surface excludes any fork-reachable event, and the artifact is scoped to the same run, there is **no new artifact-poisoning attack surface** introduced by this change. This differs qualitatively from the classic "artifact poisoning" CVE pattern (e.g. `pull_request_target` + artifact download from an untrusted `pull_request` run), which does not apply here.
- Note (pre-existing, not from this PR): this repo's own `.squad/agents/hermes/*` or other docs may reference general artifact-poisoning guidance for CI, but nothing in this PR changes the trigger model.

### 2. Sensitive-data assessment (`scripts/track_token_usage.py`)

- `build_record()` (lines ~155-215) constructs a JSON record with only: `timestamp`, `month`, `week`, `stage`, `source`, `model` (a model *name* string, e.g. `"copilot-default"`), `input_tokens`/`output_tokens`/`total_tokens` (ints), `cost_usd` (float/null), `estimated` (bool), and optionally `workflow_run_id` (stringified numeric run ID) / `run_attempt` (int) / `input_manifest_validation` (a dict of numeric ratios, a `manifest_path` string, and a templated `reason` string interpolating only numbers, e.g. `"Final input usage differs from manifest by 12.0% (100 actual vs 89 estimated)."`).
- No field ever captures free-form prompt/response content, transcript text, file contents, secrets, tokens, or PII. Token counts are either explicit CLI args, regex-extracted counts from a transcript/API-response file (only the numeric usage fields, via `parse_copilot_transcript` / `parse_api_response`), or a file-size-based estimate (`len(text)` only, text itself discarded).
- `append_record()` writes via `json.dumps(record, ensure_ascii=True)` — no raw external text is embedded.
- Confirmed this file is **already committed to and public on the `publish` branch today** (verified via `git show origin/publish:data/metrics/token-usage.jsonl`, existing rows going back to at least week 2026-W23). This PR does not introduce a new sensitive-data-to-public-branch pathway; it fixes a bug where the *current* run's row was being silently dropped before commit (previously overwritten by `origin/publish`'s stale copy during the "Hydrate prior generated state from publish" step). No change in what data class reaches `publish` — same schema, same fields, same commit job (`generate`'s existing `git add -A -- "${ADD_PATHS[@]}"` over `GENERATED_PATHS`, which already included `data/metrics/`).

### 3. Action pinning / permissions

- New steps use:
  - `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1` — identical SHA to 6 other `upload-artifact` call sites already in this file (lines 250, 259, 267, 1024, 1032, 1396, 1414).
  - `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1` — identical SHA to 9 other `download-artifact` call sites already in this file (lines 145, 155, 165, 362, 1102, 1120, 1126, 1448, 1454, 1460, 1530, 1535).
  - Both are pinned to a full 40-character commit SHA with a version comment, matching this repo's established convention for every third-party action in the file (checkout, github-script, setup-node, setup-python, configure-pages, deploy-pages, etc. are all SHA-pinned).
- Neither new step declares its own `permissions:` block — they inherit the job-level `permissions` (`analyze`: `actions: read, contents: write, issues: write, models: read`; `generate`: `actions: read, contents: write`). `actions: read` is the minimum required scope for `download-artifact`/`upload-artifact` and was already present in both jobs before this PR (needed by the pre-existing `raw-data` and `analyzed-data`/`analysis-candidate` artifact steps). **No new permission was added or requested** by this change.
- `continue-on-error: true` on the download step is a resiliency choice for a missing artifact when `if-no-files-found: warn` finds no ledger to upload. The following step emits an explicit warning. This is not a security-relevant permission relaxation.

### 4. zizmor results

Ran `zizmor --persona=regular .github/workflows/crawl-and-publish.yml` on the PR branch (`fix/br009-ledger-commit-path-gap`, zizmor v1.23.1):

```
17 findings (2 ignored, 12 suppressed): 0 informational, 0 low, 3 medium, 0 high
```

All 3 medium findings are the pre-existing `secrets-outside-env` warning (secret accessed outside a dedicated GitHub Environment) at:
- line 520 (`COPILOT_GITHUB_TOKEN` in `analyze` job)
- line 660 (`COPILOT_GITHUB_TOKEN` in `analyze` job)
- line 1591 (`WEBHOOK_URL` in `notify` job)

None of these findings are near or related to the new `token-usage-ledger` upload/download steps (lines ~1038-1050, ~1107-1120).

Diffed against `main` (`git show main:.github/workflows/crawl-and-publish.yml`, same zizmor invocation): **identical** result — `17 findings (2 ignored, 12 suppressed): 0 informational, 0 low, 3 medium, 0 high`, same 3 `secrets-outside-env` findings (at the equivalent pre-PR line numbers 520, 660, 1564 — line numbers shift slightly because the PR adds lines earlier in the file, but it's the same 3 logical findings).

**Zizmor finding count and severity are unchanged by this PR — no new findings of any severity.**

### 5. Verdict

**ACCEPT.**

Reasoning:
- No new attack surface: workflow trigger is `schedule`/`workflow_dispatch` only (no fork-reachable event), and the artifact is produced/consumed within the same run — classic artifact-poisoning patterns (fork PR → artifact → privileged job) do not apply.
- No sensitive-data exposure: `token-usage.jsonl` contains only numeric/metadata fields (timestamps, token counts, cost, model name, run ID) and is already an established, already-public part of the `publish` branch; this PR only fixes silent data loss of the current run's row, it does not change what data class is committed.
- Both new steps are SHA-pinned consistent with 100% of the rest of the file's third-party action references, and request no permissions beyond what the jobs already had.
- `zizmor` confirms zero new findings of any severity vs. `main`.

## Concerns / Gaps

- None blocking. Minor, non-blocking observations only (see follow-ups).

## Recommended Follow-ups (non-blocking)

1. The 3 pre-existing `secrets-outside-env` medium findings (`COPILOT_GITHUB_TOKEN` x2, `WEBHOOK_URL` x1) are unrelated to this PR but remain open technical debt — consider a separate follow-up to move these to GitHub Environments if the team wants to drive the zizmor medium-finding count to zero. Not this PR's responsibility.
2. This PR (per its own description) only fixes the artifact-transport gap; it explicitly does **not** wire `scripts/generate_cost_summary.py` into the workflow. Confirm that remains tracked as a separate follow-up item (per repo memory note on BR-009), so reviewers don't conflate "ledger now survives" with "cost dashboard is now fed live data."
3. `if-no-files-found: warn` on the new upload step (rather than `error`) means a missing `token-usage.jsonl` (e.g. if `track_token_usage.py` failed silently upstream) would not fail the `analyze` job — acceptable given `continue-on-error: true` on the paired download, but worth confirming this matches intended fail-open semantics for non-`normal` run modes.

## Evidence / File References

- `.github/workflows/crawl-and-publish.yml` (lines 1-75: trigger/permissions; 335-341: `analyze` job header/permissions; 1038-1050: new upload step; 1053-1058: `generate` job header/permissions; 1107-1120: new download step; 1370-1390: commit step showing `data/metrics/` already part of `GENERATED_PATHS`/`ADD_PATHS`)
- `scripts/track_token_usage.py` (full file read; `build_record()` ~line 155, `append_record()` ~line 268)
- `origin/publish:data/metrics/token-usage.jsonl` (git show, confirms pre-existing public commitment of this file)
- zizmor v1.23.1 output, PR branch vs. `main` (identical: 17 findings, 3 medium, 0 high, both runs)
