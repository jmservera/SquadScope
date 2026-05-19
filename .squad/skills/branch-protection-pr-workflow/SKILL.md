# Branch Protection via PR Workflow

confidence: high
discovered_by: Leela (CI architecture decision)
date: 2026-05-19

## Pattern

Never bypass branch protection rules. Instead, use one of two strategies:

### Strategy A: PR-based (requires "Allow GitHub Actions to create PRs" repo setting)
1. Create a timestamped feature branch from the default branch
2. Make all changes to the feature branch
3. Open a PR via `gh pr create` pointing feature branch → default branch
4. Auto-merge the PR with `gh pr merge --squash --auto --delete-branch`

### Strategy B: Unprotected publish branch (recommended for automated pipelines)
1. Push automated data directly to an unprotected `publish` branch
2. The branch ruleset only protects `refs/heads/main` — other branches accept direct pushes
3. Use artifacts for inter-job data flow within the same workflow run
4. Periodically sync `publish` → `main` via manual PR if needed

## When to Use

- **Strategy A:** When human review of automated changes is desired before merge
- **Strategy B:** When the pipeline must be self-sufficient without repo admin settings or review gates (current SquadScope approach)

## Implementation

### Strategy B (current — `publish` branch pattern)

```bash
DATA_BRANCH="publish"
# Fetch or create the unprotected branch
if git fetch origin "$DATA_BRANCH" 2>/dev/null; then
  git checkout -f -B "$DATA_BRANCH" "origin/$DATA_BRANCH"
else
  git checkout -f -B "$DATA_BRANCH" "origin/$DEFAULT_BRANCH"
fi
# Apply changes and push directly
git add data/
git diff --cached --quiet && exit 0
git commit -m "data: weekly crawl $WEEK [run #${GITHUB_RUN_ID}]"
git push origin "$DATA_BRANCH"
```

### GitHub Actions Workflow Setup

```yaml
permissions:
  contents: write

env:
  DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
```

## Notes

- Use `git checkout -f` (force) when switching branches after artifact downloads modify the working tree
- Branch name must not conflict with existing `ref/` namespace (e.g., can't use `data` if `data/*` branches exist)
- Deploy jobs may have environment protection rules limiting which branches can deploy
- The `publish` branch accumulates automated commits; main stays clean with only reviewed changes
