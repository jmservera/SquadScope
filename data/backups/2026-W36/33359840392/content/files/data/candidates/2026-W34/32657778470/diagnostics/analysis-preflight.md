# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `25891` tokens / `103564` bytes
- Prompt checksum: `4aad72d50584da4c8c45dd337a84c6a10829b85c83722cea9d49dc07e35f9b1f`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 21326 | 5332 | c85874d3ee26b9f29d5ad37f8b5f4cb0213a9e14e51d966a032c560c290a668e | data/raw/2026-W34.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21184 | 5296 | 5a560af4ff63d01f5308e61ec0c621cc953a1d013679cb098c228775a545a8fe | data/raw/2026-W34.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 48177 | 12045 | bd8f3d07b2ae235ffe660edbc149692ec93f1ab199e7797ebf19448fcf3356f3 | data/raw/2026-W34.json | Sanitized current weekly payload for 2026-W34. | included with compacted repo slices |
| prior_continuity | true | 8129 | 2033 | db69bbc8d469f2dc7bf63b69442caa873a11dae04ea6fb304f6235ef9dfaa21a | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W33-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 6793 | 1699 | 7bc1e6376824864cf17cd663869c6755df461b493cbb301525afb45dd34f46f6 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14254 | 3564 | fb6c55c4d60a4cdb2352db5f0027755d026f47201cb6479bd51cbba767991be5 | data/analyzed/2026-W34-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 103564 | 25891 | 4aad72d50584da4c8c45dd337a84c6a10829b85c83722cea9d49dc07e35f9b1f |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
