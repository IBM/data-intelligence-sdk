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

Environment variables (required):
    PLATFORM_URL     - Base URL of the instance (e.g. https://api.dai.dev.cloud.ibm.com)
    PLATFORM_API_KEY - IBM Cloud IAM API key; a fresh bearer token is obtained at runtime

Exit codes:
    0 - all contracts deleted (or already absent)
    1 - one or more deletions failed or timed out
"""

import os
import sys
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wxdi.data_contracts import DataContractsProvider
from wxdi.dq_validator.provider.config import ProviderConfig

IAM_TOKEN_URL = "https://iam.test.cloud.ibm.com/identity/token"

# How long to wait for a single contract to be fully removed by the platform.
# Each contract that has associated DQ rule assets may take a while.
DELETE_POLL_INTERVAL = 10   # seconds between polls
DELETE_MAX_POLLS     = 30   # 30 × 10 s = 5 minutes max per contract


def get_bearer_token(api_key: str) -> str:
    resp = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=30,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError("IAM response did not contain access_token")
    return f"Bearer {token}"


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
    api_key = os.environ.get("PLATFORM_API_KEY", "")

    bearer   = get_bearer_token(api_key)
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
