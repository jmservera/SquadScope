# URL — History

## Core Context
- Owns the DevSecOps guardrails toolchain and its phased rollout
  (Phase A baseline → Phase B fixes → Phase C enforcement).
- Complements Hermes: URL owns pipeline/tooling/hooks; Hermes owns security
  review, threat modeling, and alert triage.

## Learnings
- Phase A rollout pattern: introduce a tool warning-only (`continue-on-error`,
  `--soft-fail`), capture a baseline in `docs/devsecops/`, then tighten later.
- Pin every action by commit SHA and pin tool versions so local and CI match.
- Keep CI correct, not just green — never weaken, skip, or soft-fail a real gate
  to make a check pass.

## Establishment (Epic: jmservera/SquadScope-Coordinator#33) — 2026-06-26
- Phase A baselines landed for ruff (#540), checkov (#541), and zizmor (#542).
- copilot-instructions guardrail rules and this charter added (#546).

## Cross-agent note — 2026-08-04
- Hermes reviewed and accepted-with-conditions the `prevent_self_review` amendment on the
  `podcaster-real-generation` environment (SEC-09, PR #658, merged).
- URL reviewed the environment's secret scope and workflow/pipeline hardening (the other half
  of `owner-action-register.md` action 4) and found existing controls sufficient (SEC-10,
  PR #659). Added a length/character bound on the `breaking_news` `workflow_dispatch` input as
  a low-severity hygiene fix. Action 4 is now fully done.
