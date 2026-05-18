# Bender Decision Inbox — Run Counter & Reskill Trigger

- **Date:** 2026-05-18T15:22:25.067+02:00
- **Author:** Bender
- **Issue:** #15 — Add run counter persistence and every-fifth-run reskill trigger

## Context

The weekly crawl workflow already serializes runs with `concurrency`, but the learning audit found two missing pieces: there was no persisted `.squad/run-counter.txt`, and no workflow job checked that counter to trigger the every-5th-run reskill cycle.

## Decision

1. Create `.squad/run-counter.txt` in the repository, initialized to `0`.
2. Increment the counter inside the `crawl` job's git commit step **after** syncing the default branch, then commit `.squad/run-counter.txt` together with `data/raw/` and `data/snapshots/`.
3. Add a dedicated `reskill-check` job that reads the persisted counter and exposes `should_reskill` for downstream jobs.
4. Add a gated placeholder `reskill` job that logs the trigger and scaffolds `.squad/skills/` and `.squad/reskill/` until Issue #14 adds the full retrospective implementation.

## Why

- Reading the counter only after syncing `origin/main` keeps the increment tied to the latest persisted state.
- Committing `.squad/run-counter.txt` in the same crawl commit ensures the trigger survives between weekly runs.
- Splitting `reskill-check` from `reskill` keeps the trigger logic auditable and makes the future reskill implementation easier to extend.

## Follow-up

- Issue #14 should add `.squad/` persistence for reskill outputs and the actual retrospective prompt/output flow.
