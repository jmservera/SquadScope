# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `25477` tokens / `101908` bytes
- Prompt checksum: `28cf7bd6c93b5a4ad70bfae3c3ba4f3fe92ad9348e9ebf79b437b0f18ae28106`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 20183 | 5046 | 57ac5272ae09ad4a2a3034af08acf7fe5511d6843722ec9ab5e7c5b48ed58df6 | data/raw/2026-W32.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21282 | 5321 | 1d76bf2076c68e214894df1d8adc29fb0bbe2463d5c29a563b8932dc1c57521a | data/raw/2026-W32.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 46943 | 11736 | b1f734c9f73875a75442bab059d1b2469bd9a285cd840aa856de81039024e877 | data/raw/2026-W32.json | Sanitized current weekly payload for 2026-W32. | included with compacted repo slices |
| prior_continuity | true | 8107 | 2027 | d89aa827b6350b3a9f09d7267a53b968b9cd1256088c25d63962975009bdc5ab | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W31-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 6411 | 1603 | e211bfa6ddd9d3a59680f1d1682060c221a6c3b420e5b6192699f7a43bf97e52 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14236 | 3559 | d8e20806f0a8550871384e7b99feb7a06893ec7f96a4e7d26730df5f2e154f26 | data/analyzed/2026-W32-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 101908 | 25477 | 28cf7bd6c93b5a4ad70bfae3c3ba4f3fe92ad9348e9ebf79b437b0f18ae28106 |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
