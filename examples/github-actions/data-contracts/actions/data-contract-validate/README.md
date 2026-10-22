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
| `api-key` | ✅ | IBM Cloud IAM API key |
| `iam-url` | ❌ | IAM token endpoint, e.g. `https://iam.cloud.ibm.com/identity/token`. Defaults to the IBM Cloud **test** endpoint (`https://iam.test.cloud.ibm.com/identity/token`) when empty |
| `pr-number` | ✅ | PR number to post the comment on |
| `repository` | ✅ | Repository in `owner/repo` format |
| `github-token` | ✅ | GitHub token for posting PR comments |

## Outputs

| Output | Description |
|---|---|
| `overall` | `0` = all contracts valid, `1` = one or more failures |
| `body` | Markdown summary posted as a PR comment |

---

## Behaviour

1. Installs `data-intelligence-sdk==2.3.0` from TestPyPI.
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
