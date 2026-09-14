# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `83201` tokens / `332801` bytes
- Prompt checksum: `b4fd7be4294e97c9b1da3558aa3a7ae2c5cc8cbfbde85655c82c67c405d690b5`
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
| raw_metadata | true | 261477 | 65370 | 39dc5e65f5f96f716ea475617131d9aec1f8a1575deafcf7e31e87b204d03f5f | data/raw/2026-W25.json | Sanitized current weekly payload for 2026-W25. | included |
| prior_continuity | true | 17121 | 4281 | 31b7620b46aca36329ff252464ff13e57747b4bf106dbcdf66251284374ea50c | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W24-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 6883 | 1721 | 8fbe671b72c03a3843053ba5373aebae04a93ef0965c64bf2c613e4fbcbd9c62 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 761 | 191 | 74d75f0911f06c43a867a9b9578489ddd998dc2b707784055702e3e7c2463fdb | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | false | 44 | 11 | 7da9d889bcbfdd287dc298e0e6f2cd50a87741e062793c8fefb591167b73df39 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | not included: no analysis-specific skills |
| analysis_continuity | false | 54 | 14 | 4aa8aa0a5f547787857b904de1a8db84227a0dd095a215f4259dda3c27b17776 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | not included: no analysis-specific continuity capsule |
| press_correlations | true | 32814 | 8204 | ed1251934286cd7753439572d92b7f348453fb033f74da8a3465f3469f0a3bfb | data/analyzed/2026-W25-press-context.md | Deterministic mapper slice: press/developer correlation context. | included |
| rendered_prompt | true | 332801 | 83201 | b4fd7be4294e97c9b1da3558aa3a7ae2c5cc8cbfbde85655c82c67c405d690b5 |  | Exact prompt that will be passed to Copilot CLI. | included |
