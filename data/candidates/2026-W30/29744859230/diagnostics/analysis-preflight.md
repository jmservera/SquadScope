# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `83664` tokens / `334656` bytes
- Prompt checksum: `7fe9a8e187cf835a135f400ee065f915454979e76b04f83e1703ba24715eb9eb`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 110848 | 27712 | 56052de4c1f13c6a9c330685def6edff3f5d1235b52988ceb4fa3166f90ff613 | data/raw/2026-W30.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 143017 | 35755 | 44700093ca2a2a4d8c3266f85f49fa32410b752ea2837e720c794162fb4f9626 | data/raw/2026-W30.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 274467 | 68617 | 4973504b7f255550c6c83a78fffbe05b5949b2eb6eef457497efba61707ced4b | data/raw/2026-W30.json | Sanitized current weekly payload for 2026-W30. | included |
| prior_continuity | true | 12669 | 3168 | dcac7a09d4a96a32ca7cd63f1fa60f66f7db26496dc2b427ac75bf8d29232025 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W29-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 7043 | 1761 | 45da0aa072a255ff866e582bef5a8a9cf0f00d76d31acc34bb5c6293f85b272b | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14277 | 3570 | 7843d081cbd58ad9e90a9678b26bb3193015473dd3c1336a43ba24b4f719e5f8 | data/analyzed/2026-W30-press-context.md | Deterministic mapper slice: press/developer correlation context. | included: condensed alongside synthesis narrative |
| rendered_prompt | true | 334656 | 83664 | 7fe9a8e187cf835a135f400ee065f915454979e76b04f83e1703ba24715eb9eb |  | Exact prompt that will be passed to Copilot CLI. | included |
