# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `24996` tokens / `99984` bytes
- Prompt checksum: `93d7a6e14730e7e21c75aeb1aa9f93d9549ec47d8b4bb487bd6684a4b7a55e6b`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 18793 | 4699 | 32fee097dbfa2843a0f145e7921e5c27a8ca86f3d9706f49d26fea7e70840a3b | data/raw/2026-W39.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21266 | 5317 | f9a13ab9fe0cb1619385ea417cfd5d2f9bdc2e552e824979d0dda6c1f8fb95f7 | data/raw/2026-W39.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 45552 | 11388 | b7a7e3d6add6ed8f8665a1fbb94520f87a1b2fc79b2a7c992169e6bb67bfc1ac | data/raw/2026-W39.json | Sanitized current weekly payload for 2026-W39. | included with compacted repo slices |
| prior_continuity | true | 8111 | 2028 | fb5b789eafaf14b1ff9befac3aed430d0afaa91b50ff766e55df0d571637baec | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W38-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 5831 | 1458 | 4fff678ae713fac899c7e0783d7a5a562a965f9b6b03c5c5b16c74d5e0f9cff4 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14264 | 3566 | 32cde1652b44065934b69d5f483fb42654bb3315e66b7e25eee995819e4fb82f | data/analyzed/2026-W39-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 99984 | 24996 | 93d7a6e14730e7e21c75aeb1aa9f93d9549ec47d8b4bb487bd6684a4b7a55e6b |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
