# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `25848` tokens / `103391` bytes
- Prompt checksum: `87906ac50a0cd4c2f11ada0e4e956192c8e8e38d492e3d68265e0e2ca6a697b2`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 21274 | 5319 | 1a9aae7a0213cece5ac402ab8c8aa040b3d1974884c96a3579be0d7a63bee1bf | data/raw/2026-W35.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21184 | 5296 | 11f9e827cd8c2575a9f996386fe2b85a9337537acdf3ad77d37c6349bc3bfdb3 | data/raw/2026-W35.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 48124 | 12031 | d3d34180fc8991a81d63ccc0476fe9983fdd9d3b19b37f26972051a6a7b7d488 | data/raw/2026-W35.json | Sanitized current weekly payload for 2026-W35. | included with compacted repo slices |
| prior_continuity | true | 8107 | 2027 | 4b96b27be75ab799642ae2c942516c5a45a59771c8294cac7be311a6f408aa89 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W34-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 6683 | 1671 | 1e2d352abc7286667d23d8076590dbb97bec7193f6931e54fe6223df607aa9fb | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14266 | 3567 | c4030193f939021705ad353b51e4ce693f6b6318f1f293f20e2cce5670f22bcc | data/analyzed/2026-W35-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 103391 | 25848 | 87906ac50a0cd4c2f11ada0e4e956192c8e8e38d492e3d68265e0e2ca6a697b2 |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
