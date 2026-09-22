# Issue 779 — Fry measurement and gate evidence

Date: 2026-09-22  
Role: Fry, Tester / QA  
Scope: scheduled runs W37 `34082521901`, W38 `34806779896`, and W39 `35561779454`

## QA verdict

**Gate evidence passes; measurement acceptance remains blocked.**

- All three retained final and per-attempt `analysis_gate` reports passed with zero
  structural/schema, editorial, evidence-citation, or AI-provenance errors and no
  repair actions.
- W38 and W39 declared and artifact-recorded `gpt-5.6-sol`. The retained Copilot
  logs do not expose `currentModel` or equivalent independent runtime model
  metadata, so the exact executed model is not log-observed.
- The retained ledger has one estimated `analysis` row per run. It has no
  synthesis row, per-call breakdown, cached-input count, cache-write count, or
  measured billing record. Per-agent token/cost/cache attribution is unavailable.
- The reported ledger comparison is arithmetically correct: W39 is **31.57%**
  more expensive than the W37 ledger row despite **1.30% fewer total estimated
  tokens**. However, W37 declared `gpt-5.5` while its ledger was priced as
  `copilot-default`/Sonnet. Repricing the same W37 estimates with the canonical
  `gpt-5.5` rates gives `$0.217700`; against that corrected baseline W38 is
  **26.48% cheaper** and W39 **26.60% cheaper**. Therefore the `+31.6%` figure is
  a truthful ledger-to-ledger comparison, but not a valid model-normalized
  gpt-5.5-versus-Sol cost conclusion.
- Configuration rollback is still two agent declaration edits. A consistent
  rollback PR should additionally update the workflow's gate/ledger attribution
  literals and the workflow-structure test, matching the four-file pattern used
  by PR #745.

## Authoritative sources

### GitHub

- Issue: https://github.com/jmservera/SquadScope/issues/779
- Upgrade PR: https://github.com/jmservera/SquadScope/pull/745
- Pricing PR: https://github.com/jmservera/SquadScope/pull/739
- Closed attribution-fix PR: https://github.com/jmservera/SquadScope/pull/740
- PRD archival PR: https://github.com/jmservera/SquadScope/pull/774
- W37 run: https://github.com/jmservera/SquadScope/actions/runs/34082521901
- W38 run: https://github.com/jmservera/SquadScope/actions/runs/34806779896
- W39 run: https://github.com/jmservera/SquadScope/actions/runs/35561779454

### Repository and retained artifacts

- `.github/workflows/crawl-and-publish.yml`
- `.github/agents/weekly-analysis.agent.md`
- `.github/agents/weekly-synthesis.agent.md`
- `scripts/analysis_gate.py`
- `scripts/model_pricing.py`
- `scripts/track_token_usage.py`
- `scripts/preflight_cost_check.py`
- `tests/test_track_token_usage.py`
- `tests/test_copilot_pricing_review.py`
- `docs/prds/weekly-agents-gpt-5-6-sol.md` (archived under `docs/processed/`
  when this evidence was collected)
- Retained `analysis-candidate`, `analyzed-data`, and `token-usage-ledger`
  artifacts downloaded from each run.

## 1. Run and gate outcomes

| Week | Run | Head SHA | Analyze job | Final gate | Structural/schema | Editorial | Evidence citation | AI provenance | Repair actions |
|---|---:|---|---|---|---|---|---|---|---|
| W37 | `34082521901` | `16b423d89fc6dd9f2860736a6c5c81b21a617921` | success | passed | passed, 0 errors | passed, 0 errors | passed, 0 errors | passed, 0 errors | none |
| W38 | `34806779896` | `ab3343388ea541ed4d53343bea417799f9def16b` | success | passed | passed, 0 errors | passed, 0 errors | passed, 0 errors | passed, 0 errors | none |
| W39 | `35561779454` | `a766faec5964efcbbe581ae7a9713f986f93fd21` | success | passed | passed, 0 errors | passed, 0 errors | passed, 0 errors | passed, 0 errors | none |

The final `analysis-gate-report.json` and
`diagnostics/gate-copilot-cli-attempt-0.json` agree for every run:

- `passed: true`
- `failure_class: "passed"`
- `errors_before_repair: []`
- `errors_after_repair: []`
- `repair_actions: []`
- all four named gate categories passed

The publish manifests independently embed the gate report, record validation
status `passed`, and list `analysis_gate` as passed. Each preflight manifest has
`degraded: true` because the prompt was deterministically compacted, but
`prompt_within_budget: true`, `publish_eligible: true`, and
`promotion_policy: "normal-promotion"`. That preflight state is not a gate
failure.

Gate quality details:

| Week | Words | Repo citations | Press citations | Quality components |
|---|---:|---:|---:|---|
| W37 | 1,414 | 24 | 5 | base 60, depth 15, evidence 10, press 15 |
| W38 | 1,342 | 15 | 5 | base 60, depth 15, evidence 10, press 15 |
| W39 | 1,399 | 21 | 5 | base 60, depth 15, evidence 10, press 15 |

## 2. Model identity: declared, observed, and recorded

