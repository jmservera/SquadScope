# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `81548` tokens / `326189` bytes
- Prompt checksum: `bdd5e871ad6fd9846fa95e5b98e68c93d75d9a69b63602cac5a6dee38f6a94e9`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 17378 | 4345 | 1f6944ac8d79d12a43fb5292f3071af23c88a659914bf34e92c6c98bd206b5d0 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 119617 | 29905 | f04ae84c6ac9fb1caeb06fd87b50d656e1b6c726c87282374e6eaf2779a5b3f3 | data/raw/2026-W29.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 141900 | 35475 | a9c117bbc9c3b5959bf6c712378688fadbb55fcac0e7c707073207e9097633ad | data/raw/2026-W29.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 282649 | 70663 | 9aafa4ee05431b35b31a10ef552188288073093506971e0515204fdfa7ee5fec | data/raw/2026-W29.json | Sanitized current weekly payload for 2026-W29. | included |
| prior_continuity | true | 12033 | 3009 | 6518c830c646ebc5d382c657658d12b9fa2dff772a96c9fcc0c8de59040bb4c7 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W28-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 5638 | 1410 | c471f4108d2f375f635e44b6b0379ab72c36484fefa985ca549462a2995f04fa | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | false | 0 | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | data/analyzed/2026-W29-press-context.md | Deterministic mapper slice: press/developer correlation context. | not included: no press context |
| rendered_prompt | true | 326189 | 81548 | bdd5e871ad6fd9846fa95e5b98e68c93d75d9a69b63602cac5a6dee38f6a94e9 |  | Exact prompt that will be passed to Copilot CLI. | included |
