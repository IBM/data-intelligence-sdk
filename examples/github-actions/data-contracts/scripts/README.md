# Python Scripts

The scripts in this directory are the core logic behind each composite action. They can also be run locally for debugging.

| Script | Purpose |
|---|---|
| [`contract_utils.py`](contract_utils.py) | Shared utility — extracts `projectId` from a contract file |
| [`validate_contract.py`](validate_contract.py) | Validate a single contract against the platform |
| [`create_contract.py`](create_contract.py) | Create or upsert contracts (PR or merge mode) |
| [`test_contract.py`](test_contract.py) | Trigger and poll test runs |
| [`delete_contract.py`](delete_contract.py) | Delete ephemeral contracts |
| [`save_test_results.py`](save_test_results.py) | Save PR test results to the real contracts after merge |

---

## Common Setup

### Install the SDK

```bash
pip install "data-intelligence-sdk==2.3.0"
```

### Environment variables (required by all scripts)

| Variable | Description |
|---|---|
| `PLATFORM_URL` | Base URL of the CPD / watsonx instance (e.g. `https://api.dai.dev.cloud.ibm.com`) |
| `PLATFORM_API_KEY` | IBM Cloud IAM API key |
| `IAM_TOKEN_URL` | *(Optional)* IAM token endpoint. Defaults to `https://iam.test.cloud.ibm.com/identity/token`. Use `https://iam.cloud.ibm.com/identity/token` for production IBM Cloud |

```bash
export PLATFORM_URL="https://api.dai.dev.cloud.ibm.com"
export PLATFORM_API_KEY="your-iam-api-key"
export IAM_TOKEN_URL="https://iam.cloud.ibm.com/identity/token"   # optional
```

---

## `contract_utils.py`

Shared utility module. Provides `extract_project_id(contract_file, fallback)` which reads `customProperties.projectId` from a contract file (JSON or YAML). All other scripts load this module at runtime via `importlib` — it is not called directly.

---

## `validate_contract.py`

Validates a single contract file against the platform API.

```bash
python .github/scripts/validate_contract.py <contract_file>
```

**Example**

```bash
python .github/scripts/validate_contract.py contracts/dc.yaml
```

### Behaviour

1. Reads `projectId` from the contract's `customProperties`.
2. Exchanges `PLATFORM_API_KEY` for a short-lived IBM Cloud IAM bearer token (endpoint from `IAM_TOKEN_URL`).
3. Calls `DataContractsProvider.validate_project_data_contract()` with the contract content.
4. Prints `VALID` or `INVALID` with a list of errors.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Contract is valid |
| `1` | Contract is invalid, missing `projectId`, or an error occurred |

---

## `create_contract.py`

Creates or replaces one or more contracts in a CPD project.

```bash
# PR mode — creates ephemeral contracts named <filename>_PR_<pr_number>
python .github/scripts/create_contract.py --mode pr --pr-number <N> <file1> [<file2> ...]

# Merge mode — upserts the real contract using the canonical filename
python .github/scripts/create_contract.py --mode merge <file1> [<file2> ...]
```

**Example**

```bash
python .github/scripts/create_contract.py --mode pr --pr-number 42 contracts/dc.yaml
python .github/scripts/create_contract.py --mode merge contracts/dc.yaml contracts/dc_2.yaml
```

### Behaviour

- Reads `projectId` from each file's `customProperties`.
- Lists existing contracts in the project (`limit=200`).
- If a contract with the target name exists → replaces it (`replace_project_data_contract`).
- If not → creates it (`create_project_data_contract`).
- Writes `contract_ids` (space-separated `project_id:contract_id` pairs) and a Markdown `body` to `GITHUB_OUTPUT` when that env var is set.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All contracts created or updated successfully |
| `1` | One or more failures, or missing `projectId` |

---

## `test_contract.py`

Triggers a test run for each contract and polls until completion.

```bash
python .github/scripts/test_contract.py <project_id:contract_id> [<project_id:contract_id> ...]
```

Each argument must be a `project_id:contract_id` pair as produced by `create_contract.py`.

**Example**

```bash
python .github/scripts/test_contract.py abc123:dc-id-001 abc123:dc-id-002
```

### Behaviour

1. Calls `DataContractsProvider.test_project_data_contract()` to trigger the run.
2. Retries up to **3 times** on transient 5xx errors (exponential backoff: 15 s, 30 s, 60 s).
3. Polls `get_project_data_contract_test_result()` every **10 seconds**, up to **30 times** (5 min max).
4. Reports per-rule check results (rule name, dataset, field, status, tested/passed/failed counts) and any schema validation issues in a Markdown table.
5. For each run with status `completed`, writes the full result to `$RESULTS_DIR/test-result_<contract_name>.json` (`RESULTS_DIR` defaults to `test-results`). `<contract_name>` is the contract's name with the `_PR_<n>` suffix removed, so the merge flow can match the file to the real contract. If the name lookup fails, the contract ID is used instead.
6. Writes `overall` (`0` = all passed, `1` = failures) and `body` to `GITHUB_OUTPUT`.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Always — the composite action's "Fail if test failed" step reads `overall` to decide whether to fail |

---

## `delete_contract.py`

Deletes ephemeral contracts and polls until each is confirmed gone.

```bash
python .github/scripts/delete_contract.py <project_id:contract_id> [<project_id:contract_id> ...]
```

**Example**

```bash
python .github/scripts/delete_contract.py abc123:dc-id-001 abc123:dc-id-002
```

### Behaviour

1. Groups contract IDs by project.
2. Issues a single `delete_project_data_contracts()` call per project (batch delete).
3. Polls `get_project_data_contract()` for each contract ID every **10 seconds**, up to **30 times** (5 min max).
4. A `404` response confirms deletion (`✅ confirmed deleted`).
5. Timeout without a `404` is reported as a warning and exits `1`.

The platform deletes DQ rule assets asynchronously before removing the contract asset itself, which is why polling is necessary.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All contracts deleted (or already absent) |
| `1` | One or more deletions failed or timed out |

---

## `save_test_results.py`

Saves the test results from a merged PR against the real contracts, using `POST /test_results`.

```bash
python .github/scripts/save_test_results.py --results-dir <dir> <project_id:contract_id> [<project_id:contract_id> ...]
```

`<dir>` is the folder holding the `test-result_<name>.json` files written by `test_contract.py` (the unzipped PR artifact). Each entry is a `project_id:contract_id` pair from `create_contract.py --mode merge`.

**Example**

```bash
python .github/scripts/save_test_results.py --results-dir ./test-results abc123:dc-id-001
```

### Behaviour

1. Looks up each contract's name with `get_project_data_contract()`.
2. Reads `<dir>/test-result_<name>.json`. If the file does not exist, the contract is skipped.
3. Removes the top-level `id` and `href`, then calls `create_project_data_contract_test_result()`.
4. Prints the new test result ID and status.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All available results saved, or nothing to save |
| `1` | A lookup or save failed, or an entry was not in `project_id:contract_id` format |
