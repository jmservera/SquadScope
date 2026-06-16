# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `85179` tokens / `340713` bytes
- Prompt checksum: `df84cfe3aaac4016d2453855ced60698461d20e7323ae1aeb5e04d132c36ae2b`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 13561 | 3391 | db6c7bd62d4c52e233aae6b3dd460b58414a9a313fe6fabf1315b6422bd2201f | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 101692 | 25423 | 9324241b6130273380faf053702a2d39ed186058f6f2878428ee59a72cd05822 | data/raw/2026-W25.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 139919 | 34980 | 80cdbf5550ad35bd91639500fbe6e19e30c589f4d6d3e488b70cd679ce695943 | data/raw/2026-W25.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 262015 | 65504 | 80a4cfef7b6b434151c0b82c6174145a2487c71e3a61e976bd67dea9f26d943a | data/raw/2026-W25.json | Sanitized current weekly payload for 2026-W25. | included |
| prior_continuity | true | 17121 | 4281 | 31b7620b46aca36329ff252464ff13e57747b4bf106dbcdf66251284374ea50c | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W24-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 6573 | 1644 | 2203f0529abb0f4b080683230ae5eca720b37c84927bbdbcf1a653085c86ee8f | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 32814 | 8204 | ed1251934286cd7753439572d92b7f348453fb033f74da8a3465f3469f0a3bfb | data/analyzed/2026-W25-press-context.md | Deterministic mapper slice: press/developer correlation context. | included |
| rendered_prompt | true | 340713 | 85179 | df84cfe3aaac4016d2453855ced60698461d20e7323ae1aeb5e04d132c36ae2b |  | Exact prompt that will be passed to Copilot CLI. | included |
