#!/usr/bin/env python3
"""
Trigger and poll data contract test runs in a CPD/watsonx project.

Usage:
    python test_contract.py <entry1> [<entry2> ...]

Each entry must be a <project_id>:<contract_id> pair emitted by create_contract.py.
Project ID is embedded in each entry from customProperties.projectId in the contract file.

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
    0 - all contract tests completed (pass/fail reported via GITHUB_OUTPUT)
    1 - unexpected error

Writes GITHUB_OUTPUT:
    body    - Markdown summary for PR comment
    overall - 0 (all passed) or 1 (one or more failed)
"""

import importlib.util
import json
import os
import re
import sys
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from wxdi.data_contracts import DataContractsProvider
from wxdi.data_contracts.models import DataContractTestRequest
from wxdi.dq_validator.provider.config import ProviderConfig

# Load contract_utils from the same directory as this script
_utils_path = os.path.join(os.path.dirname(__file__), "contract_utils.py")
_spec = importlib.util.spec_from_file_location("contract_utils", _utils_path)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
get_bearer_token = _mod.get_bearer_token

# Directory where per-contract result JSON files are written (uploaded as an artifact).
RESULTS_DIR = os.environ.get("RESULTS_DIR", "test-results")

MAX_POLLS        = 30
POLL_INTERVAL    = 10
TRIGGER_RETRIES  = 3      # retry the POST trigger on transient 5xx errors
TRIGGER_BACKOFF  = 15     # seconds between retries (doubles each attempt)


