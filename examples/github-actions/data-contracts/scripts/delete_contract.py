#!/usr/bin/env python3
"""
Delete ephemeral data contracts from a CPD/watsonx project.

Used after PR validation to clean up ephemeral contracts created with
the _PR_<pr_number> naming pattern.

The DELETE API is asynchronous — the platform tears down the DQ rule assets
it created before the contract asset itself is removed.  After triggering the
delete this script polls get_project_data_contract per contract until the API
returns 404 (contract is gone) before reporting success.

Usage:
    python delete_contract.py <project_id:contract_id> [<project_id:contract_id> ...]

Environment variables:
    PLATFORM_URL        - (required) Base URL of the instance (e.g. https://api.dai.dev.cloud.ibm.com)
    PLATFORM_ENV        - ibm_cloud (default) | aws_cloud | gov_cloud | on_prem
    PLATFORM_API_KEY    - API key (cloud); optional for on_prem when username/password is used
    PLATFORM_USERNAME   - on_prem only
    PLATFORM_PASSWORD   - on_prem only, when no API key is given
    PLATFORM_ACCOUNT_ID - aws_cloud only
    IAM_TOKEN_URL       - optional token endpoint override (cloud environments)
A fresh bearer token is obtained at runtime via wxdi.common.auth.

Exit codes:
    0 - all contracts deleted (or already absent)
    1 - one or more deletions failed or timed out
"""

import importlib.util
import os
import sys
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wxdi.data_contracts import DataContractsProvider
from wxdi.dq_validator.provider.config import ProviderConfig

# Load contract_utils from the same directory as this script
_utils_path = os.path.join(os.path.dirname(__file__), "contract_utils.py")
_spec = importlib.util.spec_from_file_location("contract_utils", _utils_path)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
get_bearer_token = _mod.get_bearer_token

# How long to wait for a single contract to be fully removed by the platform.
# Each contract that has associated DQ rule assets may take a while.
DELETE_POLL_INTERVAL = 10   # seconds between polls
DELETE_MAX_POLLS     = 30   # 30 × 10 s = 5 minutes max per contract


def wait_for_deletion(provider: DataContractsProvider, project_id: str, cid: str) -> bool:
    """Poll until the contract is gone (404) or the timeout is reached.

    The platform deletes DQ rule assets asynchronously before removing the
    contract asset itself.  During that window get_project_data_contract keeps
    returning the contract (possibly with status='deleting' in model_extra).

    Returns:
        True  — contract is confirmed deleted (404 received)
        False — timed out; contract still present after DELETE_MAX_POLLS polls
    """
    for attempt in range(1, DELETE_MAX_POLLS + 1):
        try:
            dc = provider.get_project_data_contract(project_id, cid)
            # Derive human-readable status from the nested entity field if present
            entity   = (dc.model_extra or {}).get("entity") or {}
            ibm_dc   = entity.get("ibm_data_contract") or {}
            status   = ibm_dc.get("status") or "deleting"
            print(f"  [{attempt}/{DELETE_MAX_POLLS}] contract {cid} still present "
                  f"(status={status}) — waiting {DELETE_POLL_INTERVAL}s ...")
            time.sleep(DELETE_POLL_INTERVAL)
        except ValueError as exc:
            # The SDK raises ValueError on any non-2xx; a 404 means it's gone.
            if "404" in str(exc):
                print(f"  ✅ contract {cid} confirmed deleted (404).")
                return True
            # Any other error — log and keep polling
            print(f"  WARNING: unexpected error polling {cid}: {exc}", file=sys.stderr)
            time.sleep(DELETE_POLL_INTERVAL)

    print(f"  ⚠️  Timed out waiting for contract {cid} to be deleted.", file=sys.stderr)
    return False


def main() -> int:
    entries = sys.argv[1:]
    if not entries:
        print("No contract IDs provided — nothing to delete.")
        return 0

    cpd_url = os.environ.get("PLATFORM_URL", "").rstrip("/")

    bearer   = get_bearer_token()
    config   = ProviderConfig(url=cpd_url, auth_token=bearer)
    provider = DataContractsProvider(config)

    # Group contract IDs by project so we can batch-trigger delete per project,
    # then poll each contract individually.
    by_project: dict[str, list[str]] = {}
    for entry in entries:
        if ":" not in entry:
            print(f"ERROR: entry '{entry}' is not in project_id:contract_id format.",
                  file=sys.stderr)
            return 1
        project_id, cid = entry.split(":", 1)
        by_project.setdefault(project_id, []).append(cid)

    overall = 0
    for project_id, cids in by_project.items():
        ids_csv = ",".join(cids)
        print(f"Triggering delete of {len(cids)} ephemeral contract(s) "
              f"from project {project_id}: {ids_csv}")
        try:
            provider.delete_project_data_contracts(
                project_id,
                data_contract_ids=ids_csv,
            )
        except ValueError as exc:
            print(f"  ERROR: delete request failed for project {project_id}: {exc}",
                  file=sys.stderr)
            overall = 1
            continue

        print(f"  Delete request accepted — waiting for all DQ rules "
              f"and contract assets to be removed ...")

        # Poll each contract individually until it disappears (404).
        for cid in cids:
            if not wait_for_deletion(provider, project_id, cid):
                overall = 1

    return overall


if __name__ == "__main__":
    sys.exit(main())
