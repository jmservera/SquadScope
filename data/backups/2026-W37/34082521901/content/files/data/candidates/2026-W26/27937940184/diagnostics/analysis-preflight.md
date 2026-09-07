# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `22006` tokens / `88022` bytes
- Prompt checksum: `34fbc6fd64ef8eed982f00795ccf804fd8b9d5db82b7821c03741dabfa1f6fbc`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 13798 | 3450 | ca3f363f99078fb3b3952b54514c71d0f09312f075101d27be84d62ed0469ae2 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 15931 | 3983 | d542996ef2e63cfd5f24ce32b9c3a792f85531b6730bc01fa4b708ad4951406e | data/raw/2026-W26.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 15528 | 3882 | 6082e8718c271062b204f21cbc4380e69082ed11ccc7f19cc90f986a6a748c5f | data/raw/2026-W26.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 37006 | 9252 | 542d5af343120c17049217a10d4db3eb78df9abb28b9a5b1b6320db997c6e9be | data/raw/2026-W26.json | Sanitized current weekly payload for 2026-W26. | included with compacted repo slices |
| prior_continuity | true | 8111 | 2028 | 85a1d5199d6a55c367b9c58372f404a82fbe9255b8ac8aa3e9a5d8421f39b456 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W25-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 6207 | 1552 | 7b5dc2cca09ca90d5f4f5f6ed268c563ec64ccb825c2c176895f52c265a6a22a | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14270 | 3568 | 0b573fea722e80abd38ef3a3647deea1bc29d980ca8477f39a82e90204de84c1 | data/analyzed/2026-W26-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 88022 | 22006 | 34fbc6fd64ef8eed982f00795ccf804fd8b9d5db82b7821c03741dabfa1f6fbc |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
