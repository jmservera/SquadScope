---
name: "product-boundary-zero-impact"
description: "Keep sister-product work out of SquadScope's website and publishing pipeline unless the integration is explicitly external and non-blocking."
domain: "architecture, product-boundaries"
confidence: "high"
source: "issue #310 correction and issue #312 reskill after Podcaster repository split"
---

## Context

Use this when a proposed feature is related to SquadScope but belongs to a sister product, tool, or separate repository. The Podcaster split is the canonical case: Podcaster now lives in `jmservera/SquadScope-Podcaster`, while SquadScope may only link to it externally.

## Patterns

- Treat the sister product as the owner of its backlog, infrastructure, secrets, runtime, and release process.
- Keep SquadScope publishing zero-impact: no new required jobs, approvals, costs, cloud resources, or failure modes in the weekly website pipeline.
- Limit SquadScope changes to external links, interface contracts, docs, or harmless prototypes unless a future decision explicitly changes the product boundary.
- Route implementation work for Podcaster-owned concerns to Podcaster: Azure resources, TTS, staging, manual Spotify publishing packets, and future automation.
- Keep remaining SquadScope podcast issues narrow: post-publish handoff (#302) and external podcast link (#307).

## Examples

- Good: Add or update a SquadScope website link that points to the external Podcaster experience.
- Good: Document a handoff contract that lets SquadScope know an episode exists without blocking weekly publishing.
- Good: File TTS, Azure, staging, Spotify, or automation work in `jmservera/SquadScope-Podcaster`.

## Anti-Patterns

- Adding Podcaster infrastructure, secrets, TTS generation, or publishing approval gates to the SquadScope website pipeline.
- Letting a Podcaster failure block or degrade SquadScope's weekly publish.
- Keeping duplicated podcast implementation backlog in SquadScope after ownership moved to the sister repository.
