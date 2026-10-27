#!/usr/bin/env python3
"""
Create data contracts in a CPD/watsonx project.

Two modes:

  --mode pr   (PR validation)
      Creates an ephemeral contract named "<contract_name>_PR_<pr_number>"
      in the project (customProperties.projectId) - always, even for DPH
      contracts. Used for CI testing only and deleted afterwards.
      Emits contract_ids as "<project_id>:<contract_id>" pairs.

  --mode merge  (post-merge upsert)
      Creates or replaces the real contract using the canonical name from
      the contract file. DPH contracts (isDPH=true) go to the DPH catalog and
      are linked to the draft; all others go to the project. Emits
      "<project_id>:<contract_id>" pairs, or "catalog:<catalog_id>:<contract_id>"
      for contracts created in the DPH catalog. The catalog is taken from
      customProperties.catalogId when present, else resolved via the DPH API.

Usage:
    python create_contract.py --mode pr   --pr-number <N> <file1> [<file2> ...]
    python create_contract.py --mode merge               <file1> [<file2> ...]

Environment variables:
    PLATFORM_URL        - (required) Base URL of the instance (e.g. https://api.dai.dev.cloud.ibm.com)
    PLATFORM_ENV        - ibm_cloud (default) | aws_cloud | gov_cloud | on_prem
    PLATFORM_API_KEY    - API key (cloud); optional for on_prem when username/password is used
    PLATFORM_USERNAME   - on_prem only
    PLATFORM_PASSWORD   - on_prem only, when no API key is given
    PLATFORM_ACCOUNT_ID - aws_cloud only
    IAM_TOKEN_URL       - optional token endpoint override (cloud environments)
A fresh bearer token is obtained at runtime via wxdi.common.auth.

Project ID is read exclusively from customProperties.projectId in each contract file.

Exit codes:
    0 - all contracts created/updated successfully
    1 - one or more contracts failed or an error occurred

Writes GITHUB_OUTPUT:
    body         - Markdown summary for PR comment
    contract_ids - Space-separated list of <project_id>:<contract_id> pairs
                   (DPH catalog: "catalog:<catalog_id>:<contract_id>")
"""

import os
import sys
import json
import argparse
import importlib.util
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wxdi.data_contracts import DataContractsProvider
from wxdi.data_contracts.models import DataContractPrototypeJson, DataContractPrototypeYaml
from wxdi.dq_validator.provider.config import ProviderConfig

# Load contract_utils from the same directory as this script
_utils_path = os.path.join(os.path.dirname(__file__), "contract_utils.py")
_spec = importlib.util.spec_from_file_location("contract_utils", _utils_path)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
extract_target_info = _mod.extract_target_info
is_valid_draft_id = _mod.is_valid_draft_id
get_draft_contract_info = _mod.get_draft_contract_info
_YAML_AVAILABLE = _mod._YAML_AVAILABLE
get_bearer_token = _mod.get_bearer_token


def get_dph_client(cpd_url: str, bearer_token: str):
    """Create and return a configured DphV1 client."""
    from wxdi.dph_services import DphV1
    from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator

    raw_token = bearer_token.replace("Bearer ", "").strip()
    authenticator = BearerTokenAuthenticator(raw_token)
    dph = DphV1(authenticator=authenticator)
    dph.set_service_url(cpd_url)
    return dph


def get_dph_catalog_id(dph) -> str:
    """Fetch the default Data Product Hub catalog ID via DphV1.get_initialize_status().

    Extracts the catalog ID from the container.id query parameter in the
    response href. Raises RuntimeError when DPH is unavailable or not yet
    initialized — initialization is an operator responsibility and must not
    be triggered automatically by CI.
    """
    from urllib.parse import urlparse, parse_qs
    from ibm_cloud_sdk_core.api_exception import ApiException

    try:
        resp = dph.get_initialize_status()
        res = resp.get_result() if hasattr(resp, "get_result") else resp.result
    except ApiException as exc:
        raise RuntimeError(
            f"DPH status check failed (status={exc.status_code}): {exc.message}. "
            "Ensure the PLATFORM_URL points to a fully initialized DPH instance."
        ) from exc

    status = res.get("status", "")
    if status != "succeeded":
        raise RuntimeError(
            f"DPH initialization has not succeeded (status={status!r}). "
            "Ensure the DPH instance is fully initialized before running contracts."
        )

    # Extract catalog ID from container.id query param in href
    href = res.get("href", "")
    catalog_id = parse_qs(urlparse(href).query).get("container.id", [None])[0]
    if not catalog_id:
        raise RuntimeError(f"DPH catalog container ID not found in href: {href!r}")

    return catalog_id


