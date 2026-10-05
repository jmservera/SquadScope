# Publish-sync GitHub App

The `Sync publish data to main` workflow (`.github/workflows/sync-publish-to-main.yml`)
pushes the `sync/publish-to-main` branch and opens the weekly sync PR with a GitHub App
installation token. It then waits for the ruleset's required checks and squash-merges the PR
with `GITHUB_TOKEN`. When the merge succeeds, the run succeeds, and `Auto-dispatch podcast after
weekly article` starts from that run as before.

## Why GITHUB_TOKEN cannot open the sync PR

Ruleset `main` (16532660) requires 12 GitHub Actions checks, plus CodeQL. A PR can satisfy
those checks only with check runs from its own `statusCheckRollup`: suites that `pull_request`
(or `push`) events start for the PR, plus code scanning. With `GITHUB_TOKEN`, neither works
(jmservera/SquadScope#826):

- Since [2026-06-11](https://github.blog/changelog/2026-06-11-bot-created-pull-requests-can-run-workflows-if-approved/),
  `pull_request` runs for changes by `github-actions[bot]` wait for a human with write access to
  approve them. Without that approval they expire as zero-job failures ("This workflow run
  required approval but was not approved before it expired").
- Check runs from `workflow_dispatch` suites, which jmservera/SquadScope#820 added, report on the
  same head SHA, under the same names and app (`integration_id` 15368). They are still not part
  of the PR's rollup, so the merge API reports "12 of 12 required status checks are expected".
  On jmservera/SquadScope#822 (head `260fc0b`), all dispatched runs passed and the PR stayed
  `BLOCKED`.

Pushes and PRs from a GitHub App start ordinary `pull_request` runs without approval. The App is
**not** a ruleset bypass actor and cannot skip any check. The ruleset stays unchanged.

If the App is not configured, the first step of the workflow fails with an error that links to
this page. It does not fall back to `GITHUB_TOKEN`.

## One-time setup (repository owner)

1. **Create the App.** Go to **Settings → Developer settings → GitHub Apps → New GitHub App**
   under the `jmservera` account.
   - **GitHub App name:** for example, `claracle-publish-sync`.
   - **Homepage URL:** `https://github.com/jmservera/SquadScope`.
   - **Webhook:** clear **Active**.
   - **Repository permissions:** set **Contents** to *Read and write* and **Pull requests** to
     *Read and write*. **Metadata** is set to *Read-only* automatically. Leave every other
     permission at *No access*, including Workflows, Actions, Checks, and Administration.
   - **Where can this GitHub App be installed?** select *Only on this account*.
2. **Copy the Client ID** from the App's **General** page. It looks like `Iv23li…`.
3. **Generate a private key** under **Private keys** and download the `.pem` file.
4. **Install the App.** On the **Install App** page, choose *Only select repositories* →
   `jmservera/SquadScope`.
5. **Create the `publish-sync` environment.** Restrict it to `main`, with no required
   reviewers and no wait timer:

   ```bash
   gh api -X PUT repos/jmservera/SquadScope/environments/publish-sync \
     -F 'deployment_branch_policy[protected_branches]=false' \
     -F 'deployment_branch_policy[custom_branch_policies]=true'
   gh api -X POST repos/jmservera/SquadScope/environments/publish-sync/deployment-branch-policies \
     -f name=main -f type=branch
   ```

6. **Store the credentials in that environment.** Store them in the environment, not at repository level:

   ```bash
   gh variable set PUBLISH_SYNC_APP_CLIENT_ID --env publish-sync \
     --repo jmservera/SquadScope --body 'Iv23li...'
   gh secret set PUBLISH_SYNC_APP_PRIVATE_KEY --env publish-sync \
     --repo jmservera/SquadScope < claracle-publish-sync.private-key.pem
   ```

   Then delete the local `.pem` file.

## Verify

- `gh workflow run sync-publish-to-main.yml --repo jmservera/SquadScope` checks the
  configuration gate. If `publish` has nothing new for `main`, the run stops at "No changes to
  sync" and does not mint a token or open a PR. A successful run still starts
  `Auto-dispatch podcast after weekly article`. That workflow only reaches Podcaster through
  the protected `podcaster-real-generation` environment approval, so deny or leave that
  approval pending for a validation-only run. You can also set `PODCAST_AUTO_DISPATCH_PAUSED`
  to `true` beforehand.
- The weekly run should show the sync PR authored by `app/<app-slug>`. Its required checks should
  come from `pull_request` runs with no "approval required" banner, and the
  `Wait for required checks and merge` step should merge it.

## Operations

- **Key rotation:** generate a new private key, update `PUBLISH_SYNC_APP_PRIVATE_KEY`, then
  delete the old key from the App.
- **Legacy PR:** if an open sync PR was authored by `github-actions[bot]`, the workflow closes it
  and opens a new PR as the App.
- **Merge failure:** the merge step prints the PR's `mergeStateStatus`. Typical causes are a
  failed required check, an unresolved review thread (the ruleset requires thread resolution),
  or a CodeQL alert. Fix the cause and re-run the workflow. Never merge with `--admin`.
