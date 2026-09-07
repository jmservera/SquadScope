# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `21160` tokens / `84637` bytes
- Prompt checksum: `a719d206ed4deef1d1e44cf9a29d73f5c8ee9182a02028ea87a5e864617a842d`
- Degraded/compacted: `true`
- Degradation reason: Prompt was deterministically compacted to fit the configured token budget.
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 13798 | 3450 | ca3f363f99078fb3b3952b54514c71d0f09312f075101d27be84d62ed0469ae2 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 13479 | 3370 | a3361cd6dc70a3e19af7008a1ff172370f0e1e698949e6957bb2cc77dfdc659e | data/raw/2026-W27.json | Deterministic mapper slice: newly discovered repositories. | compacted to top 25 repos by stars |
| trending_repos | true | 15012 | 3753 | 6707858045b53412dd887e79f0fa5f5556709da3b62d71ad32ab67600531d1bb | data/raw/2026-W27.json | Deterministic mapper slice: continuing/trending repositories. | compacted to top 25 repos by stars_gained/stars |
| raw_metadata | true | 33171 | 8293 | e9b91f727c84eec3787e80766dad97e69dee553362058ef0984c71648e7f911a | data/raw/2026-W27.json | Sanitized current weekly payload for 2026-W27. | included with compacted repo slices |
| prior_continuity | true | 8107 | 2027 | 6ecee1a44b3d9551e73d4ac58cab591a6793400c1f1b445853f5105f06c77959 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W26-summary.md | Deterministic mapper slice: prior weekly continuity. | compacted |
| historical_context | true | 6715 | 1679 | 7582393c612d1426f0bee2141a43f2fbec9165a9a0de494943367aeda3c6f941 | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 14216 | 3554 | d09964fb0e28a42c5ef2f715079f69e36e12e4b2f5e32e642245c57d974355b7 | data/analyzed/2026-W27-press-context.md | Deterministic mapper slice: press/developer correlation context. | compacted |
| rendered_prompt | true | 84637 | 21160 | a719d206ed4deef1d1e44cf9a29d73f5c8ee9182a02028ea87a5e864617a842d |  | Exact prompt that will be passed to Copilot CLI. | included after deterministic compaction |
