#!/usr/bin/env python3
"""
Create data contracts in a CPD/watsonx project.

Two modes:

  --mode pr   (PR validation)
      Creates an ephemeral contract named "<contract_name>_PR_<pr_number>".
      The contract is used for CI testing only and deleted afterwards.
      Emits contract_ids as "<project_id>:<contract_id>" pairs.

  --mode merge  (post-merge upsert)
      Creates or replaces the real contract using the canonical name from
      the contract file. This is the production upsert path.

Usage:
    python create_contract.py --mode pr   --pr-number <N> <file1> [<file2> ...]
    python create_contract.py --mode merge               <file1> [<file2> ...]

Environment variables (required):
    PLATFORM_URL     - Base URL of the instance (e.g. https://api.dai.dev.cloud.ibm.com)
    PLATFORM_API_KEY - IBM Cloud IAM API key; a fresh bearer token is obtained at runtime

Project ID is read exclusively from customProperties.projectId in each contract file.

Exit codes:
    0 - all contracts created/updated successfully
    1 - one or more contracts failed or an error occurred

Writes GITHUB_OUTPUT:
    body         - Markdown summary for PR comment
    contract_ids - Space-separated list of <project_id>:<contract_id> pairs
"""

import os
import sys
import argparse
import importlib.util
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wxdi.data_contracts import DataContractsProvider
from wxdi.data_contracts.models import DataContractPrototypeYaml
from wxdi.dq_validator.provider.config import ProviderConfig

# Load contract_utils from the same directory as this script
_utils_path = os.path.join(os.path.dirname(__file__), "contract_utils.py")
_spec = importlib.util.spec_from_file_location("contract_utils", _utils_path)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
extract_project_id = _mod.extract_project_id

IAM_TOKEN_URL = (
    os.environ.get("IAM_TOKEN_URL")
    or "https://iam.test.cloud.ibm.com/identity/token"
)


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
    api_key = os.environ.get("PLATFORM_API_KEY", "")

    bearer   = get_bearer_token(api_key)
    config   = ProviderConfig(url=cpd_url, auth_token=bearer)
    provider = DataContractsProvider(config)

    result_lines   = []
    contract_pairs = []

    for f in args.files:
        canonical_name = os.path.splitext(os.path.basename(f))[0]

        # In PR mode use an ephemeral name so the real contract is untouched
        if args.mode == "pr":
            name = f"{canonical_name}_PR_{args.pr_number}"
        else:
            name = canonical_name

        project_id = extract_project_id(f, "")
        if not project_id:
            print(f"ERROR: customProperties.projectId not found in {f}.",
                  file=sys.stderr)
            sys.exit(1)

        print(f"[{args.mode}] Using project_id={project_id}, contract name='{name}' for {f}")

        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()

        collection = provider.list_project_data_contracts(project_id, limit=200)
        existing   = next((dc for dc in collection.data_contracts if dc.name == name), None)

        body = DataContractPrototypeYaml(name=name, contract_yaml=content)
        if existing:
            contract = provider.replace_project_data_contract(
                project_id, existing.id, body, validate=True
            )
            if args.mode == "pr":
                result_lines.append(f"### 🔄 `{f}` — ephemeral contract updated (name: `{name}`, id: `{contract.id}`)")
            else:
                result_lines.append(f"### 🔄 `{f}` — updated (id: `{contract.id}`)")
            print(f"Updated  {f}  →  name={name}  id={contract.id}")
        else:
            contract = provider.create_project_data_contract(
                project_id, body, validate=True
            )
            if args.mode == "pr":
                result_lines.append(f"### ✅ `{f}` — ephemeral contract created (name: `{name}`, id: `{contract.id}`)")
            else:
                result_lines.append(f"### ✅ `{f}` — created (id: `{contract.id}`)")
            print(f"Created  {f}  →  name={name}  id={contract.id}")

        contract_pairs.append(f"{project_id}:{contract.id}")

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