def link_contract_to_data_product_draft(dph, draft_id: str, contract_terms_id: str, contract_id: str, data_product_id: str = "-"):
    """Link data contract to draft contract terms using an 'add' JSON patch."""
    from wxdi.dph_services.dph_v1 import JsonPatchOperation

    print(f"  Linking contract {contract_id} to draft {draft_id} (contract_terms_id: {contract_terms_id}) ...")
    patch_op = JsonPatchOperation(op="add", path="/data_contract_id", value=contract_id)
    dph.update_data_product_draft_contract_terms(
        data_product_id=data_product_id,
        draft_id=draft_id,
        contract_terms_id=contract_terms_id,
        json_patch_instructions=[patch_op],
    )
    print(f"  Successfully linked data_contract_id={contract_id} to draft {draft_id}")


def parse_contract_content(content: str) -> dict:
    """Parse contract file content (JSON or YAML) into a dict."""
    try:
        doc = json.loads(content)
    except json.JSONDecodeError:
        if not _YAML_AVAILABLE:
            raise RuntimeError(
                "Contract file is not valid JSON and PyYAML is not installed — "
                "install pyyaml to support YAML contract files."
            )
        import yaml
        doc = yaml.safe_load(content)
    if not isinstance(doc, dict):
        raise RuntimeError("Contract file did not parse to an object")
    return doc


