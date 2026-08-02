<!-- markdownlint-disable-file -->
# Planning Log: Claracle Relaunch Follow-Up Execution

## Selected Path

Execute repository-verifiable work and prepare owner-ready handoffs. Do not hardcode analytics identifiers, configure Google properties without account access, trigger duplicate-prone podcast generation, grant human sign-off, or enable rollout flags.

## Discrepancies

* The empty checked-in GA default is fork-safe configuration, not proof that production GA4 is disconnected.
* Issue #599 closed after agent-side wiring, while its human-action checklist remains incomplete.
* Issue #622 calls itself non-blocking polish; it must not be represented as a mandatory launch gate without a sponsor decision.
* A real Podcaster run and an environment-bound dry run exist, but no run combines both properties.
* Hugo/Pagefind timing separation is shipped; Q-01 requires workload attribution and retained statistics rather than another timer split.
* `discover_topic_candidates.py --check` fails against the inherited registry at commit `8fddceb`. A temporary regeneration retains 2,173 total candidates and the same five eligible candidates, while rotating four sanitized keys. This branch does not rewrite publish-derived state; refresh it through the owning generation workflow.

## Deferred Owner Actions

* jmservera: GA4 property mapping, GSC token and verification, sitemap submission, Realtime confirmation, baseline values, and rollout decisions
* Hermes: SEC-01 through SEC-06 dispositions and NFR-004 sign-off
* URL: protected environment and secret-scope review
* Podcaster maintainer: idempotency or one-run authorization
* Fry and accessibility reviewer: manual keyboard and screen-reader record
* Amy: final visual matrix and acceptance conclusion

## Safety Decisions

* Keep `GA_MEASUREMENT_ID` and `GSC_SITE_VERIFICATION` values out of source and evidence.
* Keep `repo_pages.enabled` and `topic_hubs.dynamic_creation.enabled` false.
* Keep quality thresholds unchanged.
* Keep cost thresholds report-only until approved.
* Do not dispatch real downstream generation during planning.
