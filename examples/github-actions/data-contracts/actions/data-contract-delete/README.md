# data-contract-delete

Deletes ephemeral contracts created during PR validation and polls until each is confirmed gone from the platform.

**Source**: [`action.yml`](action.yml)  
**Script**: [`../../scripts/delete_contract.py`](../../scripts/delete_contract.py)

This action always runs (`if: always()`) — even when the test job fails — guaranteeing cleanup of ephemeral contracts regardless of pipeline outcome.

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

---

## Behaviour

1. Installs `data-intelligence-sdk==2.3.0` from PyPI.
2. Runs `delete_contract.py <contract-ids>`.
3. Groups IDs by project and issues one `delete_project_data_contracts()` call per project (batch delete).
4. The platform deletes DQ rule assets asynchronously before removing the contract itself — the script polls `get_project_data_contract()` for each ID every **10 seconds**, up to **30 times** (5 min max).
5. A `404` response confirms deletion.
6. Posts a success or failure PR comment.

> **If cleanup fails**, the PR comment instructs reviewers to delete orphaned contracts manually from the project.

---

## PR comment format

On success:

```
## 🗑️ Ephemeral Contracts Cleaned Up

2 ephemeral contract(s) deleted after PR validation.

```
project_id:contract_id_1 project_id:contract_id_2
```
```

On failure:

```
## ⚠️ Ephemeral Contract Cleanup — failed

One or more ephemeral contracts could not be deleted.
Please remove them manually from the project.
```
