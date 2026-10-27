# data-contract-create

Creates or replaces data contracts in a CPD/watsonx project. Used in two modes: an ephemeral copy for PR validation, and a production upsert after merge.

**Source**: [`action.yml`](action.yml)  
**Script**: [`../../scripts/create_contract.py`](../../scripts/create_contract.py)

---

## Modes

| Mode | Contract name on platform | Purpose |
|---|---|---|
| `pr` | `<filename>_PR_<pr_number>` | Ephemeral copy — production contract is never touched |
| `merge` | `<filename>` (canonical) | Upserts the real production contract after merge to `main` |

If a contract with the target name already exists it is replaced (`replace_project_data_contract`); otherwise it is created fresh (`create_project_data_contract`).

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `mode` | ✅ | `pr` or `merge` |
| `changed-files` | ✅ | Space-separated list of changed contract file paths |
| `url` | ✅ | CPD / watsonx base URL |
| `environment` | ❌ | Deployment type: `ibm_cloud` (default), `aws_cloud`, `gov_cloud` or `on_prem` |
| `api-key` | ⚠️ | API key. Required for `ibm_cloud`, `aws_cloud` and `gov_cloud`; for `on_prem` provide it or `username` + `password` |
| `username` | ❌ | Username (`on_prem` only; required there) |
| `password` | ❌ | Password (`on_prem` only, when no `api-key` is given) |
| `account-id` | ❌ | Account ID (`aws_cloud` only; required there) |
| `iam-url` | ❌ | Token endpoint override for cloud environments, e.g. `https://iam.cloud.ibm.com/identity/token`. When empty, `ibm_cloud` uses the IBM Cloud **test** endpoint (`https://iam.test.cloud.ibm.com/identity/token`) and other cloud types use the SDK default. Ignored for `on_prem` |
| `pr-number` | ❌ | PR number — required when `mode` is `pr` |
| `repository` | ✅ | Repository in `owner/repo` format |
| `github-token` | ✅ | GitHub token for posting PR comments |

⚠️ = conditionally required — see [Authentication](../README.md#authentication) for what each `environment` needs.

## Outputs

| Output | Description |
|---|---|
| `contract-ids` | Space-separated `project_id:contract_id` pairs — consumed by the test and delete actions |
| `body` | Markdown summary posted as a PR comment |

---

## Behaviour

1. Installs `data-intelligence-sdk==2.3.0` from PyPI.
2. Runs `create_contract.py --mode <mode> --pr-number <pr-number> <files...>`.
3. For each file, reads `projectId` from `customProperties`, lists existing contracts, then creates or replaces.
4. Emits `contract_ids` (space-separated `project_id:contract_id` pairs) to `GITHUB_OUTPUT`.
5. Posts a success or failure PR comment (only when `pr-number` is set).

## PR comment format

```
## 📦 Data Contract Create (Ephemeral — PR validation)

### ✅ `contracts/dc.yaml` — ephemeral contract created (name: `dc_PR_42`, id: `abc-123`)

### 🔄 `contracts/dc_2.yaml` — ephemeral contract updated (name: `dc_2_PR_42`, id: `def-456`)
```
