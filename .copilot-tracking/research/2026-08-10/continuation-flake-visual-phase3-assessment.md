<!-- markdownlint-disable-file -->

# Continuation Assessment: Flake Fix, Visual Baseline, Phase 3 (2026-08-10)

This records findings for the three Suggested Next Work items from the prior
session that were investigated but NOT code-changed in this session, per
`continue=all`. Item 1 (ledger commit-path gap) was implemented as PR #701;
see `.copilot-tracking/changes/2026-08-10/br009-ledger-commit-path-gap-changes.md`.

## Item 2: `test_atomic_publish_proof_integration` flake — root cause found, no fix applied

Traced the exact failure path by extracting the real commit-step shell via
`scripts.atomic_publish_proof.extract_commit_step` and reading it in full.
The failure ("No promoted analysis or generated Observatory changes to
commit.") fires at this guard in the extracted script:

```sh
if ! git status --short -- "${GENERATED_PATHS[@]}" | grep -q .; then
  echo "No promoted analysis or generated Observatory changes to commit."
  ...
  exit 0
fi
```

Root cause: `_select_manifest()` in `scripts/atomic_publish_proof.py` always
picks the **latest** eligible manifest under `data/candidates/*/*/publish-manifest.json`.
The proof's "normal" scenario promotes that same manifest into a repo already
hydrated from `origin/publish`. When the real production pipeline has already
published that exact week for real (confirmed: `origin/publish`'s tip is
`publish: weekly article transaction 2026-W32 [run #30782430176]`, dated
2026-08-03 — the same week the proof's manifest selection resolves to), the
simulated "candidate" content is byte-identical to what's already checked out
from `publish`, so re-promoting it produces zero diff and the guard correctly
(from the script's own perspective) reports nothing to commit.

This is a **steady-state condition**, not a git race: whenever `main` and
`publish` are already in sync for the latest real candidate week — the common
case between scheduled runs — this proof's assumption that "promoting a
candidate always produces a new diff" doesn't hold. It only reliably produces
a genuine diff in the narrow window where a new candidate exists but hasn't
yet been fully synced to `publish`.

**Why no fix was applied**: retrying within the same test invocation would
not help — `main`/`publish` state is fixed for the duration of a single CI
job, so a retry reproduces the identical outcome deterministically. A real
fix would need to change what the "normal" scenario proves (e.g., force a
synthetic content mutation into the promoted manifest so the diff is never
incidental), which is a nontrivial redesign of a test that specifically
proves the production publish transaction's atomicity — exactly the kind of
change this repo's own history (CR-06, three separate bugfix PRs) warns
against making speculatively. Recommend a dedicated, reviewed follow-up
rather than a guess-fix here.

**Recommended follow-up** (not started): redesign the "normal" scenario to
inject a deliberately-synthetic, always-novel mutation into the promoted
candidate content (distinct from the nonce already written to
`data/derived/observatory/atomic-publish-proof.json`, which was not
sufficient to prevent this specific failure), so the proof's "did it commit"
assertion no longer depends on whether `main`/`publish` happen to already be
in sync for the latest real week.

## Item 3: Visual-regression baseline for the cost-dashboard "valid" state — deferred, not code-changed

Investigated `tests/visual/visual.spec.mjs`, `tests/visual/a11y-perf.spec.mjs`,
and `scripts/design/verify-visual.mjs`. These specs navigate a live-served
build of the actual repository state (`/about/`, `/dashboard/`, etc.) — there
is no fixture-injection mechanism for parameterizing `data/metrics/cost-summary.json`
before the build these tests run against.

Adding a true "valid" state visual baseline today would require one of:

1. Committing a fixture `data/metrics/cost-summary.json` to the repo so the
   real site build renders the valid state — this directly re-introduces the
   "independently maintained total" placeholder problem BR-009 exists to
   remove, and is explicitly the wrong direction.
2. Building new CI plumbing for a throwaway, fixture-fed Hugo build solely
   for this one Playwright spec — a nontrivial addition to
   `scripts/design/verify-visual.mjs`'s build orchestration, not a small
   change.

**Disposition**: correctly deferred, as already recorded in
`.copilot-tracking/reviews/2026-08-10/br-009-squad-acceptance-review.md`
(Calculon's follow-up). The right time to add this baseline is once BR-009
activation lands and `data/metrics/cost-summary.json` is a real, generated
artifact in the tree — at that point the existing `/about/`/`/dashboard/`
visual specs will naturally capture the valid state with no extra plumbing.

## Item 4: Phase 3 (Repository Inventory and Migration Candidate) — blocked on external evidence

Per the plan's own dependency note: "Repository retirement requires URL-level
external evidence that may not be available in the repository and cannot be
inferred from aggregate analytics." The Phase 3 checklist's first four items
require URL Inspection API results, Search Analytics (Google Search Console)
data, sampled inbound-link evidence, and per-URL disposition decisions —
none of which exist in this repository and none of which can be fabricated
or inferred locally.

**Not started.** This phase needs the user (or whoever holds GSC/webmaster
access for the production domain) to supply that external evidence before
any of Phase 3's data-gathering steps can proceed. No code or tracking
changes were made for this item beyond confirming the blocker is still real
and unchanged.
