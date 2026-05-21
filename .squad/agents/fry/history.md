# Fry — History

## Core Context
- Owns pipeline validation across crawling, analysis, and publication.
- Uses test coverage to keep workflow changes honest.

## Learnings
- The PaperMod theme in this repo needs Hugo `v0.146.0+`, so build validation must use a sufficiently new Hugo binary.
- End-to-end checks matter more than isolated unit confidence when artifacts move across crawl, analyze, and publish stages.
- Raw crawl output can be publishable with curation, but trend filters still need skepticism about exploit noise and weak momentum data.
