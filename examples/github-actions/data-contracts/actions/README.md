# Composite Actions

Each stage of the pipeline is implemented as a reusable [composite action](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action). All four actions install `data-intelligence-sdk==2.3.0` from TestPyPI before running their Python script.

| Action | README | Purpose |
|---|---|---|
| `data-contract-validate` | [README](data-contract-validate/README.md) | Validate contract files against the platform |
| `data-contract-create` | [README](data-contract-create/README.md) | Create or upsert contracts (PR or merge mode) |
| `data-contract-test` | [README](data-contract-test/README.md) | Trigger and poll test runs |
| `data-contract-delete` | [README](data-contract-delete/README.md) | Delete ephemeral contracts after PR validation |
| `data-contract-save-results` | [README](data-contract-save-results/README.md) | After merge, save the PR's test results to the real contracts |

---

## SDK Dependency

All five actions install the same package before running:

```bash
pip install "data-intelligence-sdk==2.3.0"
```

To upgrade, update the version string in all five `action.yml` files.

---

## IAM Endpoint

Every action accepts an optional `iam-url` input — the IAM token endpoint used to exchange `api-key` for a bearer token. It is passed to the scripts as the `IAM_TOKEN_URL` environment variable.

| Environment of the API key | `iam-url` |
|---|---|
| IBM Cloud test (default when empty) | `https://iam.test.cloud.ibm.com/identity/token` |
| IBM Cloud production | `https://iam.cloud.ibm.com/identity/token` |

The bundled workflow supplies it from the optional `IAM_TOKEN_URL` repository secret, so switching environments needs no code change.
