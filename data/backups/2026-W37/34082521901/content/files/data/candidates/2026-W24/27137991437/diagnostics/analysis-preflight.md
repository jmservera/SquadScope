# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `77880` tokens / `311518` bytes
- Prompt checksum: `9b4b570ed7f0a8e1a8741f6d246089839c0a9e3c0669568744a724efac5ff7a2`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 12248 | 3062 | e66bdab27d4288a713e1f0d88846c9df8aec834c7fee448564a331b667f6ee76 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 90273 | 22569 | a75f118e69f6999e5e9b37bcdf259d41e55c5c88bbfd4314131460f94e017141 | data/raw/2026-W24.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 139116 | 34779 | b113be3e9ad3311395469b6459d20790ce271026c6449ba3076cb791ac49b71b | data/raw/2026-W24.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 248374 | 62094 | 0967c2429f93117b4fa5ffed317d8891686be780b293d540e083cf84aa6fc7ab | data/raw/2026-W24.json | Sanitized current weekly payload for 2026-W24. | included |
| prior_continuity | true | 16398 | 4100 | eadff75a4e3041a6a4094072321e45621d882eaeafcad4fb00a0b0714eebeb60 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W23-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| analysis_wisdom | true | 761 | 191 | 74d75f0911f06c43a867a9b9578489ddd998dc2b707784055702e3e7c2463fdb | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | false | 44 | 11 | 7da9d889bcbfdd287dc298e0e6f2cd50a87741e062793c8fefb591167b73df39 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | not included: no analysis-specific skills |
| press_correlations | true | 32786 | 8197 | eb8f9c8f85bdbc533857ff55591610cd0e6ef6fd0c28ef66c993a414b22ddec5 | data/analyzed/2026-W24-press-context.md | Deterministic mapper slice: press/developer correlation context. | included |
| rendered_prompt | true | 311518 | 77880 | 9b4b570ed7f0a8e1a8741f6d246089839c0a9e3c0669568744a724efac5ff7a2 |  | Exact prompt that will be passed to Copilot CLI. | included |