def _get_catalog_dc_type(dc) -> str:
    """Return the lowercased type string from a catalog DataContract, or "".

    DataContract has a declared `type` field that is populated when the server
    returns the flat OpenAPI shape.  In practice the catalog API returns the
    nested CAMS asset shape instead, where `type` is not promoted by the SDK's
    _promote_nested_fields validator — so dc.type is None for real responses.
    The actual value lives in the nested path:
        model_extra["entity"]["ibm_data_contract"]["type"]
    The flat dc.type check is kept as a forward-compatibility fallback in case
    a future SDK version starts promoting the field.
    """
    # Flat shape (promoted by SDK — future-proofing)
    flat = getattr(dc, "type", None)
    if flat:
        return str(flat).lower()
    # Nested CAMS asset shape (current real API response)
    entity = ((getattr(dc, "model_extra", None) or {}).get("entity") or {})
    nested = (entity.get("ibm_data_contract") or {}).get("type")
    return str(nested).lower() if nested else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pr", "merge"], required=True,
                        help="'pr' creates an ephemeral contract; 'merge' upserts the real one")
    parser.add_argument("--pr-number", default="",
                        help="PR number — required when --mode pr")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    if not args.files:
        print("No contract files provided — nothing to create.")
        return 0

    if args.mode == "pr" and not args.pr_number:
        print("ERROR: --pr-number is required when --mode pr", file=sys.stderr)
        return 1

    cpd_url = os.environ.get("PLATFORM_URL", "").rstrip("/")

    bearer   = get_bearer_token()
    config   = ProviderConfig(url=cpd_url, auth_token=bearer)
    provider = DataContractsProvider(config)

    result_lines   = []
    contract_pairs = []

    # Cache DPH client and catalog id if needed
    dph_client = None
    dph_catalog_id = None

    for f in args.files:
        canonical_name = os.path.splitext(os.path.basename(f))[0]

        # In PR mode use an ephemeral name so the real contract is untouched
        if args.mode == "pr":
            name = f"{canonical_name}_PR_{args.pr_number}"
        else:
            name = canonical_name

        target = extract_target_info(f)
        is_dph = target.get("is_dph", False)
        contract_type = target.get("type", "").lower()
        is_contract_type = contract_type == "contract"
        draft_id = target.get("draft_id", "")
        data_product_id = "-"
        project_id = target.get("project_id", "")

        # Catalog (DPH) is the final state only: PR validation always uses a
        # temporary contract in the project so the catalog/draft stay untouched.
        if is_dph and args.mode == "merge":
            if not dph_client:
                dph_client = get_dph_client(cpd_url, bearer)
            # customProperties.catalogId (optional) is used directly; otherwise
            # resolve the default DPH catalog with an extra API call (cached).
            file_catalog_id = target.get("catalog_id", "")
            if file_catalog_id:
                catalog_id = file_catalog_id
            else:
                if not dph_catalog_id:
                    try:
                        dph_catalog_id = get_dph_catalog_id(dph_client)
                    except Exception as exc:
                        print(f"ERROR: Failed to resolve DPH catalog for {f}: {exc}", file=sys.stderr)
                        sys.exit(1)
                catalog_id = dph_catalog_id

            # When type is "contract", draftId is mandatory, as "<asset_id>@<catalog_id>"
            if is_contract_type and not draft_id:
                print(f"ERROR: customProperties.draftId is required when isDPH is true and type is 'contract' in {f}.",
                      file=sys.stderr)
                sys.exit(1)
            if is_contract_type and not is_valid_draft_id(draft_id):
                print(f"ERROR: customProperties.draftId '{draft_id}' in {f} is not in "
                      "'<asset_id>@<catalog_id>' format.", file=sys.stderr)
                sys.exit(1)

            container_id = catalog_id
            container_type = "catalog"
            print(f"[{args.mode}] Using DPH catalog_id={container_id}, contract name='{name}' for {f}")
        else:
            if not project_id:
                print(f"ERROR: customProperties.projectId not found in {f} "
                      "(required for non-DPH contracts and for PR validation of DPH contracts).",
                      file=sys.stderr)
                sys.exit(1)

            container_id = project_id
            container_type = "project"
            print(f"[{args.mode}] Using project_id={container_id}, contract name='{name}' for {f}")

        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()

        if container_type == "catalog":
            existing_draft_contract_id = ""
            resolved_terms_id = ""
            # data_product_id sent with the contract: the asset id part of draftId
            # ("<asset_id>@<catalog_id>") for type "contract", otherwise "".
            draft_asset_id = draft_id.split("@", 1)[0] if is_contract_type else ""
            if is_contract_type:
                # type "contract": the draft is the source of truth. No name/type search -
                # replace the contract already attached to the draft, otherwise create
                # a new one and attach it to the draft's contract terms.
                try:
                    existing_draft_contract_id, resolved_terms_id = get_draft_contract_info(
                        dph=dph_client,
                        draft_id=draft_id,
                        data_product_id=data_product_id,
                    )
                except Exception as exc:
                    print(f"ERROR: Failed to inspect draft {draft_id}: {exc}", file=sys.stderr)
                    sys.exit(1)
                target_replace_id = existing_draft_contract_id or None
            else:
                # type "contract_template": match an existing catalog contract by name and type
                collection = provider.list_catalog_data_contracts(container_id, limit=200)

                existing = next(
                    (
                        dc for dc in collection.data_contracts
                        if dc.name == name
                        and (not contract_type or _get_catalog_dc_type(dc) in ("", contract_type))
                    ),
                    None,
                )
                target_replace_id = existing.id if existing else None

            # Catalog contracts are sent as contract_json (parsed from the JSON/YAML file).
            # type is "contract" or "contract_template" (from customProperties.type)
            # data_product_id is the asset id from draftId for type "contract", else "".
            body = DataContractPrototypeJson(
                name=name,
                contract_json=parse_contract_content(content),
                type=contract_type,
                data_product_id=draft_asset_id,
            )
            print(f"  data_product_id={draft_asset_id!r}")
            if target_replace_id:
                # PUT / replace operation on existing contract in catalog
                print(f"  Existing contract found (id={target_replace_id}). Performing PUT/replace operation in catalog ...")
                contract = provider.replace_catalog_data_contract(
                    container_id, target_replace_id, body, validate=True
                )
                result_lines.append(f"### 🔄 `{f}` — updated in DPH catalog (id: `{contract.id}`)")
                print(f"Updated DPH contract {f}  →  name={name}  id={contract.id}")
            else:
                # POST / create new contract in catalog
                contract = provider.create_catalog_data_contract(
                    container_id, body, validate=True
                )
                # Link newly created contract to data product draft
                if is_contract_type:
                    try:
                        link_contract_to_data_product_draft(
                            dph=dph_client,
                            draft_id=draft_id,
                            contract_terms_id=resolved_terms_id,
                            data_product_id=data_product_id,
                            contract_id=contract.id,
                        )
                    except Exception as exc:
                        # The catalog contract was created but linking to the draft
                        # failed. Roll back by deleting the orphaned contract.
                        print(
                            f"ERROR: Failed to link contract {contract.id} to draft {draft_id}: {exc}",
                            file=sys.stderr,
                        )
                        print(
                            f"  Rolling back: deleting orphaned catalog contract {contract.id} ...",
                            file=sys.stderr,
                        )
                        try:
                            provider.delete_catalog_data_contracts(
                                container_id,
                                data_contract_ids=contract.id,
                            )
                            print(f"  Rollback succeeded: contract {contract.id} deleted.")
                            result_lines.append(
                                f"### ❌ `{f}` — catalog contract created but link to draft failed "
                                f"(rolled back, contract `{contract.id}` deleted)."
                            )
                        except Exception as del_exc:
                            # Rollback itself failed — log the orphan ID so it can be
                            # cleaned up manually.
                            orphan_pair = f"catalog:{container_id}:{contract.id}"
                            print(
                                f"  ⚠️  Rollback failed: {del_exc}\n"
                                f"  ORPHANED CATALOG CONTRACT — delete manually: {orphan_pair}",
                                file=sys.stderr,
                            )
                            result_lines.append(
                                f"### ❌ `{f}` — catalog contract created but NOT linked to draft, "
                                f"and rollback failed (orphan id: `{contract.id}`, catalog: `{container_id}`). "
                                f"**Delete manually before re-running.**"
                            )
                        # Flush partial summary to GITHUB_OUTPUT before exiting so
                        # the error is visible in the PR comment even on failure.
                        github_output = os.environ.get("GITHUB_OUTPUT", "")
                        if github_output:
                            with open(github_output, "a") as _out:
                                _out.write("body<<EOF\n")
                                _out.write(
                                    "## 📦 Data Contract Create\n\n"
                                    + "\n\n".join(result_lines)
                                    + "\n\nEOF\n"
                                )
                        sys.exit(1)

                result_lines.append(f"### ✅ `{f}` — created in DPH catalog (id: `{contract.id}`)")
                print(f"Created DPH contract {f}  →  name={name}  id={contract.id}")
        else:
            collection = provider.list_project_data_contracts(container_id, limit=200)
            existing   = next((dc for dc in collection.data_contracts if dc.name == name), None)
            body       = DataContractPrototypeYaml(name=name, contract_yaml=content)
            if existing:
                contract = provider.replace_project_data_contract(
                    container_id, existing.id, body, validate=True
                )
                if args.mode == "pr":
                    result_lines.append(f"### 🔄 `{f}` — ephemeral contract updated (name: `{name}`, id: `{contract.id}`)")
                else:
                    result_lines.append(f"### 🔄 `{f}` — updated (id: `{contract.id}`)")
                print(f"Updated  {f}  →  name={name}  id={contract.id}")
            else:
                contract = provider.create_project_data_contract(
                    container_id, body, validate=True
                )
                if args.mode == "pr":
                    result_lines.append(f"### ✅ `{f}` — ephemeral contract created (name: `{name}`, id: `{contract.id}`)")
                else:
                    result_lines.append(f"### ✅ `{f}` — created (id: `{contract.id}`)")
                print(f"Created  {f}  →  name={name}  id={contract.id}")

        # Catalog pairs are prefixed so downstream steps use the catalog APIs
        prefix = "catalog:" if container_type == "catalog" else ""
        contract_pairs.append(f"{prefix}{container_id}:{contract.id}")

    if args.mode == "pr":
        md_title = "## 📦 Data Contract Create (Ephemeral — PR validation)"
    else:
        md_title = "## 📦 Data Contract Create"

    md = md_title + "\n\n" + "\n\n".join(result_lines) + "\n"
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as out:
            out.write("body<<EOF\n")
            out.write(md + "\n")
            out.write("EOF\n")
            out.write("contract_ids=" + " ".join(contract_pairs) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
