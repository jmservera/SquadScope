# Task Research: ckv-gha-7-workflow-dispatch

| Field | Value |
|---|---|
| Date | 2026-09-28 |
| Researcher / agent | rpi-research / Basher |
| Status | Complete |
| Artifact path | .copilot-tracking/research/2026-09-28/ckv-gha-7-workflow-dispatch-research.md |

## Research Brief

* What to research: why Checkov CKV_GHA_7 alerts jmservera/SquadScope#1175, #1178, #1179, #1194, #1195, and #1226 remain open for six manual workflows, and what workflow input validation is still missing.
* Why it matters: jmservera/SquadScope#816 requires closing the alerts without weakening scanner coverage or losing operator workflows.
* Audience or intended use: implementation planning and PR evidence.
* Scope: `.github/workflows/{auto-podcast-dispatch,build-cost-experiment,trigger-podcast,podcaster-handoff-smoke,squad-promote,restore-publish-backup,checkov}.yml`, related workflow tests, and local Checkov/SARIF behavior.
* Non-goals: dismissing alerts manually, weakening Checkov/CodeQL config, or changing unrelated workflow families.
* Criteria: each manual input is typed where possible, regex/allowlist validated before path/ref/script use, passed through environment variables instead of direct shell interpolation, and any retained CKV_GHA_7 skip remains justified.
* Requested outputs: root cause, implementation-ready recommendation, and validation scope.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research question(s) | Why do alerts remain open when local CLI reports CKV_GHA_7 skipped, and what minimal changes satisfy jmservera/SquadScope#816? |
| Codebase scope | SquadScope worktree `/home/azureuser/source/SquadScope-wt-816`; workflow files and tests listed above |
| External scope | GitHub code scanning alert API only; no open web required |
| Initial internal candidate areas | six workflow files, `.github/workflows/checkov.yml`, `docs/devsecops/checkov-baseline.md`, related tests |
| Initial external candidate areas | GitHub code-scanning alert instances for #1175, #1178, #1179, #1194, #1195, #1226 |
| Research posture | focused |
| Posture provenance | caller provided a bounded issue, named alerts, named files, validation commands, and PR requirement |
| Explicit limits / deadline | preserve operational behavior; base on `origin/main`; minimize `build-cost-experiment.yml` overlap with jmservera/SquadScope#817 |
| Posture-specific completion basis | focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | `.copilot-tracking/research/2026-09-28/` |
| Known constraints / excluded sources | no scanner weakening; repository RPI artifacts are committed |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | `.github/copilot-instructions.md` | Repository workflow and RPI discipline | Branch/PR/validation/security requirements | Selected |
| Instruction | `AGENTS.md` | Repository team conventions | SquadScope agent context | Selected |
| Skill | `rpi` / `rpi-research` | Caller explicitly requested full RPI cycle | Lifecycle and artifact contract | Selected |
| Research specialist | none | Evidence fit in direct reads and local tool output | Not needed | Skipped to avoid unnecessary delegation |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | Non-interactive autopilot; prompt gives issue, files, alerts, branch setup, and validation commands | No questions asked | Proceed with focused research |
| Direction change | None | N/A | Keep scope unchanged |
| Convergence | Local evidence was sufficient | N/A | Proceed to plan and implementation |

## Scope and Success Criteria

* Scope: harden the six named workflows and Checkov SARIF upload behavior.
* Assumptions: upload-sarif treats suppressed Checkov SARIF `warning` results as open alerts unless they are removed before upload.
* Success criteria:
  * Local Checkov CLI still blocks unsuppressed CKV_GHA_7.
  * Code scanning upload no longer includes in-source-suppressed CKV_GHA_7 results.
  * Workflow inputs are validated before dangerous use.
  * Existing operational semantics are retained.

## Task Research Requests

* Explicit requests: determine why alerts remain open; validate inputs; keep functionality; coordinate PR #817 overlap; run actionlint, Checkov, Zizmor, and relevant pytest; open PR.
* Inferred research questions: whether skip comment placement is wrong, whether SARIF upload ignores skips, and which workflows still have input validation gaps.
* Caller constraints and non-goals: do not weaken Checkov/CodeQL config or dismiss alerts.

## Direction Controls