| Week | Agent declarations at run SHA | Log-observed runtime model | Gate/manifest/ledger model |
|---|---|---|---|
| W37 | `weekly-synthesis`: `gpt-5.5`; `weekly-analysis`: `gpt-5.5` | **Unavailable.** Logs show `--agent weekly-synthesis` and `--agent weekly-analysis`, but no `currentModel`/usage metadata. | `copilot-default` |
| W38 | both agents: `gpt-5.6-sol` | **Unavailable.** No independent runtime model field retained. | `gpt-5.6-sol` |
| W39 | both agents: `gpt-5.6-sol` | **Unavailable.** No independent runtime model field retained. | `gpt-5.6-sol` |

Interpretation:

- The strongest evidence for W38/W39 is internally consistent configuration plus
  provenance artifacts: both agent frontmatters select Sol, the workflow invokes
  those agents without a `--model` override, and the gate, publish manifest, and
  ledger record Sol.
- This is not the same as runtime usage telemetry. Unlike the PRD's earlier
  controlled comparison, these scheduled runs did not retain
  `--usage-output-file` data with a `currentModel` field.
- W37 exposes a known attribution defect: both agent declarations were
  `gpt-5.5`, but the workflow passed/stored `copilot-default`. PR #740 documents
  that exact bug. Thus W37's artifact-recorded model is not reliable evidence of
  the executed model.
- Synthesis artifacts contain no model field. The publish manifest's model is an
  analysis-stage provenance label, not separate proof for both calls.

## 3. Usage, cost, input size, and latency

### Canonical retained ledger rows

These values are estimates, not provider-measured usage. Every row has
`estimated: true`. `track_token_usage.py` attempted transcript parsing, found no
recognized usage pattern, and fell back to approximately `characters / 4` for
the analysis prompt and final article.

| Week | Ledger model | Input tokens | Output tokens | Total | Cost USD | Credit-equivalent at $0.01/credit |
|---|---|---:|---:|---:|---:|---:|
| W37 | `copilot-default` | 25,210 | 3,055 | 28,265 | $0.121455 | 12.1455 |
| W38 | `gpt-5.6-sol` | 24,966 | 3,009 | 27,975 | $0.160044 | 16.0044 |
| W39 | `gpt-5.6-sol` | 24,884 | 3,013 | 27,897 | $0.159796 | 15.9796 |

The credit-equivalent uses the PRD's stated conversion, one AI credit =
`$0.01`; it is not a retained provider charge.

### Exact retained input file sizes and timing

| Week | Analysis rendered prompt | Analysis manifest estimate | Synthesis prompt | Synthesis output | Synthesis step wall time | Analysis-path duration |
|---|---:|---:|---:|---:|---:|---:|
| W37 | 101,599 bytes | 25,400 tokens | 42,978 bytes | 6,509 bytes | 42 s | 59 s |
| W38 | 100,429 bytes | 25,108 tokens | 43,569 bytes | 4,940 bytes | 35 s | 48 s |
| W39 | 99,984 bytes | 24,996 tokens | 43,592 bytes | 5,766 bytes | 31 s | 44 s |

Notes:

- Analysis-path duration is the workflow's exact emitted
  `duration_seconds`, covering the analysis retry loop, gate, and usage-record
  write; it is not isolated provider latency.
- Synthesis timing is the GitHub Actions step boundary and includes synthesis
  prompt preparation/CLI handling, so it is also not isolated provider latency.
- Exact per-agent input/output/cache tokens and per-agent cost are
  **unavailable**. File byte sizes and step wall times must not be treated as
  provider usage.
- Cached-input and cache-write counts are **unavailable** for all three runs.
  The ledger schema rows contain neither field and therefore price both as zero.
- The single ledger row must not be split or allocated between synthesis and
  analysis. The workflow only invokes `track_token_usage.py` after the analysis
  call and creates no synthesis usage record.

## 4. Canonical pricing attribution and comparable deltas

`scripts/model_pricing.py` defines:

- `copilot-default`: input `$3/M`, cached input `$0.30/M`, cache write
  `$3.75/M`, output `$15/M`
- `gpt-5.5` default tier: input `$5/M`, cached input `$0.50/M`, output `$30/M`
- `gpt-5.6-sol` default tier: input `$4/M`, cached input `$0.40/M`, cache
  write `$5/M`, output `$20/M`
- long-context threshold for GPT-5.5/Sol: input tokens greater than `272,000`

All three rows are below the long-context threshold. The canonical function is:

`(input * input_rate + cached_input * cached_rate + cache_write * cache_write_rate + output * output_rate) / 1_000_000`

rounded to six decimals. With no retained cache counts:

- W37 ledger: `(25,210 × 3 + 3,055 × 15) / 1M = $0.121455`
- W38: `(24,966 × 4 + 3,009 × 20) / 1M = $0.160044`
- W39: `(24,884 × 4 + 3,013 × 20) / 1M = $0.159796`

### Ledger-to-ledger comparison

| Comparison with W37 ledger | Input delta | Output delta | Total-token delta | Cost delta |
|---|---:|---:|---:|---:|
| W38 | -0.97% | -1.51% | -1.03% | **+31.77%** |
| W39 | -1.29% | -1.37% | -1.30% | **+31.57%** |

