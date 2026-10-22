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

All four actions install the same package before running:

```bash
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  "data-intelligence-sdk==2.3.0"
```

To upgrade, update the version string in all four `action.yml` files.
