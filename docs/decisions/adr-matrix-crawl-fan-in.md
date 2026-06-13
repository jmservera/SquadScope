# ADR: Matrix Crawl Fan-In Architecture

**Status:** Accepted  
**Date:** 2026-06-13  
**Decision makers:** Leela (Lead/Architect)  
**Related issues:** #331, #333, #356, #435, #436, #437, #438, #439

---

## Context

SquadScope collects weekly GitHub repository signals and external news via RSS, then runs AI-powered analysis to produce trend summaries. As the system grows (more sources, more repos, longer analysis), the question arose: should we parallelize crawling with GitHub Actions matrix jobs?

Investigation (documented in the [PRD](../processed/PRD-matrix-crawl-map-reduce-analysis.md)) revealed:

1. RSS collection is already fast (~1s for 5 feeds) — matrix overhead would exceed actual work time.
2. GitHub API crawling is rate-limit-constrained, not compute-constrained — parallelism risks quota exhaustion without proportional speedup.
3. Analysis duration (28+ minutes) and context growth (112k+ tokens) are the actual bottlenecks.
4. Downstream consumers expect canonical artifact formats regardless of collection topology.

---

## Decision

We adopt a **staged, evidence-gated architecture** with three key design choices:

### 1. Keep monolithic crawl as default; matrix is opt-in

**Choice:** The default crawl topology remains monolithic (single GitHub crawl process + in-process RSS fetching). Matrix fan-out is enabled only when measurable triggers fire.

**Alternatives considered:**
- **Always-on matrix:** Rejected. Adds runner setup cost, artifact I/O overhead, cache merge complexity, and rate-limit instability for no measured benefit at current scale.
- **Hybrid from day one:** Deferred. Premature complexity without evidence of need.

**Triggers for RSS matrix:**
- RSS p95 > 60 seconds
- Source count > 10
- Source requires independent credentials or isolation

**Triggers for GitHub matrix:**
- Shard experiment proves ≥25% speedup
- No more than 10% API-call growth
- Zero secondary-rate-limit regression

### 2. Deterministic fan-in with strict contracts

**Choice:** All matrix legs produce per-shard artifacts with schema validation, shared run context, and checksums. A fan-in job deterministically merges them into canonical payloads that are byte-stable for the same inputs.

**Alternatives considered:**
- **Append-only merge (no ordering):** Rejected. Non-deterministic output breaks caching, diffing, and downstream idempotency.
- **Last-writer-wins:** Rejected. Data loss risk when shards overlap.
- **Event-stream merge:** Over-engineered for batch workflows. Deferred.

**Key contract properties:**
- Deterministic ordering (repos by `full_name`, articles by `(source_id, url)`)
- Idempotent: same inputs → same outputs
- Fail-closed on required artifacts; graceful degradation on optional sources
- Schema-versioned with forward-compatible rejection

### 3. Map/reduce as analysis experiment, not crawl optimization

**Choice:** Map/reduce is positioned as an analysis-quality tool (reducing LLM context, improving citations) — not as a crawl-speed mechanism. It runs in dry-run mode only until evidence validates quality parity.

**Alternatives considered:**
- **Map/reduce for crawl parallelism:** Rejected. Crawl is I/O-bound (API rate limits), not compute-bound. Parallelism doesn't help.
- **Immediate production map/reduce:** Rejected. Must prove quality parity with single-pass analysis before promoting output.
- **Vector DB / embedding approach:** Non-goal for MVP. No external paid infrastructure.

---

## Consequences

### Positive

- **No premature complexity:** Pipeline stays simple until evidence justifies change.
- **Safe experimentation:** Dry-run and candidate-only modes allow testing without risk.
- **Downstream stability:** Canonical artifact contracts isolate consumers from topology changes.
- **Measurable rollout:** Clear acceptance criteria prevent subjective "good enough" decisions.
- **Deterministic validation:** Byte-stable output enables automated regression testing.

### Negative

- **Delayed parallelism:** If source count grows rapidly, we'll need to implement matrix mode reactively rather than having it pre-built.
- **Experiment overhead:** Shard experiments require dedicated runs comparing baseline vs. variant.
- **Contract maintenance:** Schema versioning adds development overhead for artifact format changes.

### Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Triggers never fire, matrix code rots | Review triggers quarterly; remove dead code if unused for 6 months |
| Fan-in non-determinism edge cases | Automated QA gates (#438) with fixture-based determinism tests |
| Map/reduce quality never matches single-pass | Keep single-pass as default; map/reduce stays experimental until proven |
| Schema version proliferation | Strict one-version-active policy; old schemas rejected immediately |

---

## Implementation Roadmap

| Phase | Issue | Status | Description |
|-------|-------|--------|-------------|
| 0 | #333 | In progress | Define fan-in validation path and run-context schema |
| 1 | #435 | Planned | GitHub shard experiment with guardrails |
| 1 | #436 | Planned | RSS per-source artifacts + deterministic merge |
| 1 | #437 | Planned | Observability metrics wiring |
| 2 | #438 | Planned | Automated QA gates |
| 2 | #439 | This PR | Documentation package (contracts, runbook, ADR) |
| 3 | — | Future | Evidence-based rollout decision (enable or archive) |

---

## References

- PRD: [Matrix Crawl and Map/Reduce Analysis](../processed/PRD-matrix-crawl-map-reduce-analysis.md)
- Fan-in contracts: [docs/matrix-crawl-fan-in-contracts.md](../matrix-crawl-fan-in-contracts.md)
- Runbook: [docs/matrix-crawl-runbook.md](../matrix-crawl-runbook.md)
- Issue #356: Triage meta-issue for matrix crawl & map/reduce
- Issue #331: Define map/reduce analysis promotion path
- Issue #333: Define crawl matrix readiness and fan-in validation path
