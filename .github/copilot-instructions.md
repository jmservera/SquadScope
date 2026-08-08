# Copilot Instructions for SquadScope

## Project Context

* SquadScope, publicly branded as Claracle, analyzes GitHub trends and publishes
  a Hugo site.
* Use the Squad agent as the default for AI-assisted work. When using Copilot
  CLI, pass `--agent squad`.
* Read `architecture.md` for system boundaries and `.squad/team.md` plus
  `.squad/routing.md` for current ownership.
* Pipeline code lives in `scripts/`, tests in `tests/`, Hugo content in
  `content/`, and templates and assets in `layouts/` and `assets/`.

## Branch and Pull Request Workflow

All changes must use a branch and a pull request. Never commit directly to
`main` or bypass branch protection.

1. Start from current `main` in a clean, dedicated worktree and create a focused
   branch. Use the repository prefixes such as `feat/`, `fix/`, `docs/`,
   `data/`, or `squad/`.
2. Keep each PR to one concern. Separate product or code changes,
   generated-data updates, and infrastructure changes.
3. Run the checks relevant to the changed files before pushing. Do not weaken,
   skip, or make a real gate non-blocking to obtain a green result.
4. Push the branch, open a PR, and ensure the automatic Copilot review starts.
   If automation does not start it, add GitHub Copilot as a reviewer through the
   PR's Reviewers control when Copilot review is enabled for the repository.
5. Wait until Copilot has finished reviewing the latest commit. A completed
   review may have no comments when the change is acceptable. Do not treat a
   pending review or the absence of comments before completion as approval.
6. Inspect every failed check and every comment from Copilot or another
   reviewer. Fix valid findings, push the fixes, and reply with rationale when a
   suggested change is not appropriate.
7. Resolve each review thread only after its fix or documented disposition is
   visible on the PR. Unresolved threads block merge.
8. After every substantive push, wait for checks and Copilot review to finish
   again against the new head commit. Reinspect comments because the new review
   may produce additional findings.
9. If GitHub reports that the branch is behind or the PR is stale, update the
   branch from current `main`, resolve conflicts, push, and repeat the complete
   checks and review cycle.
10. Merge only when the latest head commit is current with `main`, all required
    checks pass, Copilot has finished reviewing that commit, and no review
    threads remain unresolved. Automated PRs still require human review.

The most common merge blockers are failed checks, unresolved review comments,
and a branch that needs an update from `main`. Diagnose and correct the cause;
do not bypass the protection.

For stacked PRs, document the base and merge order. Merge the base first,
retarget the dependent PR to `main`, update it, and repeat checks and review.

## Validation

Run the smallest relevant checks while developing, then run all affected gates
before pushing:

* Python: `ruff check .`, `ruff format --check .`, and `pytest tests/`
* Hugo or content: `hugo --minify`, followed by inspection of rendered output
  for user-facing changes
* Workflow, IaC, or container configuration: the blocking Checkov scan defined
  in `docs/devsecops/checkov-baseline.md`
* GitHub Actions workflows: the pinned Zizmor command defined in
  `docs/devsecops/zizmor-baseline.md`
* Dockerfile or Containerfile changes: a local `docker build`
* Podcast handoff changes: the tests and smoke workflow associated with
  `.github/workflows/podcaster-handoff-smoke.yml`

Local hooks in `.pre-commit-config.yaml` cover Ruff, Checkov, pytest, and Docker
build checks. Run Zizmor separately for workflow changes. Keep tool versions
synchronized with CI and the baseline documents. A local emergency hook bypass
does not justify skipping or weakening CI.

## Generated Content and Data

* Treat checked-in crawl artifacts as source data. Regenerate derived content
  with its owning script instead of editing generated output by hand.
* Review lifecycle state, generated content, taxonomy registries, manifests,
  and checksums as one transaction when the pipeline updates them together.
* Keep generated-data PRs limited to generated files and their corresponding
  metadata. Do not mix them with source, template, or documentation changes.
* Do not commit local Hugo output or transient evidence under `public/`,
  `resources/_gen/`, reports, or ignored screenshot result directories.
* Follow `docs/data-observatory-runbook.md` for observatory operations and
  `docs/branch-pr-hygiene.md` for branch and generated-data rules.

## Security and Review Ownership

* Never commit secrets. Use GitHub environment secrets and least-privilege,
  job-level workflow permissions.
* Route architecture and final code review to Leela, testing to Fry, CI and
  guardrail changes to URL, and security review to Hermes.
* Workflow, infrastructure, Dockerfile, and Containerfile changes require both
  URL pipeline review and Hermes security review.
* Changes to prompts, imported external text, generated AI content, or
  user-facing AI output require Nibbler review for prompt injection and AI
  safety concerns.

## Cross-Repository Contracts

Changes to `config/podcast.json` or `scripts/podcaster_handoff.py` affect
SquadScope-Podcaster. Coordinate those changes with that repository and verify
the handoff contract before merge. SquadScope owns the stable post-publication
handoff; podcast generation remains outside this repository's critical
publishing path.

## Authentication Troubleshooting

Multiple GitHub CLI accounts may be configured on this machine. If a push,
`gh` write, or environment operation fails with an unexpected permission error,
run `gh auth status`. Switch to the repository owner account with
`gh auth switch --user jmservera --hostname github.com` when needed.
