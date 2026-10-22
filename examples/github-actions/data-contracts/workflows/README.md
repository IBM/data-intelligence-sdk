# CI/CD Workflow

The pipeline is defined in [`validate-data-contract.yml`](validate-data-contract.yml) and triggers on two events:

| Event | Paths watched | What runs |
|---|---|---|
| `pull_request` | `contracts/**`, `.github/workflows/**`, `.github/actions/**`, `.github/scripts/**` | PR flow (validate → create → test → delete) |
| `push` to `main` | `contracts/**` | Merge flow (upsert real contracts, then save test results) |

---

## PR Flow

When a pull request adds or modifies any file under `contracts/`, four jobs run in sequence. A PR comment is posted after each job so reviewers have full visibility without leaving GitHub.

```
PR opened / updated (contracts/** changed)
│
├─ Job 1: validate
│      Validates each changed contract file against the platform API.
│      Fails fast if any contract is invalid — subsequent jobs are skipped.
│
├─ Job 2: create-temp-contract         (needs: validate)
│      Creates an ephemeral copy of each contract named
│      <filename>_PR_<pr_number> in the target project.
│      The real production contract is never touched.
│
├─ Job 3: test                         (needs: create-temp-contract)
│      Triggers a test run against each ephemeral contract.
│      Polls until the run completes, then reports per-rule results.
│      Uploads each completed run's result as a JSON workflow artifact and
│      links it from the PR comment.
│
└─ Job 4: delete-temp-contract         (needs: create-temp-contract + test)
       Runs with `if: always()` — executes even if Job 3 failed.
       Deletes all ephemeral contracts and polls until each is confirmed gone (404).
```

### Job conditions

| Job | Condition |
|---|---|
| `validate` | `github.event_name == 'pull_request'` |
| `create-temp-contract` | PR event **and** at least one contract file changed |
| `test` | PR event **and** `create-temp-contract` produced contract IDs |
| `delete-temp-contract` | `always()` **and** PR event **and** contract IDs exist |

---

## Merge Flow

After a PR is merged to `main`, a single job runs:

**`upsert-on-merge`** — runs two steps:

1. **Upsert real contracts** — detects files changed since the last remote commit, then calls the [create action](../actions/data-contract-create/README.md) in `merge` mode. This upserts each changed contract using its canonical name (the filename without extension). If a contract with that name already exists in the project it is replaced; otherwise it is created fresh.
2. **Save PR test results** — calls the [save-results action](../actions/data-contract-save-results/README.md), which downloads the JSON test results uploaded by the merged PR's test job and saves each one to the matching real contract with `POST /test_results`. Contracts with no saved result are skipped.

No PR comment is posted on merge — results are visible in the Actions run log.

---

## Required Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `PLATFORM_URL` | Base URL of the CPD / watsonx instance (e.g. `https://api.dai.dev.cloud.ibm.com`) |
| `PLATFORM_API_KEY` | IBM Cloud IAM API key with access to the target project |

`GITHUB_TOKEN` is provided automatically by GitHub Actions — no manual configuration needed.

---

## Workflow Permissions

```yaml
permissions:
  pull-requests: write   # post PR comments
  contents: read         # checkout the repository
  actions: read          # download the PR's test-result artifact on merge
```

---

## Changed-file Detection

Both flows use [`tj-actions/changed-files@v44`](https://github.com/tj-actions/changed-files) to detect which files under `contracts/**` were modified. Only changed files are processed — unchanged contracts are skipped entirely.
