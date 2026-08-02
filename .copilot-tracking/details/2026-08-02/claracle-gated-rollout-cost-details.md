<!-- markdownlint-disable-file -->
# Implementation Details: Claracle Gated Rollouts and Cost Measurement

## Cost Experiment Contract

Every variant starts from a clean destination and the same hydrated source state. The machine-readable record must include main SHA, publish SHA, workload variant, source counts by page class, Hugo and Pagefind versions and raw durations, rendered and indexed counts, output bytes, runner identity, exit state, and Actions URL.

Use cumulative variants so marginal cost can be calculated without changing generator logic:

1. Observatory generated classes excluded
2. Five checked-in topic hubs included
3. Three generated data pages included
4. 263 checked-in repository pages included
5. Optional approved dynamic canary included

Do not derive a blocking budget from one run. Retain at least three comparable runs and calculate median plus nearest-rank p95 separately for Hugo and Pagefind.

## Dynamic Preview Contract

A preview must evaluate the same eligible-candidate and assignment path as write mode while performing no filesystem mutation. Its structured output must identify candidate slug, title, evidence weeks, supporting sources, proposed hub path, proposed weekly assignments, registry effect, and skip reason. Tests must compare preview output with the corresponding isolated write transaction.

The first canary uses explicit deferrals in `ignore_topics`; no threshold change is permitted. Threshold-based canaries are unsafe because repository generation can classify existing pages as obsolete.

## Repository Activation Contract

The isolated enabled preflight must preserve the existing recurrence threshold and hydrated publish state. A reviewer must disposition every obsolete or expired path. No removal is accepted from mere crawl absence. The second generation must be byte-stable.

Rollback has two parts:

1. Disable the production flag to stop future mutation.
2. Revert the generated-state transaction to undo pages, ledgers, registries, assignments, and logs already committed.

## Approval Contract

Hermes approves security and lifecycle policy. URL approves workflows, secret scope, and retained artifacts. jmservera separately approves the dynamic-topic canary and repository-page activation. Each approval identifies the exact revision, evidence, conditions, rollback owner, and date.
