# data-contract-test

Triggers test runs for ephemeral contracts, polls until completion, and posts a detailed PR comment with per-rule check results and schema validation issues.

**Source**: [`action.yml`](action.yml)  
**Script**: [`../../scripts/test_contract.py`](../../scripts/test_contract.py)

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `contract-ids` | ✅ | Space-separated `project_id:contract_id` pairs (from the create action) |
| `url` | ✅ | CPD / watsonx base URL |
| `environment` | ❌ | Deployment type: `ibm_cloud` (default), `aws_cloud`, `gov_cloud` or `on_prem` |
| `api-key` | ⚠️ | API key. Required for `ibm_cloud`, `aws_cloud` and `gov_cloud`; for `on_prem` provide it or `username` + `password` |
| `username` | ❌ | Username (`on_prem` only; required there) |
| `password` | ❌ | Password (`on_prem` only, when no `api-key` is given) |
| `account-id` | ❌ | Account ID (`aws_cloud` only; required there) |
| `iam-url` | ❌ | Token endpoint override for cloud environments, e.g. `https://iam.cloud.ibm.com/identity/token`. When empty, `ibm_cloud` uses the IBM Cloud **test** endpoint (`https://iam.test.cloud.ibm.com/identity/token`) and other cloud types use the SDK default. Ignored for `on_prem` |
| `pr-number` | ✅ | PR number to post the comment on |
| `repository` | ✅ | Repository in `owner/repo` format |
| `github-token` | ✅ | GitHub token for posting PR comments |

⚠️ = conditionally required — see [Authentication](../README.md#authentication) for what each `environment` needs.

## Outputs

| Output | Description |
|---|---|
| `overall` | `0` = all tests passed, `1` = one or more failures |
| `body` | Markdown summary posted as a PR comment |

---

## Behaviour

1. Installs `data-intelligence-sdk==2.3.0` from PyPI.
2. Runs `test_contract.py <contract-ids>`.
3. For each contract, triggers a test run via `test_project_data_contract()`.
4. Retries up to **3 times** on transient 5xx errors (exponential backoff: 15 s → 30 s → 60 s).
5. Polls `get_project_data_contract_test_result()` every **10 seconds**, up to **30 times** (5 min max per contract).
6. Collects per-rule check results and schema validation issues into a Markdown table.
7. For each contract whose run is `completed`, writes the full test result to `test-results/test-result_<contract_name>.json`. `<contract_name>` is the contract's name without the `_PR_<n>` suffix, so the [save-results action](../data-contract-save-results/README.md) can match the file to the real contract after merge.
8. Writes `overall` and `body` to `GITHUB_OUTPUT`.
9. Uploads the `test-results/` JSON files as a workflow artifact (`data-contract-test-results-pr-<pr-number>`).
10. Posts a success or failure PR comment. On success the comment ends with a link to the artifact.
11. A dedicated "Fail if test failed" step reads `overall` and calls `exit 1` if needed — the script itself always exits `0` to ensure the comment step always runs.

---

## PR comment format

```
## 🧪 Data Contract Test Run

### ✅ `abc-123` — test completed
> Run ID: `run-001` | Started: 2024-01-01T10:00:00Z | Ended: 2024-01-01T10:02:00Z

**Check Results**

| Rule | Dataset | Field | Status | Tested | Passed | Failed |
|---|---|---|---|---|---|---|
| Null Value Check | BANK_CLIENTS | ACCOUNT_ID | `passed` | 5112 | 5112 | 0 |

📎 [Download test result JSON](https://github.com/<owner>/<repo>/actions/runs/<run_id>/artifacts/<artifact_id>)
```

GitHub's API cannot attach files to a PR comment, so the JSON is uploaded as a workflow artifact and linked from the comment. Artifacts require GitHub sign-in to download and expire per the repository's retention setting (90 days by default).
