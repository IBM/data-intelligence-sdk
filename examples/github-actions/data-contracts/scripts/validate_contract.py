#!/usr/bin/env python3
"""
Validate a single data contract file using the data-intelligence-sdk.

Usage:
    python validate_contract.py <contract_file>

Environment variables:
    PLATFORM_URL        - (required) Base URL of the instance (e.g. https://api.dai.dev.cloud.ibm.com)
    PLATFORM_ENV        - ibm_cloud (default) | aws_cloud | gov_cloud | on_prem
    PLATFORM_API_KEY    - API key (cloud); optional for on_prem when username/password is used
    PLATFORM_USERNAME   - on_prem only
    PLATFORM_PASSWORD   - on_prem only, when no API key is given
    PLATFORM_ACCOUNT_ID - aws_cloud only
    IAM_TOKEN_URL       - optional token endpoint override (cloud environments)
A fresh bearer token is obtained at runtime via wxdi.common.auth.

customProperties.projectId is required for every contract, including DPH contracts
(isDPH=true). Validation always runs against the project so that schema and rule
errors are caught before merge, regardless of where the contract ultimately lives.

For DPH contracts of type "contract", customProperties.draftId is also required,
in "<asset_id>@<catalog_id>" format. Validation additionally checks that the draft
exists and has contract terms — failing early if it is missing, malformed, or has
no contract terms id.

Exit codes:
    0 - contract is valid
    1 - contract is invalid or an error occurred
"""

import os
import sys
import importlib.util

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wxdi.data_contracts import DataContractsProvider
from wxdi.data_contracts.models import DataContractValidationRequest
from wxdi.dq_validator.provider.config import ProviderConfig


# Load contract_utils from the same directory as this script
_utils_path = os.path.join(os.path.dirname(__file__), "contract_utils.py")
_spec = importlib.util.spec_from_file_location("contract_utils", _utils_path)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
extract_project_id = _mod.extract_project_id
extract_target_info = _mod.extract_target_info
is_valid_draft_id = _mod.is_valid_draft_id
get_draft_contract_info = _mod.get_draft_contract_info
get_bearer_token = _mod.get_bearer_token


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_contract.py <contract_file>", file=sys.stderr)
        return 1

    contract_file = sys.argv[1]

    cpd_url  = os.environ.get("PLATFORM_URL", "").rstrip("/")

    # projectId is required for all contracts — DPH and non-DPH alike.
    # Validation always runs against the project (validate_project_data_contract)
    # so schema and rule errors are caught before merge.
    project_id = extract_project_id(contract_file, "")

    if not cpd_url or not project_id:
        missing = [n for n, v in [("PLATFORM_URL", cpd_url)] if not v]
        if not project_id:
            print(
                f"ERROR: customProperties.projectId not found in {contract_file}. "
                f"projectId is required for all contracts, including DPH contracts.",
                file=sys.stderr,
            )
        if missing:
            print(f"ERROR: missing required env vars: {', '.join(missing)}", file=sys.stderr)
        return 1

    target = extract_target_info(contract_file)
    draft_id = ""  # set only for DPH type "contract"; triggers the draft check below
    if target.get("is_dph") and target.get("type", "").lower() == "contract":
        draft_id = target.get("draft_id", "")
        if not draft_id:
            print(
                f"ERROR: customProperties.draftId is required when isDPH is true and type is "
                f"'contract' in {contract_file}.",
                file=sys.stderr,
            )
            return 1
        if not is_valid_draft_id(draft_id):
            print(
                f"ERROR: customProperties.draftId '{draft_id}' in {contract_file} is not in "
                f"'<asset_id>@<catalog_id>' format.",
                file=sys.stderr,
            )
            return 1

    print(f"Using project_id={project_id} for {contract_file}")

    try:
        bearer_token = get_bearer_token()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if draft_id:
        # DPH type "contract": the draft must exist and have contract terms (with an id)
        try:
            from wxdi.dph_services import DphV1
            from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
            dph = DphV1(authenticator=BearerTokenAuthenticator(bearer_token.replace("Bearer ", "").strip()))
            dph.set_service_url(cpd_url)
            _, terms_id = get_draft_contract_info(dph, draft_id)
        except Exception as exc:
            print(f"ERROR: draft {draft_id} in {contract_file} is not usable: {exc}", file=sys.stderr)
            return 1
        print(f"Draft OK: contract_terms_id={terms_id}")

    try:
        with open(contract_file, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        print(f"ERROR: Could not read {contract_file}: {exc}", file=sys.stderr)
        return 1

    config   = ProviderConfig(url=cpd_url, auth_token=bearer_token)
    provider = DataContractsProvider(config)
    body     = DataContractValidationRequest(data_contract_content=content)

    try:
        result = provider.validate_project_data_contract(project_id, body)
    except ValueError as exc:
        print(f"ERROR: Validation request failed: {exc}", file=sys.stderr)
        return 1

    if result.valid:
        print(f"VALID: {contract_file}")
        return 0

    # Print structured errors to stdout so the workflow can capture them
    print(f"INVALID: {contract_file} — {result.error_count} error(s)")
    for err in result.errors:
        prop = err.property or "(contract)"
        print(f"  [{err.type}] {prop}: {err.message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
