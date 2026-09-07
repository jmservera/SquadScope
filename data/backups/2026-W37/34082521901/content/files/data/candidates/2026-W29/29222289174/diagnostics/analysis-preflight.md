# Analysis Prompt Preflight

- Prompt budget: `90000` tokens
- Rendered prompt: `79528` tokens / `318110` bytes
- Prompt checksum: `0b44f66f5c6ca212638bfc32a53ba64221d9a05fa4238ad498f948f17f9e46ce`
- Degraded/compacted: `false`
- Degradation reason: none
- Publish eligible: `true`
- Promotion policy: normal-promotion
- Fallback policy: copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. degraded/compacted prompts are staged/candidate-only by default.
- Deterministic slices: new_repos, trending_repos, press_correlations, prior_continuity

| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| prompt_template | true | 13798 | 3450 | ca3f363f99078fb3b3952b54514c71d0f09312f075101d27be84d62ed0469ae2 | /home/runner/work/SquadScope/SquadScope/prompts/analyze-weekly.md | Base weekly analysis instructions. | included |
| new_repos | true | 81832 | 20458 | 66cb5716257ebba83b80816a0da39cc938efb243384d9565429b66bb4fda5b36 | data/raw/2026-W29.json | Deterministic mapper slice: newly discovered repositories. | included |
| trending_repos | true | 141958 | 35490 | 3cd3f7b5d6a5b769274b51fe00bda21799bba4d596918066cb6c3f516a97b0a6 | data/raw/2026-W29.json | Deterministic mapper slice: continuing/trending repositories. | included |
| raw_metadata | true | 242582 | 60646 | 5a0c4a6799af399bca3512fe944dcd305d3ffce740fa37e0162d3e5738ea0c2c | data/raw/2026-W29.json | Sanitized current weekly payload for 2026-W29. | included |
| prior_continuity | true | 12033 | 3009 | 6518c830c646ebc5d382c657658d12b9fa2dff772a96c9fcc0c8de59040bb4c7 | /home/runner/work/SquadScope/SquadScope/data/analyzed/2026-W28-summary.md | Deterministic mapper slice: prior weekly continuity. | included |
| historical_context | true | 8502 | 2126 | 90889f598322a25c422f4daa5a4e512cbee8bda5a2d5e077a788850642391adf | /home/runner/work/SquadScope/SquadScope/content | Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports. | included |
| analysis_wisdom | true | 2169 | 543 | c72d292ae4407cccf115c08f0bcc9c48263e2ea052bd5cfd2423d432b3c86d9f | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/wisdom.md | Analysis-specific wisdom capsule from topic learning state. | included |
| analysis_skills | true | 3644 | 911 | 2fc0bad5a4e314633feaaf02942a6a4ebd6158b6d7d6a645b9d0c3e2d6f9b05d | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/skills | Analysis-specific learned skill capsule from topic learning state. | included |
| analysis_continuity | true | 2730 | 683 | 8b02154127eaed7320b2af8ea12b68250cd8335b4b23108d7ce3be0620d25006 | /home/runner/work/SquadScope/SquadScope/.squad/topics/ai-ml/continuity.md | Analysis continuity capsule distilled from recent multi-week learnings. | included |
| press_correlations | true | 32566 | 8142 | 6a5d587b6d6d0e716313b53c3fd1a89e27d1e0c08e22775405e6cba93a6f9741 | data/analyzed/2026-W29-press-context.md | Deterministic mapper slice: press/developer correlation context. | included |
| rendered_prompt | true | 318110 | 79528 | 0b44f66f5c6ca212638bfc32a53ba64221d9a05fa4238ad498f948f17f9e46ce |  | Exact prompt that will be passed to Copilot CLI. | included |
