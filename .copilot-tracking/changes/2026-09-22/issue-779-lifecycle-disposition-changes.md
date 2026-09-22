# Issue 779 lifecycle disposition changes

Date: 2026-09-22
Owner: Leela
Issue: https://github.com/jmservera/SquadScope/issues/779

## Changes

- Restored `weekly-agents-gpt-5-6-sol.md` from `docs/processed/` to
  `docs/prds/`, preserving rename history.
- Replaced the premature archived/completed state with
  **implemented; validation incomplete/blocked**.
- Recorded W38/W39 passing gate outcomes and qualified editorial acceptance,
  including unsupported directional predictions, missing reader-visible
  references, and the limits of the 100 quality score.
- Distinguished:
  - the retained W37-to-W38/W39 ledger comparison (about 31.6% higher);
  - W37's incorrect `copilot-default` attribution despite GPT-5.5 declarations;
  - the reconstructed GPT-5.5-priced comparison (Sol about 26.5% lower);
  - missing per-agent, runtime-model, cache, measured-cost, synthesis, and
    isolated provider-latency evidence.
- Clarified that the 2026-09-08 owner approval authorized implementation, not
  lifecycle closure with incomplete post-upgrade evidence.
- Created the focused owner decision/rollback issue recorded below.

## GitHub decision issue

URL: https://github.com/jmservera/SquadScope/issues/780

Decision requested:

1. retain GPT-5.6-Sol provisionally while collecting instrumented, comparable
   evidence for both weekly calls; or
2. execute the consistent four-file rollback (two effective agent declarations
   plus workflow and test attribution surfaces).

## Evidence artifact disposition

Retain the Fry and Farnsworth issue-779 research reports for the focused docs
PR. The repository already tracks dated evidence under
`.copilot-tracking/research/`; these reports are the direct basis for the PRD
disposition and should not be discarded. They were not modified by Leela.

## Validation

- `git diff --check`
- path/status inspection confirming the PRD rename and authorized-file-only
  changes
- GitHub duplicate search before decision issue creation

## Reviewer remediation

Fry's rejection review triggered a bounded source-evidence correction. Scribe
is the revision owner. The PRD now marks the blinded editorial review complete,
uses the repository-retained Fry and Farnsworth reports plus linked GitHub
records as the canonical current source trail, and identifies the original
machine-local session artifacts as non-repository historical context.