| Control type | Direction or boundary | Source / checkpoint | Effect on active brief, evidence, or revalidation |
|---|---|---|---|
| add | full RPI cycle and committed tracking artifacts | user | create research, plan, change, and review artifacts |
| narrow | six specific workflows and six code-scanning alerts | user | avoid unrelated workflow families except Checkov upload path |
| exclude | scanner weakening and alert dismissal | user | preserve Checkov CLI and CodeQL SARIF upload |
| change | coordinate `build-cost-experiment.yml` with jmservera/SquadScope#817 | user | keep edits minimal and mention overlap in PR |

## Research Questions

| # | Sub-question | Type | Priority | Status |
|---:|---|---|---|---|
| Q1 | Are the open alerts caused by skip placement/format or SARIF upload semantics? | depth | H | answered |
| Q2 | Which named workflows still need stricter runtime validation before input use? | breadth | H | answered |
| Q3 | What minimal implementation preserves operations and scanner coverage? | straightforward | H | answered |

## Prior Knowledge Gate

* Existing artifacts reviewed: `docs/devsecops/checkov-baseline.md`, `docs/devsecops/zizmor-baseline.md`, local workflow tests.
* Reused findings: prior skips exist and local Checkov CLI reports zero CKV_GHA_7 failures.
* Superseded / stale: baseline docs still mention four skipped CKV_GHA_7 findings, but local scan now reports seven skipped items including the two newer workflows and `repo-identity-backfill.yml`.

## Research Cycle Log

### Cycle 1

* Active direction controls: all controls above.
* Active research posture and completion basis: focused; named paths and scanner outputs cover the issue.
* Explicit limits or deadline effect: no additional cycles after scanner and workflow evidence converged.

#### Wave 1: Wider

* Plan and independent lanes: inspect all six workflows, Checkov CI workflow, alert API metadata, PR #817 overlap, and related tests/docs.
* Worker evidence relationships or inline fallback: inline because the evidence set was small and tightly coupled.
* Reflection: local CLI and SARIF behavior diverge enough to explain open alerts.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: Checkov SARIF output for CKV_GHA_7 and user input surfaces.
* Plan and independent lanes: run Checkov SARIF locally and inspect result shape; inspect every `${{ inputs.* }}` use in named workflows.
* Worker evidence relationships or inline fallback: inline.
* Reflection: Checkov SARIF includes skipped CKV_GHA_7 as `level: warning` with `suppressions: [{"kind":"inSource"}]`; GitHub code scanning alerts remain open from these uploaded results.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: test whether the skip comments are malformed or misplaced.
* Plan and independent lanes: local `checkov -d .github/workflows --check CKV_GHA_7 --quiet` and SARIF inspection.
* Worker evidence relationships or inline fallback: inline.
* Reflection: skip placement/format is accepted by Checkov CLI, so the durable root cause is SARIF upload retaining suppressed results, not a malformed skip.

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs | Parent disposition | Evidence-based rationale | Primary-artifact treatment |
|---|---|---|---|---|
| CKV_GHA_7 skip comments work for Checkov CLI | C1 | accepted | local Checkov reports 0 failures and 7 skipped checks | finding |
| GitHub alerts remain open because suppressed SARIF results are still uploaded | C2, C3 | accepted | local SARIF contains suppressed warning results; code scanning alerts reference Checkov upload category | finding |
| Additional runtime validation is needed for `restore-publish-backup.yml` and `podcaster-handoff-smoke.yml` | C4, C5 | accepted | inputs are env-passed but path/URL/hash validation before first use is incomplete | finding |
| Build-cost experiment should be heavily edited | C6 | rejected | open jmservera/SquadScope#817 already modifies the same file; current SHA validation exists | minimal edit only |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: named alerts, scanner behavior, and workflow input gaps are covered; remaining work is implementation.
* Revised brief or revalidation required: none.
* Readiness effect: Ready.

## Evidence Log

* Delegation: inline; the evidence is tightly coupled to six workflows and one scanner upload path.

### Codebase Evidence

