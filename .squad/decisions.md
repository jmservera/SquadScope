

### 2026-09-22: Keep the live accessibility gate active after reskill

**By:** Ralph

**What:** Archive stale decisions while retaining the current release gate in the active ledger.

**References:** #594, #714, PR #773

**Why:** PR #773 merged on 2026-09-22 and is no longer active work. The relaunch epic #594 remains open solely for #714. That issue requires a new immutable release candidate followed by genuine live screen-reader evidence; automation and browser tooling cannot substitute for the named-reviewer evidence.

### 2026-09-22: Retain active prompt-safety and Podcaster environment conditions

**By:** Ralph

**What:** Keep the still-operative SEC-05 and SEC-09 conditions in the active ledger after archiving their original disposition records.

**References:** SEC-05, SEC-09, PR #659

**Why:** Generated content must continue through review before merge, the prompt-injection corpus must grow when real incidents are observed, and any future auto-publish path requires a new Hermes review. The `podcaster-real-generation` environment must retain its wait timer, pre-dispatch intent check, post-run evidence review, and main-only boundary; restore self-review protection if a second qualified reviewer joins and revisit the exception during the next security cycle.
