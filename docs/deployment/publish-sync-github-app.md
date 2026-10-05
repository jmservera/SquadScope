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

If the App is not configured, or `PUBLISH_SYNC_APP_PRIVATE_KEY` lacks the PEM
`BEGIN`/`END … PRIVATE KEY-----` lines, the first step of the workflow fails with an error that
links to this page. This is only a shape check. A key body that has both lines but is invalid
still fails later, at the token mint step. It does not fall
back to `GITHUB_TOKEN`.

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
3. **Generate a private key.** On the App's page (**Settings → Developer settings → GitHub
   Apps → your App**), scroll to **Private keys** and click **Generate a private key**. The
   browser downloads a `.pem` file that starts with `-----BEGIN RSA PRIVATE KEY-----` and ends
   with `-----END RSA PRIVATE KEY-----`. This file is the value of
   `PUBLISH_SYNC_APP_PRIVATE_KEY`.

   > [!IMPORTANT]
   > Do **not** use **Client secrets → Generate a new client secret**. A client secret is for
   > the OAuth web flow. It cannot sign the App's JWT, so the token mint step fails.
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

   Always set the secret from the file with `<`, as shown. If you run `gh secret set` without
   input and paste the key at the prompt, only the first line is stored, and the stored value
   is not a usable key. Then delete the local `.pem` file.

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

Validated end to end on 2026-10-05: run
[37381144815](https://github.com/jmservera/SquadScope/actions/runs/37381144815) opened sync PR
jmservera/SquadScope#828 as `app/squadscope-pr-app`, waited for the required checks, and merged
it. The podcast auto-dispatch dedup then skipped W41, which already had an episode.

## Operations

- **Key rotation:** generate a new private key, update `PUBLISH_SYNC_APP_PRIVATE_KEY`, then
  delete the old key from the App.
- **Legacy PR:** if an open sync PR was authored by `github-actions[bot]`, the workflow closes it
  and opens a new PR as the App.
- **Merge failure:** the merge step prints the PR's `mergeStateStatus`. Typical causes are a
  failed required check, an unresolved review thread (the ruleset requires thread resolution),
  or a CodeQL alert. Fix the cause and re-run the workflow. Never merge with `--admin`.

## Troubleshooting

- **`Invalid keyData` or `ERR_OSSL_ASN1_NOT_ENOUGH_DATA` in `Mint publish-sync GitHub App
  token`:** `PUBLISH_SYNC_APP_PRIVATE_KEY` is not a full PEM private key. Usually it holds an
  OAuth client secret, or a paste that kept only the first line. Generate a private key (step 3),
  set the secret from the `.pem` file with `< key.pem` (step 6), and re-run the workflow. The
  configuration gate catches both cases before the mint step with a shape check. It fails with
  "PUBLISH_SYNC_APP_PRIVATE_KEY is not a PEM private key" when the secret has no
  `-----BEGIN … PRIVATE KEY-----` or `-----END … PRIVATE KEY-----` line.
