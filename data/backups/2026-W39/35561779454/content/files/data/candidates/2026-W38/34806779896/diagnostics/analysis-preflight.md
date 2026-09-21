# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `25108` tokens / `100429` bytes
- Prompt checksum: `31bc7ff71e497643bc62707ee1ef98fe9c283645f4791d2542a08c4bc310aded`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 19401 | 4851 | 35b2fd06de7cbd5e1e439570606057753aaf217c4e269286b0df2f2cba16e104 | data/raw/2026-W38.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21875 | 5469 | 649d360cdd1fefd43d50b893ac90366fab6703c0941689be34fbb538bddaebca | data/raw/2026-W38.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 46829 | 11708 | fe716d1234395ceb195c13f5eb4659f910d1e86baaca2ecedc75b97c2cc4bc25 | data/raw/2026-W38.json | Sanitized current weekly payload for 2026-W38. | included with compacted repo slices |
| prior_continuity | true | 8107 | 2027 | 3aa636fb0d1e3f9b29048c3b4d12f1a2e9dab1ac869f3d9342e314e0ae08decf | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W37-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 5005 | 1252 | 9856a2b8a7aafc9e2936f5fc460762f0007ce0bc8877fe8ea780ac2050c3c163 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14262 | 3566 | dc5313426a603f60ad2f869c73162e388a2322f7bdda3c2064b7fd98f989be79 | data/analyzed/2026-W38-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 100429 | 25108 | 31bc7ff71e497643bc62707ee1ef98fe9c283645f4791d2542a08c4bc310aded |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
