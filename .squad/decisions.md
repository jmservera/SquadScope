# Run 27055543722 — Analysis Failure Root Cause & Diagnosis [2026-06-06]

## Executive Summary

Workflow run 27055543722 confirmed persistent analysis failures traced to **AI output contract inconsistency**, **deterministic retry loops**, and **unavailable fallback**. The crawler was healthy; analysis failed deterministically after ~25 minutes across all Copilot attempts, falling through to no-AI fallback which the safety manifest correctly blocked.

## Consolidated Root Causes (Ranked by Confidence)

### 1. Prompt/Spec/Gate Schema Drift — Very High Confidence
- `prompts/analyze-weekly.md` and `docs/analysis-spec.md` specify predictions as `{repo, direction, confidence}`
- `scripts/analysis_gate.py` requires `predictions[].claim_type in {signal, noise, gap}`
- Run 27030646485: All 3 Copilot attempts failed on `predictions[*].claim_type must be one of signal, noise, gap`
- Run 27055543722: Same deterministic failure across all 3 attempts
- **Immediate action:** Align contract; update gate or prompt to match

### 2. Context Bloat & Undercounted Preflight — Very High Confidence
- Preflight estimates: ~74k tokens (raw JSON + skills only)
- Actual final ledger: ~113k tokens (preflight + template + identity/wisdom + prior summary + press context + agent wrapper)
- Gap of ~39k tokens (38% undercount) dilutes model attention
- Renders skills payload (~45.8 KB / 11.4k tokens) contains unrelated operational/design skills, not analysis-specific
- **Immediate action:** Render exact prompt before preflight; use analysis-specific wisdom capsule

### 3. Blind Deterministic Retry Loop — Very High Confidence
- Three full Copilot attempts (9-11 min each) repeated identical flawed prompt
- No gate-error classification or deterministic repair (e.g., timestamp/schema normalization)
- Retries waste 25-29 minutes, then fall through to no-AI
- **Immediate action:** Classify gate failures; repair frontmatter once; fail-fast on systematic errors

### 4. Unavailable AI Fallback — High Confidence
- GitHub Models configured to `openai/gpt-4o` → `403 no_access` on both runs
- No fallback to accessible model; pipeline jumps directly to no-AI
- **Immediate action:** Preflight model access before expensive Copilot attempts

