# PR Review Thread Resolution via GraphQL

confidence: medium
discovered_by: Leela (PR workflow standardization)
date: 2026-05-19

## Pattern

Resolve pull request review threads programmatically using GitHub's GraphQL API. This enables:
1. Automated responses to review comments
2. Marking conversations as resolved without manual UI interaction
3. Audit-trail-preserving replies (comment visible in history)
4. Integration with workflow automation for issue resolution and documentation updates

## When to Use

- Confirming issue fixes in PR review threads
- Updating review comments with implementation details
- Resolving conversations after changes are made
- Automating feedback acknowledgment in CI/CD workflows
- Multi-agent handoff scenarios where one agent acknowledges another's review

## Implementation

### GraphQL Mutation Pattern

```graphql
mutation {
  addPullRequestReviewThreadReply(input: {
    threadId: "PRRT_kwDOSgq4hM6C3UXy"
    body: "✅ Fixed: [Description of change]"
  }) {
    comment {
      id
    }
  }
}
```

### How to Get Thread ID

1. Query the PR to list review threads:
```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequest(number: 123) {
      reviewThreads(first: 10) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes {
              body
            }
          }
        }
      }
    }
  }
}
```

2. Extract the `id` field (e.g., `PRRT_kwDOSgq4hM6C3UXy`)
3. Use it in the `addPullRequestReviewThreadReply` mutation

### CLI Integration

```bash
# Store thread IDs from PR
THREAD_IDS=$(gh api graphql -f query='
  query {
    repository(owner: "$OWNER", name: "$REPO") {
      pullRequest(number: $PR_NUMBER) {
        reviewThreads(first: 10) {
          nodes {
            id
          }
        }
      }
    }
  }
' -F OWNER=owner -F REPO=repo -F PR_NUMBER=123 --jq '.data.repository.pullRequest.reviewThreads.nodes[].id')

# Reply to each thread
for THREAD_ID in $THREAD_IDS; do
  gh api graphql -f query='
    mutation {
      addPullRequestReviewThreadReply(input: {
        threadId: "$THREAD_ID"
        body: "Fixed in commit abc123"
      }) {
        comment { id }
      }
    }
  ' -F THREAD_ID="$THREAD_ID"
done
```

## Examples

From `reply_thread1.graphql`:

```graphql
mutation {
  addPullRequestReviewThreadReply(input: {
    threadId: "PRRT_kwDOSgq4hM6C3UXy"
    body: "✅ Fixed: Removed the submodule initialization instruction from the rollout checklist. The project does not use git submodules."
  }) {
    comment {
      id
    }
  }
}
```

## Notes

- Thread IDs are opaque identifiers; they cannot be easily reverse-engineered from PR/comment numbers
- Use `gh api graphql` for CLI-based GraphQL queries
- Replies are visible in the PR review thread history (not hidden)
- Marking as resolved requires a separate GraphQL call (not shown in this example)
- Authentication requires `repo` or `pull_request` scope
