# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `25294` tokens / `101173` bytes
- Prompt checksum: `2f892f26c9bdf6a2b884f5fad6b52f239b030c2d5fae429109965c8d1aad7d03`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 20698 | 5175 | c7dbe2973981ca4fb678f0a59e81d90ac1868d2b18f701cc5c2b6b82c13b335d | data/raw/2026-W36.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21012 | 5253 | 9949db387179d20ecf993c146c1733b8bd148d4b8e4f38f88711ab0dd0ad4442 | data/raw/2026-W36.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 47294 | 11824 | 3bc2cd00436679549677107640e54227127293a502b8d72736039c41bcfbbfa8 | data/raw/2026-W36.json | Sanitized current weekly payload for 2026-W36. | included with compacted repo slices |
| prior_continuity | true | 8107 | 2027 | 084928a3553be0b2824923b61d5b4e4aeb28806a027f545a97033e440867e4f7 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W35-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 5311 | 1328 | a723b47ce5bca199fa865a4b8a5dc3fcc6b346bd4f3fe0b681356bf5a990d642 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14250 | 3563 | 4407f6d02faf65cdcc0592202b71ac420288c2680f7d6191f21c3767237d3765 | data/analyzed/2026-W36-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 101173 | 25294 | 2f892f26c9bdf6a2b884f5fad6b52f239b030c2d5fae429109965c8d1aad7d03 |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
