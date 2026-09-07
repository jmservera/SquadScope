# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `82048` tokens / `328190` bytes
- Prompt checksum: `5c2a54c7442cf867d0c25ca80edb3ca31957e311110fd8a67d170af9d78de08a`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 13286 | 3322 | 3fc6f8ff142c49483bed0267a052023bda519e1028eb39ee958a8dd2dbe4a54d | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 98629 | 24658 | 1dcdf1cbdbf97c554e40f2422cdd7ff79208d7d11fdf48c1ec3002ce87d7bac5 | data/raw/2026-W25.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 139665 | 34917 | 6f7b15cd2a26a97c555a69d5f2c1e18bb4bad8db9fdcd19a7da3f8a0758b9999 | data/raw/2026-W25.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 257954 | 64489 | 72d2d6a42a855b0303edd43c3e3312e612c80b415b6c147c294b963e597fa23a | data/raw/2026-W25.json | Sanitized current weekly payload for 2026-W25. | included |
| prior_continuity | true | 17121 | 4281 | 31b7620b46aca36329ff252464ff13e57747b4bf106dbcdf66251284374ea50c | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W24-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 5993 | 1499 | cc04e17694ea12cbb73f9c676d5701e235ded758cf1f6d49fa5d30436f854977 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 761 | 191 | 74d75f0911f06c43a867a9b9578489ddd998dc2b707784055702e3e7c2463fdb | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | false | 44 | 11 | 7da9d889bcbfdd287dc298e0e6f2cd50a87741e062793c8fefb591167b73df39 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | not included: no analysis-specific skills |
| press_correlations | true | 32931 | 8233 | 878334bf61a222d5fc109f0ed95fdb98703ff0a4fe3ef0a6abddab3dea931148 | data/analyzed/2026-W25-press-context.md | Deterministic mapper slice: press/developer correlation context. | included |
| rendered_prompt | true | 328190 | 82048 | 5c2a54c7442cf867d0c25ca80edb3ca31957e311110fd8a67d170af9d78de08a |  | Exact prompt that will be passed to Copilot CLI. | included |
