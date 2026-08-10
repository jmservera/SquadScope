# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `25699` tokens / `102796` bytes
- Prompt checksum: `32c8cc70a98c3007714b0ee94dc0e47610910bc1286e16e653c7729b25356a95`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 19391 | 4848 | 4582117dd63823f4ea745736a2f6697bfbcd38dc8da69f8e09ac458cccd07766 | data/raw/2026-W33.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21254 | 5314 | 83a9f6792039602f6e5cb24dd7f8112d4e68f67bc5bbb38eb5025d74e87b009d | data/raw/2026-W33.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 46111 | 11528 | 60c7adbf019f8ad52305a8cbd8d379ae1c2ca7148b13d75d925a2976a40a4ea1 | data/raw/2026-W33.json | Sanitized current weekly payload for 2026-W33. | included with compacted repo slices |
| prior_continuity | true | 8125 | 2032 | c1d4aaefb45a18f9bd44f8dd5411e18a6b1869801e491af72da07a93720dd7b6 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W32-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 8094 | 2024 | c1b86c4978b22b661af342d6641b28b0e64ef7064f71a85edcbd9cbd5a2da7e3 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14255 | 3564 | f4043ad0bdcf9d0e11f6374f0e5edeac54d93c58229f6e81b973357d50597742 | data/analyzed/2026-W33-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 102796 | 25699 | 32c8cc70a98c3007714b0ee94dc0e47610910bc1286e16e653c7729b25356a95 |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