### 5. No-AI Fallback Provenance Not Enforced — High Confidence
- `analysis_gate.py` checks structure only, not provenance
- No-AI output (quality_score 62, self-referential language) passed structural gate
- Run 27030646485: No-AI published despite existing AI article from previous week
- **Immediate action:** Enforce no-AI publish-blocking in manifest (already done in #249); add to diagnostics

### 6. Weak Evidence/Citation Validation — Medium-High Confidence
- Gate does not validate repo-link coverage (every mentioned repo must be `[owner/repo](url)`)
- Gate does not validate press citation integrity or that links resolve to retained articles
- No-AI fallback uses raw descriptions without editorial curation

### 7. Learned Context Overhead & Agent Wrapper — Medium-High Confidence
- Workflow calls `copilot --agent squad` for publication analysis
- Squad agent adds routing/delegation instructions on top of the rendered prompt
- Flat skills bundle mixes unrelated squad operational skills with analysis context

## Recommended Immediate Fixes

### 1. Align Prediction Contract (Blocker for Next Run)
- **Decision:** Require `claim_type in {signal, noise, gap}` (supports hindsight classification)
- **Actions:**
  - Update `docs/analysis-spec.md` and `prompts/analyze-weekly.md` to specify predictions as `{repo, claim_type, direction, confidence}`
  - Add contract-drift test: parse docs/prompt/gate and assert matching prediction schema
  - Add regression fixtures for bad-date and prediction-shape errors

### 2. Deterministic Frontmatter & Repair Loop
- **Actions:**
  - Precompute and mechanically inject `date`, `week`, `year`, `repos_featured`, `stars_tracked`
  - Add focused repair prompt for gate failures (classifies errors; repairs timestamp/schema once)
  - Fail-fast if error is systematic; do not retry if only deterministic fields are wrong

### 3. Exact Rendered Prompt Preflight
- **Actions:**
  - Build `analysis-input-manifest.json` with component byte/token counts
  - Render exact prompt (template + raw JSON + wisdom + skills + press context + prior summary)
  - Compare rendered-prompt estimate to final ledger; fail or compact if gap > 10%

### 4. Analysis-Specific Wisdom Capsule
- **Actions:**
  - Replace full learned-context injection with `{{EDITORIAL_WISDOM_CAPSULE}}` (~1-2k tokens max)
  - Select only analysis-relevant learnings; exclude operational/design/PR workflow skills
  - Keep prior-week continuity notes (~500 tokens) for editorial context

### 5. GitHub Models Access Preflight
- **Actions:**
  - Add fast `models-health` check before Copilot attempts
  - If configured model is inaccessible, switch to known-good fallback or mark unavailable up front
  - Record provider/model/access status in `models-health.json` artifact

### 6. No-AI as Diagnostic Only
- **Actions:**
  - Keep no-AI fallback for diagnostics/artifact purposes
  - Tag as `diagnostic_no_ai_candidate` (not fallback recovery)
  - Ensure manifest blocks promotion unless explicit force flag is set
  - Do not let no-AI replace existing good AI article

### 7. Direct Analyzer Invocation
- **Actions:**
  - Stop calling `--agent squad` for publication analysis
  - Use plain Copilot CLI or minimal analyzer agent (Farnsworth-only)
  - Remove squad routing/delegation context from analysis prompt

## Map/Reduce Status

**Hold for now.** Map/reduce remains dry-run candidate only after immediate fixes land. The signal-type claim-ledger architecture is sound but adding a second pipeline before deterministic contract/repair/preflight are solid risks masking the same root causes across more calls.

## Observability to Add

- `analysis-input-manifest.json`: component token counts by segment
- `analysis-attempts.jsonl`: per-attempt provider, model, duration, gate errors, failure class
- `models-health.json`: endpoint, model, access status, fallback selected
- `gate-report.json`: structured `analysis_gate.py` output
- Persist failed candidates under `data/candidates/{week}/{run_id}/` for reproduction

## Acceptance Criteria for Next Run

1. ✅ Prediction contract aligned across docs, prompt, gate
2. ✅ Exact rendered-prompt preflight within 10% of final ledger
3. ✅ Deterministic frontmatter/schema failures do not trigger full retries
4. ✅ GitHub Models access is preflighted or marked unavailable
5. ✅ No-AI manifest blocks promotion unless existing AI article is gone
6. ✅ Final markdown passes both structural and evidence-citation gates
7. ✅ Attempt artifacts retained for root-cause analysis

## Cross-Team Notes

- **Farnsworth:** Comprehensive root-cause diagnosis and process proposal documented
- **Bender:** Pipeline failure mechanics, contract mismatch, context bloat analysis
- **Fry:** QA test fixtures, gate/spec alignment, publish protection test plan, rollout phases
- **Leela:** Issue hierarchy (#248-#261), GitHub creation/updates, PR #245 safety review

## Related Issues

- #248 — Parent epic: protect published analysis from unsafe reruns
- #249 — Publish eligibility manifest with no-AI blocking (✅ safety gate worked this run)
- #255 — Strengthen publish gate beyond structural validation
- #256 — Deterministic preflight compaction and fallback policy
- #265 — Triaged run 27055543722 as real P0 analysis bug
- #266 — New immediate P0 child for contract alignment and deterministic repair

---

---

## Run 27056632166 — Successful analysis and publish cycle

**Date:** 2026-06-06T07:43:44.173+00:00  
**Run:** #27056632166  
**Status:** ✅ End-to-end success: Copilot analysis passed; publish manifest decision promoted; generate/deploy succeeded; notify skipped (publish_release=false)

### Key outcomes

- **Analysis:** Copilot-only path completed successfully with prediction schema aligned and gate passing
- **Publish decision:** Manifest promotion confirmed eligibility; run 27055543722 overwrite-protection validated
- **Deploy:** Content and weekly page generated and deployed to main
- **PRs merged:** #267, #268, #271, #272 integrated into main

### Related PRs and commits

- **#267** (QA guard prediction schema repair loop): Fixed schema mismatch between prediction format and `analysis_gate.py` requirement; validated with regression tests
- **#268** (Copilot-only analysis): Made weekly analysis Copilot-only with failure classifier and token-renewal issue handling
- **#271** (Exclude squad state from publish sync): Fixed publish sync to exclude .squad directory
- **#272** (Sync publish data to main): Successfully synced generated content and data to main

### Failure classification and handling

- **Run 27055543722 failure** (safely blocked): No-AI blocked by publish manifest; no overwrite occurred
- **Immediate action:** Created issue for Copilot token renewal if needed; classified failures by cause (inaccessible, token, context, timeout, transient, other)

### Analysis insights

- Analysis time: ~28m41s with initial Copilot attempts
- Token usage: ~112.9k estimated input tokens
- Crawl/news: Healthy; no performance issues
- Press context: Capped at ~8k tokens; working as designed
- Key learning: Schema contract discipline prevents retry cascade

### Follow-up PRs and decisions

- **#269** (closed as unsafe): Would have regressed .squad state; closed per safety policy
- **#270** (closed): Superseded by #271 and #272
- **#271 & #272** (merged): Safely synced generated content and squad state exclusion

### Decision summary

1. ✅ Copilot analysis Copilot-only when GitHub Models/OpenAI unavailable
2. ✅ Token failures fail immediately with issue creation for renewal
3. ✅ Transient failures retry; eventually fail for rerun
4. ✅ Publish manifest blocks unsafe reruns effectively
5. ✅ No-AI candidates tagged diagnostic, not as fallback recovery
6. ✅ Schema contract alignment prevents retry cascade

### Model research outcome

Model recommendations from #268 analysis:
- **GPT-5.5**: Best choice for high-reasoning coding/editorial (high cost)
- **GPT-5.3-Codex / Sonnet**: Routine coding tasks
- **Haiku / GPT mini**: Mappers and Scribe tasks
- **Cross-family rubber-duck reviews**: Recommended for code quality

---

## Analysis Decomposition Feasibility & Architecture

**Authors:** Bender (Crawler & Data Collector), Farnsworth (Content Curator), Fry (QA)  
**Date:** 2026-06-05T20:57:09.910+00:00  
**Status:** Recommendation finalized; proceeding post-safety layer

### Executive recommendation

**Adopt hierarchical claim-ledger map/reduce pipeline with signal-type mappers as MVP**, deterministic retrieval/compaction before every LLM call, and single reducer/final writer responsible for global thesis and reader-facing prose.

**Best candidate:** deterministic preflight/compaction + signal-type claim-ledger mappers + reducer/editorial-plan + single final writer, run as non-publishing dry-run until rerun safety layer (#248-#259) is complete.

### Why this architecture wins

1. **Uses existing artifacts:** `data/raw/{week}.json`, `data/raw/{week}-external-news.json`, `data/analyzed/{week}-correlations.json`, rendered press context, prior summaries, token/cost telemetry
2. **Deterministic slicing:** Matches current data contracts (`new_repos`, `trending_repos`, `press_correlations`, `prior_continuity`)
3. **Minimal new machinery:** No embeddings, vector store, source-specific model swarm, or GitHub crawl matrix needed for MVP
4. **Targets measured problem:** Analysis was ~28m41s with three failed Copilot gates and ~112.9k tokens; crawl/news healthy
5. **Preserves quality:** Mappers emit cited JSON ledgers; reducer/final writer owns article voice; must pass `analysis_gate.py` + evidence-contract validator

### Rejected alternatives

- **Source-specific news mappers:** Low MVP value; defer until source heterogeneity demands isolation
- **Independent full analyses + comparer:** Poor context hygiene; multiplies cost without improving provenance; acceptable only for human A/B during dry-run
- **Repo clusters first:** Risky without stable cluster IDs, overlap policy, and coverage accounting; phase 2 after deterministic topic/language sidecars

### MVP mappers (signal-type)

1. `signal-type:new-repos` — novelty, launch quality, repo clusters within discoveries
2. `signal-type:trending-repos` — momentum, star gains, established anchors, noise
3. `signal-type:press-correlations` — strong/weak alignment, divergence, source caveats
4. `signal-type:prior-continuity` — prior predictions, reversals, follow-through

### Deterministic compaction (MVP, improves current path)

**Before map/reduce:**
- Preflight computes authoritative totals, repo/article inventories, sizes, token estimates, source status, top candidates
- Emit compact per-slice evidence with: `full_name`, `url`, `description`, `language`, `topics`, `stars`, `stars_gained`, `created_at`, plus source/correlation metadata
- Remove repeated raw JSON, skills, boilerplate; keep untrusted evidence delimiters
- Cap press context; pass machine-readable correlation/article citations to press mapper

**Avoid for MVP:**
- Embeddings/vector retrieval
- LLM choosing retrieval without deterministic coverage ledger
- Raw README fetching unless explicitly bounded and cached

### Data contracts (MVP minimum)

1. **Shared run context:** `run_id`, `week`, `current_datetime`, `raw_sha256`, `external_news_sha256`, `correlations_sha256`, `code_sha`, created timestamp
2. **Preflight manifest:** Authoritative repos/counts/stars tracked, source coverage, citation inventory, token estimates by segment, slice definitions
3. **Mapper output:** `analysis_map_v1` JSON with shard_id, input_refs, token estimate, coverage, claims/findings, citations, confidence, uncertainties, contradictions, status, model/provider, duration, errors
4. **Reducer input:** Only preflight manifest + validated mapper ledgers + compact global metadata
5. **Reducer output:** `analysis_editorial_plan_v1` with selected claims, citation bindings, rejected claims, contradictions, quality notes, title/top_repo/tags
6. **Final writer output:** Existing markdown contract only; no mapper prose seams
7. **Evidence validation:** Final repo/press links must resolve to inventories/ledgers before `analysis_gate.py` passes

### Fan-in failure policy

- **Missing raw GitHub/preflight:** Fail closed
- **Missing required mapper (new_repos, trending_repos):** Fall back to current path
- **Missing optional mapper (press/prior):** Allowed with explicit degraded note and source caveat
- **Malformed mapper JSON/citations/week mismatch:** Reject and fail/degrade per shard criticality
- **Reducer over budget:** Compact or hierarchical reduce before model call
- **Final gate/evidence validation failure:** Do not publish map/reduce; preserve good article per #248-#259

### Token/runtime baseline

Known baseline:
- Final observed: ~112.9k input tokens / ~119.6k total
- Preflight estimated: ~74.3k
- Press context: ~8k tokens (capped)
- Wall time: ~28m41s across three Copilot attempts

Expected MVP budget shape:
- Preflight/manifest: deterministic, no model call
- new_repos mapper: 15k-25k input tokens
- trending_repos mapper: 15k-25k input tokens
- press_correlations mapper: 8k-12k input tokens
- prior_continuity mapper: 3k-8k input tokens
- Reducer/editorial plan: 10k-20k input tokens
- Final writer: 8k-15k input tokens

**Acceptance target:** max per-call context reduction >=30% first, then total token/runtime improvement after prompt boilerplate is compacted.

### QA validation strategy

1. Deterministic preflight: test week/checksum mismatch, missing citations, malformed mapper output, duplicates, contradictions, over-budget reduce input
2. Mapper ledgers: test claims/citations coverage, confidence/uncertainty preservation, contradiction sidecars
3. Reducer: test editorial plan quality, claim bindings, rejected-claim reasons
4. Final writer: test markdown contract, citation provenance, gate pass/fail, evidence validator pass/fail
5. Rerun stability: compare same-input reruns for top_repo/key-reference overlap before default-on
6. A/B against current path: gate pass, citation coverage, unsupported claims, max per-call tokens, total tokens, wall time, fallback count

### Staged MVP after #248-#259

**Stage A — Contracts and deterministic preflight**
- Add schemas/validators for preflight, mapper ledgers, reducer input, editorial plan, evidence validation
- Build compact deterministic slices from existing artifacts
- Add fixture tests for week/checksum mismatch, missing citations, malformed mapper, duplicates, contradictions, over-budget reduce

**Stage B — Local/no-publish map/reduce dry-run**
- Implement four signal-type mappers as claim-ledger producers
- Reducer emits editorial plan and rejected/contradiction sidecars
- Final writer emits candidate markdown
- Run `analysis_gate.py` and evidence validator; do not publish as canonical

**Stage C — CI A/B mode (4 weekly cycles)**
- Add workflow_dispatch flag and scheduled dry-run for replay fixtures
- Upload artifacts/metrics; compare against current source-of-truth

**Stage D — Guarded promotion (after A/B success)**
- Candidate into staged publish eligibility manifest only after: existing gate passes, evidence validator zero missing citations, max per-call context drops >=30%, no publish failure increase, no quality regression, fallback available

### Decision

Proceed with **signal-type map/reduce + deterministic compaction** as safest and highest-leverage candidate after safety epic. Treat source-specific maps, repo clusters, hierarchical reduce as later scale tools.

---

## Issue #249 — Candidate staging and publish manifest

**Author:** Bender  
**Status:** ✅ Implemented in run 27056632166

Weekly analysis candidates are now staged under `data/candidates/<week>/<run_id>/` and promoted to `data/analyzed/<week>-summary.md` only after `publish_eligibility_v1` manifest confirms eligibility.

**Rationale:** Makes failed, degraded, stale-evidence-backed, and no-AI candidates debuggable without overwriting good published articles. Promotion jobs verify candidate/source checksums, AI provenance, analysis gate status, source freshness, and promotion decision.

**Follow-ups:** Future safe-rerun and same-day reuse work can add explicit per-source reuse markers to manifest; current manifests default missing reuse metadata to `not_reused` for visibility rather than inference.

---

## Issue #266 — Analysis contract repair

**Author:** Farnsworth  
**Date:** 2026-06-06T07:19:25Z  
**Status:** ✅ Fixed in PR #267

**Context:** Run 27055543722 failed repeatedly because prompt/spec showed legacy prediction frontmatter while `analysis_gate.py` required `claim_type`.

**Decision:** Treat `predictions[]` as `{repo, claim_type, direction, confidence}` everywhere. Allow only audited deterministic metadata/schema repairs before gate validation. Persist gate reports and candidate snapshots per attempt.

**Rationale:** Repeating full generation on deterministic schema drift wastes AI attempts and risks no-AI fallback pressure against the product north star of high-quality AI-authored analysis.

---

## Issue #257 — Rerun protection and regression tests

**Author:** Fry  
**Date:** 2026-06-05T21:16:49Z  
**Parent:** #248  
**Status:** ✅ Merged in main

Added small deterministic promotion-guard helper and regression tests for publish eligibility contract while #249 staging/manifest work proceeded in parallel.

**Quality rule captured:** A normal rerun may promote only from `data/staging/` with valid `publish_eligibility_v1` manifest, AI-authored non-degraded provenance, passing analysis/editorial/evidence gates, and fresh or explicitly same-day-reused source artifacts. Missing, malformed, stale, failed, degraded, or no-AI candidates are blocked and written to diagnostics without touching canonical weekly summary/content.

**Validation:** ✅ Local validation passed with `PYTHONPATH=. .tools/venv/bin/python -m pytest tests -q` (581 passed).

---

## Copilot analysis directive

**By:** jmservera (via Copilot)  
**Date:** 2026-06-06T07:43:44.173+00:00  
**Status:** ✅ Implemented

**What:** GitHub Models/OpenAI fallback is not configured for this repository. Workflow analysis must use GitHub Copilot as the AI path. If Copilot analysis fails, classify the cause:
- Copilot inaccessible / token failure → fail immediately; create/update issue for token renewal assigned to repo owner
- Context too large → record in diagnostics; fall back only after safety layer ready
- Timeout → classify as transient
- Transient error → use existing retry procedure; can eventually fail for later rerun
- Other → classify and record

**Captured for team memory:** User request that prioritizes Copilot reliability and token lifecycle management over automatic fallback.


---

## Run 27056632166 — Successful analysis and publish cycle

**Date:** 2026-06-06T07:43:44.173+00:00
**Run:** #27056632166
**Status:** ✅ End-to-end success: Copilot analysis passed; publish manifest decision promoted; generate/deploy succeeded; notify skipped (publish_release=false)

### Key outcomes

- **Analysis:** Copilot-only path completed successfully with prediction schema aligned and gate passing
- **Publish decision:** Manifest promotion confirmed eligibility; run 27055543722 overwrite-protection validated
- **Deploy:** Content and weekly page generated and deployed to main
- **PRs merged:** #267, #268, #271, #272 integrated into main

### Related PRs and commits

- **#267** (QA guard prediction schema repair loop): Fixed schema mismatch between prediction format and analysis_gate.py requirement; validated with regression tests
- **#268** (Copilot-only analysis): Made weekly analysis Copilot-only with failure classifier and token-renewal issue handling
- **#271** (Exclude squad state from publish sync): Fixed publish sync to exclude .squad directory
- **#272** (Sync publish data to main): Successfully synced generated content and data to main

### Failure classification and handling

- **Run 27055543722 failure** (safely blocked): No-AI blocked by publish manifest; no overwrite occurred
- **Immediate action:** Created issue for Copilot token renewal if needed; classified failures by cause

### Analysis insights

- Analysis time: ~28m41s with initial Copilot attempts
- Token usage: ~112.9k estimated input tokens
- Crawl/news: Healthy; no performance issues
- Press context: Capped at ~8k tokens; working as designed
- Key learning: Schema contract discipline prevents retry cascade

---

## Analysis Decomposition Feasibility & Architecture

**Authors:** Bender, Farnsworth, Fry
**Date:** 2026-06-05T20:57:09.910+00:00
**Status:** Recommendation finalized; proceeding post-safety layer

### Executive recommendation

Adopt hierarchical claim-ledger map/reduce pipeline with signal-type mappers as MVP with deterministic retrieval/compaction and single reducer/final writer.

**Best candidate:** deterministic preflight/compaction + signal-type claim-ledger mappers + reducer/editorial-plan + single final writer, run as non-publishing dry-run until rerun safety layer (#248-#259) is complete.

### Why this architecture wins

1. Uses existing artifacts without new infrastructure
2. Deterministic slicing matches current data contracts
3. Targets measured problem: 28m41s analysis with three failed gates, ~112.9k tokens
4. Preserves quality: mappers emit cited JSON ledgers; reducer/writer owns voice
5. Maintains fallback path until proven

### MVP mappers (signal-type)

1. signal-type:new-repos — novelty, launch quality, repo clusters within discoveries
2. signal-type:trending-repos — momentum, star gains, established anchors, noise
3. signal-type:press-correlations — strong/weak alignment, divergence, source caveats
4. signal-type:prior-continuity — prior predictions, reversals, follow-through

### Token/runtime baseline

Known baseline:
- Final observed: ~112.9k input tokens / ~119.6k total
- Preflight estimated: ~74.3k
- Press context: ~8k tokens (capped)
- Wall time: ~28m41s across three Copilot attempts

Expected MVP budget shape:
- Preflight/manifest: deterministic, no model call
- new_repos mapper: 15k-25k input tokens
- trending_repos mapper: 15k-25k input tokens
- press_correlations mapper: 8k-12k input tokens
- prior_continuity mapper: 3k-8k input tokens
- Reducer/editorial plan: 10k-20k input tokens
- Final writer: 8k-15k input tokens

**Acceptance target:** max per-call context reduction >=30% first, then total token/runtime improvement after prompt boilerplate is compacted.

### Staged MVP after #248-#259

**Stage A:** Contracts and deterministic preflight
**Stage B:** Local/no-publish map/reduce dry-run
**Stage C:** CI A/B mode (4 weekly cycles)
**Stage D:** Guarded promotion (after A/B success)

---

## Issue #249 — Candidate staging and publish manifest

**Author:** Bender
**Status:** ✅ Implemented in run 27056632166

Weekly analysis candidates are now staged under `data/candidates/<week>/<run_id>/` and promoted only after `publish_eligibility_v1` manifest confirms eligibility.

**Rationale:** Makes failed/degraded/stale candidates debuggable without overwriting good published articles. Promotion jobs verify candidate/source checksums, AI provenance, analysis gate status, and source freshness.

---

## Issue #266 — Analysis contract repair

**Author:** Farnsworth
**Date:** 2026-06-06T07:19:25Z
**Status:** ✅ Fixed in PR #267

**Decision:** Treat predictions as {repo, claim_type, direction, confidence} everywhere. Allow only audited deterministic metadata/schema repairs before gate validation.

**Rationale:** Repeating full generation on deterministic schema drift wastes AI attempts and risks no-AI fallback pressure.

---

## Issue #257 — Rerun protection and regression tests

**Author:** Fry
**Date:** 2026-06-05T21:16:49Z
**Status:** ✅ Merged in main

**Quality rule captured:** A normal rerun may promote only from data/staging/ with valid publish_eligibility_v1 manifest, AI-authored non-degraded provenance, passing gates, and fresh or explicitly same-day-reused source artifacts.

**Validation:** ✅ Local validation passed; 581 tests passed.

---

## Copilot analysis directive

**By:** jmservera
**Date:** 2026-06-06T07:43:44.173+00:00
**Status:** ✅ Implemented

**What:** GitHub Models/OpenAI fallback not configured. Workflow analysis must use Copilot. If Copilot fails, classify cause:
- Token failure: fail immediately, create issue for renewal
- Copilot inaccessible: fail with diagnostic
- Context too large: record; fall back post-safety layer
- Timeout: classify as transient, retry
- Transient error: use existing retry; eventually fail for rerun
- Other: classify and record


---

## Run 27056632166 — Successful analysis and publish cycle

**Date:** 2026-06-06T07:43:44.173+00:00
**Run:** #27056632166
**Status:** ✅ End-to-end success: Copilot analysis passed; publish manifest decision promoted; generate/deploy succeeded; notify skipped (publish_release=false)

### Key outcomes

- **Analysis:** Copilot-only path completed successfully with prediction schema aligned and gate passing
- **Publish decision:** Manifest promotion confirmed eligibility; run 27055543722 overwrite-protection validated
- **Deploy:** Content and weekly page generated and deployed to main
- **PRs merged:** #267, #268, #271, #272 integrated into main

### Decision summary

1. ✅ Copilot analysis Copilot-only when GitHub Models/OpenAI unavailable
2. ✅ Token failures fail immediately with issue creation for renewal
3. ✅ Transient failures retry; eventually fail for rerun
4. ✅ Publish manifest blocks unsafe reruns effectively
5. ✅ Schema contract alignment prevents retry cascade

---

## Issue #249 — Candidate staging and publish manifest

**Author:** Bender
**Status:** ✅ Implemented in run 27056632166

Weekly analysis candidates are now staged under `data/candidates/<week>/<run_id>/` and promoted only after `publish_eligibility_v1` manifest confirms eligibility.

---

## Issue #266 — Analysis contract repair

**Author:** Farnsworth
**Date:** 2026-06-06T07:19:25Z
**Status:** ✅ Fixed in PR #267

**Decision:** Treat predictions as {repo, claim_type, direction, confidence} everywhere. Allow only audited deterministic metadata/schema repairs before gate validation.

---

## Issue #257 — Rerun protection and regression tests

**Author:** Fry
**Date:** 2026-06-05T21:16:49Z
**Status:** ✅ Merged in main

**Quality rule:** A normal rerun may promote only from data/staging/ with valid publish_eligibility_v1 manifest, AI-authored non-degraded provenance, passing gates, and fresh or explicitly same-day-reused source artifacts.

---

## Analysis Decomposition Recommendation

**Authors:** Bender, Farnsworth, Fry
**Date:** 2026-06-05T20:57:09.910+00:00
**Status:** Recommendation finalized; proceeding post-safety layer

### Executive recommendation

Adopt hierarchical claim-ledger map/reduce pipeline with signal-type mappers as MVP with deterministic retrieval/compaction and single reducer/final writer. Run as non-publishing dry-run until rerun safety layer (#248-#259) is complete.

### MVP mappers (signal-type)

1. signal-type:new-repos — novelty, launch quality, repo clusters within discoveries
2. signal-type:trending-repos — momentum, star gains, established anchors, noise
3. signal-type:press-correlations — strong/weak alignment, divergence, source caveats
4. signal-type:prior-continuity — prior predictions, reversals, follow-through

### Token/runtime baseline

- Final observed: ~112.9k input tokens / ~119.6k total
- Preflight estimated: ~74.3k
- Press context: ~8k tokens (capped)
- Wall time: ~28m41s

Expected MVP budgets:
- Preflight/manifest: deterministic, no model call
- Per-mapper: 15k-25k (new/trending); 8k-12k (press); 3k-8k (prior)
- Reducer: 10k-20k input tokens
- Final writer: 8k-15k input tokens

**Acceptance target:** max per-call context reduction >=30% first.

### Staged MVP after #248-#259

**Stage A:** Contracts and deterministic preflight (improves current path)
**Stage B:** Local/no-publish map/reduce dry-run
**Stage C:** CI A/B mode (4 weekly cycles)
**Stage D:** Guarded promotion (after A/B success)

---

## Copilot analysis directive

**By:** jmservera
**Date:** 2026-06-06T07:43:44.173+00:00
**Status:** ✅ Implemented

Workflow analysis must use Copilot (GitHub Models/OpenAI not configured). On failure, classify cause:
- Token failure: fail immediately, create issue for renewal
- Copilot inaccessible: fail with diagnostic
- Context too large: record; fall back post-safety layer
- Timeout: classify as transient, retry
- Transient error: use existing retry; eventually fail for rerun
- Other: classify and record