This confirms the issue comment's stated approximately **31.6%** W39 increase.
It occurs because the W37 row used the cheaper Sonnet-compatible
`copilot-default` rate profile, not because Sol consumed more estimated tokens.

### Model-corrected comparison

W37's declarations show GPT-5.5. Repricing its same estimates using the
canonical GPT-5.5 default rates gives:

`(25,210 × 5 + 3,055 × 30) / 1M = $0.217700`

| Comparison with corrected W37 GPT-5.5 estimate | Cost delta |
|---|---:|
| W38 Sol `$0.160044` | **-26.48%** |
| W39 Sol `$0.159796` | **-26.60%** |

Therefore:

1. `$0.121455` is the authoritative retained W37 ledger value.
2. `+31.6%` is mathematically correct for the retained rows.
3. It is not a sound gpt-5.5 baseline comparison because W37 was misattributed.
4. The corrected estimate suggests Sol was cheaper for these file-size
   estimates, but it still is not measured billing and excludes synthesis/cache
   usage.

An additional consistency defect is visible in W38/W39 logs:
`preflight_cost_check.py` was invoked without `--model`, so its notice used the
default `copilot-default` profile (`$0.1049`/`$0.1047`). That preflight notice is
not the canonical final ledger cost and should not be used for this comparison.

## 5. Rollback scope

The behavior-selecting rollback remains exactly two model declaration edits:

1. `.github/agents/weekly-analysis.agent.md`
2. `.github/agents/weekly-synthesis.agent.md`

Both would change `model: gpt-5.6-sol` back to `model: gpt-5.5`.

For internally consistent gate provenance, cost attribution, comments, and
tests, a rollback PR should also edit:

3. `.github/workflows/crawl-and-publish.yml` — gate model argument,
   `ANALYSIS_MODEL`, and explanatory comment.
4. `tests/test_pipeline.py` — workflow literal expectation/regression guard.

PR #745 used this same four-file shape: two effective agent declarations plus
workflow/test consistency surfaces. No data migration, schema change, prompt
change, or interface change is required.

## 6. Acceptance gaps

| Acceptance evidence | Status | Blocking gap |
|---|---|---|
| Representative post-upgrade run for both weekly agents | Partial | W38/W39 configuration and artifacts consistently say Sol, but no retained runtime `currentModel` field independently confirms either call. |
| `analysis_gate.py` passes without structural/schema/editorial/provenance failure | **Satisfied** | None for W37/W38/W39. |
| Per-agent input/output/cache tokens, AI-credit cost, input size, and latency | **Blocked** | No synthesis usage row; no per-call usage output; no cache counts; no isolated provider latency. Only input file sizes and step durations survive. |
| Comparable first-call cost against GPT-5.5 baseline | **Blocked** | W37 is artifact-priced as `copilot-default` despite declared GPT-5.5; all ledger tokens are estimates and synthesis/cache usage is absent. |
| Rollback remains two-file declaration change | **Satisfied with consistency caveat** | Effective model selection is two files; workflow/test attribution should accompany rollback. |

The gate criterion is authoritative and complete. The per-agent measurement and
model-normalized baseline cost criteria cannot be accepted from the retained
scheduled-run evidence alone.

## Commands used

Commands were run from `/home/azureuser/source/SquadScope-779`; downloaded
evidence was stored outside the worktree in the Copilot session folder.

```bash
gh issue view 779 --repo jmservera/SquadScope \
  --json number,title,body,state,labels,comments,url,createdAt,updatedAt

gh pr view 745 --repo jmservera/SquadScope \
  --json number,title,body,state,mergedAt,mergeCommit,commits,files,reviews,url

gh run view RUN_ID --repo jmservera/SquadScope \
  --json databaseId,createdAt,startedAt,updatedAt,url,headSha,jobs

gh api repos/jmservera/SquadScope/actions/runs/RUN_ID/artifacts

gh run download RUN_ID --repo jmservera/SquadScope --dir RUN_ID

gh run view RUN_ID --repo jmservera/SquadScope --job ANALYZE_JOB_ID --log

git show RUN_SHA:.github/agents/weekly-synthesis.agent.md
git show RUN_SHA:.github/agents/weekly-analysis.agent.md
git show RUN_SHA:.github/workflows/crawl-and-publish.yml

git log --follow --format='%H %ad %s' --date=iso -- \
  docs/processed/weekly-agents-gpt-5-6-sol.md

python3 - <<'PY'
from scripts.model_pricing import estimate_cost_usd, get_model_rate
for model, input_tokens, output_tokens in [
    ("copilot-default", 25210, 3055),
    ("gpt-5.5", 25210, 3055),
    ("gpt-5.6-sol", 24966, 3009),
    ("gpt-5.6-sol", 24884, 3013),
]:
    print(
        model,
        get_model_rate(model, input_tokens),
        estimate_cost_usd(model, input_tokens, output_tokens),
    )
PY
```

Relevant analyze job IDs:

- W37: `101621166615`
- W38: `103861103072`
- W39: `106216691867`
