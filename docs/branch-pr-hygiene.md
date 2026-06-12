# Branch and Generated-Data PR Hygiene

Guidelines for keeping branches, PRs, and generated-data syncs clean and reviewable.

## Principles

1. **Separation of concerns** — product/code PRs, generated-data sync PRs, and platform/infra PRs must remain separate. Never bundle unrelated changes.
2. **Clean worktrees** — PRD moves, generated-data syncs, and platform upgrades must start from a clean worktree (`git status` shows nothing untracked or modified).
3. **Focused commits** — each commit should address one logical change. Squash fixups before requesting review.

## Generated-Data Sync PRs

Generated-data PRs (e.g., weekly crawl artifacts in `data/`) follow these rules:

- **Isolation:** generated-data sync PRs contain only data files and their corresponding metadata (manifests, checksums). No source code, template, or documentation changes.
- **Branch naming:** use `data/sync-{date}` or `data/{descriptive-slug}` (e.g., `data/sync-2026-w24`).
- **Review scope:** reviewers verify the data pipeline ran correctly and output is well-formed — they do not need to re-review the pipeline code itself.
- **Example:** PR #326 demonstrates the pattern — generated-data sync isolated from product changes.

## Product / Code PRs

- **Branch naming:** use `feat/`, `fix/`, `docs/`, `squad/` prefixes as appropriate.
- **Scope:** one feature, bug fix, or docs change per PR. If a change touches multiple concerns, split it.
- **Dependencies:** if a code PR depends on a data sync landing first, note this in the PR description.

## Stacked PRs

Stacked PRs (where PR B targets PR A's branch) are acceptable when:

- Changes are sequential and tightly coupled (e.g., schema migration followed by code using new schema).
- Each PR is independently reviewable and testable at its layer.

When using stacked PRs:

- Note the base branch and merge order in each PR description.
- After the base PR merges, retarget dependent PRs to `main`.
- Never merge a dependent PR before its base PR.

## Dirty Worktree Policy

**Never commit from a dirty worktree** for:

- PRD/doc moves to `docs/processed/`
- Generated-data sync PRs
- Platform upgrades or dependency bumps
- Squad configuration changes

If unrelated modified/untracked files exist, stash or resolve them before creating the PR branch.

## Reviewer Checklist

Before approving any hygiene-sensitive PR, verify:

- [ ] PR contains only changes described in its title/description — no unrelated files.
- [ ] No secrets, tokens, connection strings, SAS URLs, or private endpoint values are present.
- [ ] Generated-data PRs do not include source code changes.
- [ ] Stacked PRs document their base branch and merge order.
- [ ] The author started from a clean worktree (no stray untracked files committed).
- [ ] CI is green and tests were not weakened to achieve green status.

## Workflow Permissions

- Generated-data sync workflows use least-privilege `contents: write` only.
- PRs opened by automation (bot/Actions) still require human review before merge.
- No workflow should commit secrets or expand permissions beyond what the specific job needs.
