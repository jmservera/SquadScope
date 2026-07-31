# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `77022` tokens / `308088` bytes
- Prompt checksum: `68b08e131d8ac3b49f8aa5605a1d2937cda43b3f351f184ee56834edd58a82b2`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 13798 | 3450 | ca3f363f99078fb3b3952b54514c71d0f09312f075101d27be84d62ed0469ae2 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 75640 | 18910 | d1e23d842be5523311b9c717036256375b6d2134961213758c9af5fb3a6478a2 | data/raw/2026-W28.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 141677 | 35420 | 0532cb3654930264cfaa85739f961a04c3b9116bb56d4b881b75ae3de03f9c96 | data/raw/2026-W28.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 235447 | 58862 | 8f8371b9e3dddb24b27748106300dda76e23379cc337b97c42d439a77e67f248 | data/raw/2026-W28.json | Sanitized current weekly payload for 2026-W28. | included |
| prior_continuity | true | 10828 | 2707 | 2104cde8f416e47855f6b68fb902febd01d1403a069c51d550cad4e546e2431b | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W27-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 6637 | 1660 | c650635dbeaf3719f50f908f11f0482766cf17aebd3a9cd68f1238e246c4b63c | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 32749 | 8188 | 3aabf4c3589ed774c9b0b21bb1d7c83864e992299b3108289562e443f7d2df4c | data/analyzed/2026-W28-press-context.md | Deterministic mapper slice: press/developer correlation context. | included |
| rendered_prompt | true | 308088 | 77022 | 68b08e131d8ac3b49f8aa5605a1d2937cda43b3f351f184ee56834edd58a82b2 |  | Exact prompt that will be passed to Copilot CLI. | included |
