# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `71449` tokens / `285796` bytes
- Prompt checksum: `5ea7a9d0c50a07027c70abd9eadf5a1a23c6078b38befcc2cdcae562e5c5e96b`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17684 | 4421 | fb35f34470d1258a67e749c09cbc08f7d57668e7f297dc4d0a793ef2c31de280 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 62104 | 15526 | eea0d771d646a16dcea2459a77a4eb2a63864c2f5e37ea71dc53d03af58aef1c | data/raw/2026-W31.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 145732 | 36433 | 188f86d05529b87f1898dc219552eab5c846a44ece19452740e48a50f32a6ce3 | data/raw/2026-W31.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 225807 | 56452 | 1655682822384e39b9defa31d67f35ac2f6917786d61a2bfc309a9417e88ac37 | data/raw/2026-W31.json | Sanitized current weekly payload for 2026-W31. | included |
| prior_continuity | true | 13760 | 3440 | 4d2ee446b94233dd4aff32b0910e90696bf6be5ca910dcdbd6107b3adf26fce4 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W30-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 5751 | 1438 | bc69c10c2cd38ad2d5ad5cc7d3c6074f7dd9da35114fba51a7349234e63092c7 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14278 | 3570 | 25b0e94489b9a2ec2b4241edaff17b20d395c7ef2e16acaaa91b63ac0ea4a55d | data/analyzed/2026-W31-press-context.md | Deterministic mapper slice: press/developer correlation context. | included: condensed alongside synthesis narrative |
| rendered_prompt | true | 285796 | 71449 | 5ea7a9d0c50a07027c70abd9eadf5a1a23c6078b38befcc2cdcae562e5c5e96b |  | Exact prompt that will be passed to Copilot CLI. | included |