def main() -> int:
    entries = sys.argv[1:]
    if not entries:
        print("No contract IDs provided — nothing to test.")
        return 0

    cpd_url = os.environ.get("PLATFORM_URL", "").rstrip("/")

    bearer   = get_bearer_token()
    config   = ProviderConfig(url=cpd_url, auth_token=bearer)
    provider = DataContractsProvider(config)

    result_lines = []
    overall      = 0

    for entry in entries:
        # Entry must be "project_id:contract_id" as emitted by create_contract.py
        if ":" not in entry:
            print(f"ERROR: entry '{entry}' is not in project_id:contract_id format.",
                  file=sys.stderr)
            overall = 1
            result_lines.append(f"### ❌ `{entry}` — invalid format (expected project_id:contract_id)")
            result_lines.append("")
            continue

        project_id, cid = entry.split(":", 1)

        print(f"Triggering test for contract id={cid} (project={project_id}) ...")
        test_resp = None
        last_exc  = None
        for attempt in range(1, TRIGGER_RETRIES + 1):
            try:
                test_resp = provider.test_project_data_contract(
                    project_id, cid,
                    DataContractTestRequest(retain_dq_objects=False),
                )
                break  # success — stop retrying
            except ValueError as exc:
                last_exc = exc
                # Only retry on transient server errors (5xx in the message)
                is_transient = any(
                    code in str(exc) for code in ("500", "502", "503", "504")
                )
                if is_transient and attempt < TRIGGER_RETRIES:
                    wait = TRIGGER_BACKOFF * (2 ** (attempt - 1))
                    print(f"  attempt {attempt}/{TRIGGER_RETRIES} failed (transient): {exc}",
                          file=sys.stderr)
                    print(f"  retrying in {wait}s ...", file=sys.stderr)
                    time.sleep(wait)
                else:
                    break  # non-transient error or out of retries

        if test_resp is None:
            print(f"ERROR: test trigger failed for {cid}: {last_exc}", file=sys.stderr)
            overall = 1
            result_lines.append(f"### ❌ `{cid}` — test trigger failed")
            result_lines.append(f"> Error: `{last_exc}`")
            result_lines.append("")
            continue

        # The trigger response returns the test run id as `id`.
        run_id = test_resp.id
        if not run_id:
            raw = test_resp.model_dump()
            print(f"WARNING: could not resolve run_id for contract {cid}. "
                  f"Raw response: {raw}", file=sys.stderr)
            overall = 1
            result_lines.append(f"### ❌ `{cid}` — test trigger returned no run ID")
            result_lines.append(f"> Raw response (all fields): `{raw}`")
            result_lines.append("")
            continue

        print(f"  run_id={run_id} — polling ...")
        result = None
        for _ in range(MAX_POLLS):
            result = provider.get_project_data_contract_test_result(
                project_id, cid, run_id, include_all_details=True
            )
            if (result.status or "").lower() in ("completed", "failed"):
                break
            time.sleep(POLL_INTERVAL)

        status = result.status if result and result.status else "unknown"
        start  = result.start  if result else "-"
        end    = result.end    if result else "-"

        if status.lower() == "completed":
            result_lines.append(f"### ✅ `{cid}` — test completed")
        else:
            overall = 1
            result_lines.append(f"### ❌ `{cid}` — test **{status}**")

        result_lines.append(
            f"> Run ID: `{run_id}` | Started: {start} | Ended: {end}"
        )

        summary = result.summary if result else None
        if summary:
            sv = summary.schema_validation
            dq = summary.data_quality
            parts = [f"Overall: `{summary.status or '-'}`"]
            if sv:
                parts.append(
                    f"Schema: `{sv.status or '-'}` "
                    f"({sv.passed_assets}/{sv.total_assets} assets, "
                    f"{sv.passed_columns}/{sv.total_columns} columns)"
                )
            if dq:
                parts.append(
                    f"Data quality: `{dq.status or '-'}` "
                    f"({dq.passed_checks}/{dq.total_checks} checks passed, "
                    f"{dq.failed_checks} failed, {dq.error_checks} errors)"
                )
            result_lines.append("> " + " | ".join(parts))

        # Data quality checks are attached to either an asset or one of its columns.
        # Each entry is (dataset, field, check).
        dq_checks = []
        for asset in (result.data_assets if result else []):
            asset_name = asset.name or asset.physical_name or "-"
            for chk in asset.data_quality_checks:
                dq_checks.append((asset_name, "-", chk))
            for col in asset.columns:
                for chk in col.data_quality_checks:
                    dq_checks.append((asset_name, col.name or col.physical_name or "-", chk))

        if dq_checks:
            def _check_status(chk):
                return (chk.results.status if chk.results else None) or "-"

            any_error = any(_check_status(c).lower() == "error" for _, _, c in dq_checks)
            if any_error:
                rows = ["| Rule | Dataset | Field | Status | Tested | Passed | Failed | Message |",
                        "|---|---|---|---|---|---|---|---|"]
            else:
                rows = ["| Rule | Dataset | Field | Status | Tested | Passed | Failed |",
                        "|---|---|---|---|---|---|---|"]

            for dataset, field, chk in dq_checks:
                res    = chk.results
                rule   = chk.name or (chk.data_quality_rule.id if chk.data_quality_rule else None) or "-"
                tested = res.tested_record_count if res and res.tested_record_count is not None else "-"
                passed = res.passed_record_count if res and res.passed_record_count is not None else "-"
                failed = res.failed_record_count if res and res.failed_record_count is not None else "-"
                row = f"| {rule} | {dataset} | {field} | `{_check_status(chk)}` | {tested} | {passed} | {failed} |"
                if any_error:
                    logs = (chk.model_extra or {}).get("logs") or []
                    msg  = logs[0].get("message", "") if logs and isinstance(logs[0], dict) else ""
                    row  = row[:-1] + f" {msg} |"
                rows.append(row)

            result_lines.append("\n**Check Results**\n\n" + "\n".join(rows))

        # Schema validation issues: anything not reported as passed.
        sv_rows = []
        for asset in (result.data_assets if result else []):
            asset_name = asset.name or asset.physical_name or "-"
            asset_sv = asset.schema_validation
            if asset_sv:
                if asset_sv.exists is False:
                    sv_rows.append(f"| `{asset_name}` | - | Asset not found | - | - |")
                pt = asset_sv.physical_type
                if pt and (pt.status or "").lower() == "failed":
                    sv_rows.append(f"| `{asset_name}` | - | Physical type mismatch | `{pt.expected}` | `{pt.actual}` |")
                for c in asset_sv.missing_columns:
                    sv_rows.append(f"| `{asset_name}` | `{c}` | Missing column | - | - |")
                for c in asset_sv.unexpected_columns:
                    sv_rows.append(f"| `{asset_name}` | `{c}` | Unexpected column | - | - |")

            for col in asset.columns:
                col_sv = col.schema_validation
                if not col_sv:
                    continue
                col_name = col.name or col.physical_name or "-"
                t = col_sv.type
                if t and (t.status or "").lower() == "failed":
                    sv_rows.append(
                        f"| `{asset_name}` | `{col_name}` | Type mismatch | "
                        f"`{t.expected_logical_type or t.expected_physical_type}` | "
                        f"`{t.actual_logical_type or t.actual_physical_type}` |"
                    )
                r = col_sv.required
                if r and (r.status or "").lower() == "failed":
                    sv_rows.append(
                        f"| `{asset_name}` | `{col_name}` | Required column contains nulls | "
                        f"`not null` | `{r.null_count} nulls` |"
                    )
                pk = col_sv.primary_key
                if pk and (pk.status or "").lower() == "failed":
                    sv_rows.append(
                        f"| `{asset_name}` | `{col_name}` | Primary key mismatch | "
                        f"`{pk.expected_primary_key}` | `{pk.actual_primary_key}` |"
                    )
                u = col_sv.unique
                if u and (u.status or "").lower() == "failed":
                    sv_rows.append(
                        f"| `{asset_name}` | `{col_name}` | Uniqueness violated | "
                        f"`unique` | `{u.duplicate_count} duplicates` |"
                    )

        if sv_rows:
            header = ["| Table | Column | Issue | Expected | Actual |", "|---|---|---|---|---|"]
            result_lines.append("\n**Schema Validation Issues**\n\n" + "\n".join(header + sv_rows))

        # Successful run: save the full result as a JSON file; the action uploads
        # RESULTS_DIR as a workflow artifact and links it from the PR comment.
        if result and status.lower() == "completed":
            os.makedirs(RESULTS_DIR, exist_ok=True)
            # Name the file after the canonical contract name (ephemeral contract is
            # "<name>_PR_<n>") so the merge job can match it to the real contract.
            contract_name = cid
            try:
                ephemeral = provider.get_project_data_contract(project_id, cid).name or cid
                contract_name = re.sub(r"_PR_\d+$", "", ephemeral)
            except ValueError as exc:
                print(f"  WARNING: could not resolve name for {cid}: {exc}", file=sys.stderr)
            out_path = os.path.join(RESULTS_DIR, f"test-result_{contract_name}.json")
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(result.model_dump(exclude_none=True), fh, indent=2, default=str)
            print(f"  saved test result JSON to {out_path}")

        result_lines.append("")

    md = "## 🧪 Data Contract Test Run\n\n" + "\n".join(result_lines) + "\n"
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as out:
            out.write("body<<EOF\n")
            out.write(md + "\n")
            out.write("EOF\n")
            out.write(f"overall={overall}\n")

    # Always exit 0 here — the composite action's "Fail if test failed" step
    # reads `overall` from GITHUB_OUTPUT and calls `exit 1` if needed.
    # Returning non-zero here would skip the "Post PR comment (success)" step.
    return 0


if __name__ == "__main__":
    sys.exit(main())
