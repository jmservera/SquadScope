# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `25400` tokens / `101599` bytes
- Prompt checksum: `d36111d38ebc4a9ea4fb526bb754f90d46aaabd331132a15289efd637d927345`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 19827 | 4957 | 8849e2a378916df6f3bda52c826552ff7cc9ff465fea7aae7dc49377fe4d878b | data/raw/2026-W37.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 21203 | 5301 | ee43e7804d82ed070f632bfa388902e2ba7818ca47530396c8e1a1fead2eb82f | data/raw/2026-W37.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 46449 | 11613 | 931d466ce5ed0287b6bc83cdb090f81930832fad5f344cab2a74d80cc300a9f3 | data/raw/2026-W37.json | Sanitized current weekly payload for 2026-W37. | included with compacted repo slices |
| prior_continuity | true | 8106 | 2027 | e6f6996c4b1be687a5f040b2adfe189b2218bcacf7516ef27294f10d8e21162a | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W36-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 6574 | 1644 | a3ef933aaa5ad1eb28624e3479eaa7c74a62af125708b2a687db8a31216531ab | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14244 | 3561 | 69c2577c8f5bf5a4cc3197e7a498e5fd1b2d678ed3d3714777309ad8303e1ef3 | data/analyzed/2026-W37-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 101599 | 25400 | d36111d38ebc4a9ea4fb526bb754f90d46aaabd331132a15289efd637d927345 |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
