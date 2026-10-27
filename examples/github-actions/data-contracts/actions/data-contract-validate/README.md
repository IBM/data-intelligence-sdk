# data-contract-validate

Validates changed data contract files against the platform using the `data-intelligence-sdk` and posts a PR comment with the results.

**Source**: [`action.yml`](action.yml)  
**Script**: [`../../scripts/validate_contract.py`](../../scripts/validate_contract.py)

If any contract is invalid the job fails, blocking the downstream `create-temp-contract` job from running.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `changed-files` | ✅ | Space-separated list of changed contract file paths |
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
| `overall` | `0` = all contracts valid, `1` = one or more failures |
| `body` | Markdown summary posted as a PR comment |

---

## Behaviour

1. Installs `data-intelligence-sdk==2.3.0` from PyPI.
2. Iterates over each file in `changed-files` and runs `validate_contract.py` against it.
3. Collects pass/fail results into a Markdown summary.
4. Posts the summary as a PR comment via `gh pr comment`.
5. Exits `1` if `overall == 1`, failing the job.

## PR comment format

```
## 🔍 Data Contract Validation

### ✅ `contracts/dc.yaml` — valid

### ❌ `contracts/dc_2.yaml` — validation failed

```
<error output>
```
```