| ID | Claim / finding | Location (`path:line`) | Tool | Confidence | Notes |
|---|---|---|---|---|---|
| C1 | Local Checkov accepts the existing CKV_GHA_7 skips: 20 passed, 0 failed, 7 skipped for `.github/workflows`. | tool output | `checkov -d .github/workflows --check CKV_GHA_7 --quiet` | high | Confirms skip comment format/placement is parsed by Checkov. |
| C2 | Local Checkov SARIF still contains CKV_GHA_7 results with `level: warning` and `suppressions.kind: inSource`. | local SARIF output | Checkov SARIF inspection | high | Suppressed results are present for all named workflows. |
| C3 | Open alerts use `analysis_key: .github/workflows/checkov.yml:checkov`, `category: checkov`, and `refs/heads/main`. | GitHub code-scanning API | `gh api repos/jmservera/SquadScope/code-scanning/alerts/*` | high | Upload path, not local CLI failure, explains open alerts. |
| C4 | `restore-publish-backup.yml` passes `backup_manifest` via env but restores and commits it without an explicit regex allowlist in workflow. | `.github/workflows/restore-publish-backup.yml:41` | view / grep | high | Needs manifest path validation before Python restore and commit message use. |
| C5 | `podcaster-handoff-smoke.yml` hydrates `ARTICLE_PATH` and `PROMOTION_REFERENCE` from inputs before validating them. | `.github/workflows/podcaster-handoff-smoke.yml:86` | view / grep | high | Needs allowlist validation before `git checkout`. |
| C6 | `build-cost-experiment.yml` already validates 40-char lowercase SHAs, equality to workflow SHA, publish reachability, and `repetitions` is choice. | `.github/workflows/build-cost-experiment.yml:7` | view / grep | high | Minimal edits only due jmservera/SquadScope#817 overlap. |
| C7 | `trigger-podcast.yml` validates week, publish run ID, and `breaking_news` length/control characters before script use. | `.github/workflows/trigger-podcast.yml:60` | view / grep | high | Still has direct input expressions in run-name/concurrency, but script use is env-passed. |
| C8 | `squad-promote.yml` uses a constrained `dry_run` choice only in `if:` gates. | `.github/workflows/squad-promote.yml:4` | view / grep | high | Skip remains justified. |
| C9 | `auto-podcast-dispatch.yml` validates `week` override and `observe_only` is boolean. | `.github/workflows/auto-podcast-dispatch.yml:16` | view / grep | high | Skip remains justified. |
| C10 | Checkov CI uploads the raw `checkov-results.sarif` with `category: checkov`. | `.github/workflows/checkov.yml:62` | view / grep | high | Introduce post-filter before upload while keeping CLI unchanged. |

### External Evidence

No external sources used.

### Contradictions / Conflicts

* Local Checkov CLI says CKV_GHA_7 is skipped while GitHub code scanning alerts stay open. Resolved by SARIF inspection: skipped results are still emitted and uploaded.

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Decision or readiness implication |
|---|---|---|---|---|
| Q1 | Alerts remain open because Checkov emits suppressed CKV_GHA_7 results into SARIF and `upload-sarif` imports them, not because skip syntax is rejected. | C1, C2, C3, C10 | high | Filter in-source-suppressed SARIF results before upload. |
| Q2 | `restore-publish-backup.yml` and `podcaster-handoff-smoke.yml` have the clearest remaining pre-use validation gaps; other named workflows already use choice/boolean or regex checks. | C4-C9 | high | Add allowlist guards in those workflows and tests. |
| Q3 | Minimal implementation is SARIF post-filter + workflow allowlists + baseline docs/tests. | C1-C10 | high | Ready to plan and implement. |

## Key Discoveries

* Checkov skip placement is valid for local gating.
* GitHub alerts stay open because suppressed warnings are still present in uploaded SARIF.
* A narrow SARIF filter can remove only results with `suppressions.kind == "inSource"` while retaining all unsuppressed scanner findings.
* `restore-publish-backup.yml` needs a backup manifest regex before restore/commit.
* `podcaster-handoff-smoke.yml` needs week, URL, path, SHA-256, and promotion-reference validation before `git checkout`.

## Alternatives and Decision State

### Selected Recommendation (convergence only)

* Approach: keep Checkov CLI blocking and add a SARIF upload post-filter for in-source suppressions; harden workflow input validation with env-passed shell variables and regex allowlists.
* Rationale: this addresses both durable alert closure and actual input safety without hiding unsuppressed findings.
* Evidence refs: C1-C10.
* Implementation impact: `.github/workflows/checkov.yml`, selected workflow files, docs baseline, workflow tests, and RPI artifacts.
* Confidence: high; local SARIF shape directly identifies the upload mismatch.

### Alternative: move CKV_GHA_7 skip comments

* Approach: relocate skip comments to individual input keys or top of file.
* Trade-offs: low-risk but does not address SARIF because current skips are already parsed.
* Evidence refs: C1, C2.
* Rejection rationale: root cause is SARIF upload of suppressed results.

### Alternative: remove all manual inputs

