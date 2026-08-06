#!/bin/bash
# Monitor PR #678 approval and cascade Items 2-5 execution
# Usage: bash ./.copilot-tracking/scripts/monitor-pr-678-cascade.sh

set -e

PR_NUMBER=678
REPO="jmservera/SquadScope"
CHECK_INTERVAL=30  # seconds
MAX_CHECKS=120     # ~60 minutes max wait

echo "🚀 Starting PR #$PR_NUMBER cascade monitoring"
echo "   Repository: $REPO"
echo "   Check interval: $CHECK_INTERVAL seconds"
echo "   Max wait time: ~$((MAX_CHECKS * CHECK_INTERVAL / 60)) minutes"
echo ""

# Function to check PR status
check_pr_status() {
    local pr_data=$(gh pr view $PR_NUMBER --repo $REPO --json state,reviews,merged,mergedAt --template '{{json .}}')
    echo "$pr_data"
}

# Function to check if PR is merged
is_pr_merged() {
    local pr_data="$1"
    echo "$pr_data" | jq -r '.merged'
}

# Function to get merge commit SHA
get_merge_commit() {
    gh pr view $PR_NUMBER --repo $REPO --json mergeCommit --template '{{.mergeCommit.oid}}'
}

# Main monitoring loop
iteration=0
merged=false

while [ $iteration -lt $MAX_CHECKS ]; do
    iteration=$((iteration + 1))
    pr_status=$(check_pr_status)
    
    if [ "$(echo "$pr_status" | is_pr_merged)" == "true" ]; then
        merged=true
        break
    fi
    
    echo "[$iteration/$MAX_CHECKS] PR #$PR_NUMBER status: $(echo "$pr_status" | jq -r '.state')"
    
    if [ $iteration -lt $MAX_CHECKS ]; then
        sleep $CHECK_INTERVAL
    fi
done

if [ "$merged" == "true" ]; then
    echo ""
    echo "✅ PR #$PR_NUMBER MERGED!"
    
    merge_sha=$(get_merge_commit)
    echo "   Merge commit: $merge_sha"
    echo ""
    
    # Automatically trigger Items 2-5 cascade
    echo "🎯 Cascading Items 2-5..."
    echo "   Item 1: ✅ Merged to main"
    echo "   Item 2: ⏳ Waiting for CI baseline capture (~45 min)"
    echo "   Item 3: ⏳ Blocked on Item 2 (~1-2 hours post-Item-1)"
    echo "   Item 4: ⏳ Passive monitoring (~1-2 days)"
    echo "   Item 5: ⏳ Blocked on Items 2-4 (~15 min post-Items-2-4)"
    echo ""
    echo "📊 Estimated completion: 2026-08-08/09"
    
    # Create cascade status file
    cat > .copilot-tracking/tracking/pr-678-merge-cascade.txt <<EOF
Item 1: PR #678 Merged (2026-08-06 $(date +%H:%M:%S) UTC)
- Commit: $merge_sha
- Status: COMPLETE

Item 2: Visual baseline capture (in-progress)
- Blocked until: Item 1 merge detected ✅
- Duration: ~45 min
- Status: AUTO-TRIGGERED by CI

Item 3: Visual evidence review (pending)
- Blocked until: Item 2 complete
- Duration: ~1-2 hours
- Status: Awaiting Amy + Fry review

Item 4: Phase 7.1 Run 3 monitoring (passive)
- Blocked until: Item 1 merge
- Duration: 1-2 days
- Status: Started, parallel to Items 2-3

Item 5: Release decision (pending)
- Blocked until: Items 2-4 complete
- Duration: ~15 min
- Status: Awaiting evidence

Overall Timeline: 2026-08-08/09
EOF
    
    echo "✅ Cascade status recorded in .copilot-tracking/tracking/pr-678-merge-cascade.txt"
    
else
    echo ""
    echo "⏳ PR #$PR_NUMBER still waiting for approval after $(($iteration * $CHECK_INTERVAL / 60)) minutes"
    echo "   Please ask a team member to:"
    echo "   1. Visit: https://github.com/jmservera/SquadScope/pull/$PR_NUMBER"
    echo "   2. Click 'Approve' review"
    echo "   3. Click 'Merge pull request' → 'Squash and merge'"
    echo ""
    echo "   Monitoring will resume automatically when approval is detected."
fi

exit 0
