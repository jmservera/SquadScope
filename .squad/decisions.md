

### 2026-09-24: Defer sharded production crawl (shard-435 experiment)

**By:** Leela (recorded by Ralph)

**What:** Do not adopt the sharded crawl for production. Archive `docs/experiments/shard-435-plan.md` to `docs/processed/` with its results.

**References:** #800, #435, PR #456, PR #803, PR #804

**Why:** Three real runs with the plan's `--shards 3` settings showed only a 4–6% speedup against the ≥25% guardrail, because only one validation worker remains after the two search shards. Two supplementary `--shards 5` runs passed the speed (about 64%), API (0% growth), and rate-limit guardrails. Byte-stability, however, cannot be proven with back-to-back live arms: repo sets were identical, and only live star, fork, and timestamp drift differed. The monolithic crawl already takes about 5.5 minutes, so the saving is too small to justify production risk. Revisit only if crawl time becomes a bottleneck, and only after adding a record/replay fan-in determinism check.

### 2026-09-22: Keep the live accessibility gate active after reskill

**By:** Ralph

**What:** Archive stale decisions while retaining the current release gate in the active ledger.

**References:** #594, #714, PR #773

**Why:** PR #773 merged on 2026-09-22 and is no longer active work. The relaunch epic #594 remains open solely for #714. That issue requires a new immutable release candidate followed by genuine live screen-reader evidence; automation and browser tooling cannot substitute for the named-reviewer evidence.

### 2026-09-22: Retain active prompt-safety and Podcaster environment conditions

**By:** Ralph

**What:** Keep the still-operative SEC-05 and SEC-09 conditions in the active ledger after archiving their original disposition records.

**References:** SEC-05, SEC-09, PR #658

**Why:** Generated content must continue through review before merge, the prompt-injection corpus must grow when real incidents are observed, and any future auto-publish path requires a new Hermes review. The `podcaster-real-generation` environment must retain its wait timer, pre-dispatch intent check, post-run evidence review, and main-only boundary; restore self-review protection if a second qualified reviewer joins and revisit the exception during the next security cycle.
