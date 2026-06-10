#!/usr/bin/env bash
# Minimal safe Ralph tick placeholder for SquadScope
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
STATE_DIR=".ralph"
mkdir -p "$STATE_DIR"
LOG="$STATE_DIR/tick_run.log"
NOW_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "[$NOW_ISO] Safe tick start" >> "$LOG"
REPO="jmservera/SquadScope"
# Fetch issues and PRs safely; if API returns empty, write empty JSON array
if ! gh issue list --repo "$REPO" --state open --limit 200 --json number,title,labels,assignees,updatedAt,url > "$STATE_DIR/issues.json" 2>"$STATE_DIR/gh_issues_err.log"; then
  echo "[]" > "$STATE_DIR/issues.json"
fi
if ! gh pr list --repo "$REPO" --state open --limit 200 --json number,title,files,labels,assignees,updatedAt,url,mergeable,mergeStateStatus,reviewDecision,author > "$STATE_DIR/prs.json" 2>"$STATE_DIR/gh_prs_err.log"; then
  echo "[]" > "$STATE_DIR/prs.json"
fi
# Write a brief summary to tick log
ISSUES_COUNT=$(jq 'length' "$STATE_DIR/issues.json" 2>/dev/null || echo 0)
PRS_COUNT=$(jq 'length' "$STATE_DIR/prs.json" 2>/dev/null || echo 0)
echo "[$NOW_ISO] Fetched issues: ${ISSUES_COUNT}, PRs: ${PRS_COUNT}" >> "$LOG"
# No further actions here; the squad loop or coordinator will process these files.
echo "[$NOW_ISO] Safe tick end" >> "$LOG"
exit 0
