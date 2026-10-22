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
| `api-key` | ✅ | IBM Cloud IAM API key |
| `pr-number` | ✅ | PR number to post the comment on |
| `repository` | ✅ | Repository in `owner/repo` format |
| `github-token` | ✅ | GitHub token for posting PR comments |

---

## Behaviour

1. Installs `data-intelligence-sdk==2.3.0` from TestPyPI.
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
