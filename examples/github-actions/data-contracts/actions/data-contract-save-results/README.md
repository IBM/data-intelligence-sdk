# data-contract-save-results

After a PR is merged, finds the test results produced by that PR's test run and saves them against the real contracts using `POST /test_results`.

**Source**: [`action.yml`](action.yml)  
**Script**: [`../../scripts/save_test_results.py`](../../scripts/save_test_results.py)

Runs only in the merge flow, right after the [create action](../data-contract-create/README.md) in `merge` mode.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `contract-ids` | ✅ | Space-separated `project_id:contract_id` pairs from the create action in `merge` mode |
| `url` | ✅ | CPD / watsonx base URL |
| `environment` | ❌ | Deployment type: `ibm_cloud` (default), `aws_cloud`, `gov_cloud` or `on_prem` |
| `api-key` | ⚠️ | API key. Required for `ibm_cloud`, `aws_cloud` and `gov_cloud`; for `on_prem` provide it or `username` + `password` |
| `username` | ❌ | Username (`on_prem` only; required there) |
| `password` | ❌ | Password (`on_prem` only, when no `api-key` is given) |
| `account-id` | ❌ | Account ID (`aws_cloud` only; required there) |
| `iam-url` | ❌ | Token endpoint override for cloud environments, e.g. `https://iam.cloud.ibm.com/identity/token`. When empty, `ibm_cloud` uses the IBM Cloud **test** endpoint (`https://iam.test.cloud.ibm.com/identity/token`) and other cloud types use the SDK default. Ignored for `on_prem` |
| `repository` | ✅ | Repository in `owner/repo` format |
| `github-token` | ✅ | GitHub token used to find the merged PR and download its artifact (the workflow needs `actions: read`) |

⚠️ = conditionally required — see [Authentication](../README.md#authentication) for what each `environment` needs.

This action has no outputs and posts no PR comment.

---

## Behaviour

1. Finds the merged PR from the commit SHA (`GET /repos/{repo}/commits/{sha}/pulls`).
2. Finds the newest unexpired artifact named `data-contract-test-results-pr-<pr-number>`, which the [test action](../data-contract-test/README.md) uploaded during the PR, then downloads and unzips it.
3. Installs `data-intelligence-sdk==2.3.0` from PyPI and runs `save_test_results.py`.
4. For each contract, looks up its name, picks `test-result_<name>.json` from the artifact, and saves it with `POST /data_quality/v4/projects/{project_id}/data_contracts/{id}/test_results`. The top-level `id` and `href` are removed because the server generates them.

If the merge has no associated PR, or the PR has no unexpired artifact, the action logs that and does nothing. A contract with no matching file is skipped. A failed save fails the job.

> Artifacts expire after the repository's retention period (90 days by default). Merges after that point save no test results.