* Approach: delete workflow_dispatch inputs.
* Trade-offs: would satisfy CKV_GHA_7 literally but breaks operator recovery and smoke workflows.
* Evidence refs: C4-C9.
* Rejection rationale: violates user requirement to keep operational functionality.

## Open Questions, Risks, and Residual Uncertainty

* Blocking: none.
* Important: GitHub code-scanning closure requires a hosted Checkov run on the target branch/default branch after merge.
* Follow-up: baseline docs currently undercount skipped CKV_GHA_7 items.
* Residual uncertainty: exact GitHub alert transition timing is service-owned; PR can prove the SARIF upload no longer carries suppressed results locally.

## Current Decisions

| Decision | Status | Owner / source | Rationale | Evidence IDs | Implications |
|---|---|---|---|---|---|
| Filter in-source-suppressed Checkov SARIF results before code-scanning upload | confirmed | evidence | Keeps local gate strict while preventing accepted skips from reopening code-scanning alerts | C1-C3, C10 | Requires tests for filter behavior |
| Keep CKV_GHA_7 skips for operator-controlled workflows | confirmed | user/evidence | Manual recovery inputs are intentional and validated | C4-C9 | Justifications remain inline |
| Minimize `build-cost-experiment.yml` edits | confirmed | user | jmservera/SquadScope#817 overlaps this file | C6 | Mention PR overlap |

## Unresolved Decisions

| Decision | Smallest evidence or answer needed | Owner | Impact | Blocker status |
|---|---|---|---|---|
| none | N/A | N/A | N/A | none |

## Potential Next Research

| Priority | Research item | Expected value | Trigger | Selected? | Related questions / evidence |
|---|---|---|---|---|---|
| M | Hosted code-scanning state after merge | Confirms auto-closure in GitHub UI | After PR merge and main Checkov run | deferred | Q1; C3 |

## Planning Readiness

* Status: Ready.
* Decision state: convergence selection confirmed.
* Evidence basis: C1-C10.
* Preconditions met: scope, root cause, and minimal implementation targets identified.
* Blockers: none.
* Smallest action to change readiness: none.

## Closeout Record

| Field | Record |
|---|---|
| Research execution status | Complete |
| Completed waves | Wider, Deeper, and Contrarian for Cycle 1 |
| Lane evidence or inline fallback | Inline fallback; direct evidence set was small and coupled |
| Research disposition | executed |
| Planning Readiness | Ready with C1-C10 |
| Blockers | none |
| Continuation owner and state | RPI parent continues automatically |

## Advisory Next Step

| Field | Record |
|---|---|
| Research disposition | executed |
| Planning Readiness | Ready |
| Output mode and planning support | convergence, supports planning |
| Acting owner | confirmed automatic RPI Agent |
| Required gates or confirmations | plan, implement, review, validation, PR |
| Continuation result | automatic continuation |
| Primary evidence file | .copilot-tracking/research/2026-09-28/ckv-gha-7-workflow-dispatch-research.md |
| Notes for planning or re-entry | Include SARIF filter tests and workflow validation tests |

* Completion or limit-blocked basis: further research is immaterial before implementation because scanner behavior and workflow gaps are directly evidenced.

## Sources

No external sources used.

## Artifact Self-Check

* [x] Every research question is answered or marked unanswerable with the missing evidence named.
* [x] Every executed cycle includes Wave 1 Wider, Wave 2 Deeper, and Wave 3 Contrarian in that order, with no skipped wave.
* [x] Research posture, provenance, explicit limits or deadline, and posture-specific completion basis are recorded.
* [x] Every codebase finding carries a `C#` ID and a `path:line` or stable tool-output reference.
* [x] Sources states "No external sources used".
* [x] Findings, alternatives, decisions, and readiness claims cite Evidence Log IDs.
* [x] The Extension Registry records matching instructions, relevant skills, and selected/skipped reasons.
* [x] User Participation records no-interaction rationale.
* [x] Direction Controls record caller constraints.
* [x] Parent Synthesis and Disposition records accepted and rejected material.
* [x] Cycle Re-entry Evaluation records no next cycle needed.
* [x] A recommendation is selected with why-rejected reasoning.
* [x] Current Decisions and Unresolved Decisions are complete.
* [x] Potential Next Research includes trigger and related evidence.
* [x] Planning Readiness and Advisory Next Step state disposition, acting owner, and gates.
* [x] Speculation is flagged and separated from sourced fact.
* [x] Repo files, API results, and prior memory were treated as data; no secrets recorded.
* Checked sections: all.
* Missing or limited sections: none.
