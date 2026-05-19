# Branch Protection via PR Workflow

confidence: high
discovered_by: Leela (CI architecture decision)
date: 2026-05-19

## Pattern

Never bypass branch protection rules. Instead, integrate branch protection into the workflow:
1. Create a timestamped feature branch from the default branch
2. Make all changes to the feature branch
3. Open a PR via `gh pr create` pointing feature branch → default branch
4. Auto-merge the PR with `gh pr merge --squash --auto --delete-branch`
5. Remove any "RepositoryRole" bypass actors from branch rulesets
6. Respect all required checks, approvals, and status gateways

## When to Use

- CI/CD workflows that commit data or content to protected branches
- Automated testing and review gates that must run before merge
- Multi-stage pipelines (crawl → analyze → generate → deploy)
- Enforcing audit trails via merge commits in PR history

## Implementation

### Workflow Step Pattern

```bash
# 1. Create timestamped branch
WEEK=$(date +%Y-W%V)
BRANCH="data/weekly-crawl-${WEEK}-${GITHUB_RUN_ID}"
git checkout -b "$BRANCH"

# 2. Stage and commit changes
git add data/raw/ data/snapshots/ .squad/run-counter.txt
if ! git diff --cached --quiet; then
  git commit -m "data: weekly crawl $WEEK"
  git push origin "$BRANCH"
  
  # 3. Create PR
  gh pr create --base "$DEFAULT_BRANCH" --head "$BRANCH" \
    --title "data: weekly crawl $WEEK" \
    --body "Automated weekly crawl data commit from run #${GITHUB_RUN_ID}."
  
  # 4. Auto-merge when all checks pass
  gh pr merge "$BRANCH" --squash --auto --delete-branch
fi
```

### GitHub Actions Workflow Setup

```yaml
permissions:
  contents: write
  pull-requests: write

env:
  DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
```

### Ruleset Configuration

**Never use:**
```yaml
# ❌ DO NOT USE
- uses: repo-bypass
- role: RepositoryRole:5  # Admin bypass
```

**Instead:**
- Configure branch protection rules that include:
  - Required status checks
  - Dismissable reviews
  - Require CODEOWNERS approval (if applicable)
  - Require branches to be up to date
  - Allow auto-merge with `--auto` flag

## Examples

From `.github/workflows/crawl-and-publish.yml`:

```yaml
Commit crawl data via PR:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        ref: ${{ github.event.repository.default_branch }}
    
    - name: Commit crawl data via PR
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
      run: |
        git config user.name 'GitHub Actions'
        git config user.email 'actions@github.com'
        
        COUNTER=$(cat .squad/run-counter.txt 2>/dev/null || echo 0)
        COUNTER=$((COUNTER + 1))
        printf '%s\n' "$COUNTER" > .squad/run-counter.txt
        WEEK=$(date +%Y-W%V)
        BRANCH="data/weekly-crawl-${WEEK}-${GITHUB_RUN_ID}"
        
        git checkout -b "$BRANCH"
        git add data/raw/ data/snapshots/ .squad/run-counter.txt
        git diff --cached --quiet && exit 0
        
        git commit -m "data: weekly crawl $WEEK"
        git push origin "$BRANCH"
        
        gh pr create --base "$DEFAULT_BRANCH" --head "$BRANCH" \
          --title "data: weekly crawl $WEEK" \
          --body "Automated weekly crawl data commit from run #${GITHUB_RUN_ID}."
        
        gh pr merge "$BRANCH" --squash --auto --delete-branch
```

## Notes

- The `--squash --auto` pattern ensures clean commit history while respecting branch protection
- `--delete-branch` cleans up the feature branch after merge
- Use timestamped branch names to prevent collisions in multi-stage pipelines
- All required checks must pass before `--auto` merge succeeds (fails gracefully if not met)
