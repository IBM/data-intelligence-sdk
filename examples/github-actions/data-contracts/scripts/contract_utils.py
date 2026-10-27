#!/usr/bin/env python3
"""
Shared utilities for data contract scripts.
"""

import json
import os
import re

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

# IAM endpoint used for ibm_cloud when IAM_TOKEN_URL is not set (IBM Cloud test).
DEFAULT_IBM_CLOUD_IAM_URL = "https://iam.test.cloud.ibm.com/identity/token"


def get_bearer_token() -> str:
    """Return a "Bearer <token>" string for the configured platform environment.

    Authentication is delegated to wxdi.common.auth (AuthConfig / AuthProvider),
    selected by environment variables:

        PLATFORM_ENV         ibm_cloud (default) | aws_cloud | gov_cloud | on_prem
        PLATFORM_URL         Platform base URL; for on_prem it is also the auth host
        PLATFORM_API_KEY     API key (cloud environments; optional for on_prem)
        PLATFORM_USERNAME    Required for on_prem
        PLATFORM_PASSWORD    on_prem, when no API key is given
        PLATFORM_ACCOUNT_ID  Required for aws_cloud
        IAM_TOKEN_URL        Optional token endpoint override for cloud environments.
                             Defaults to the IBM Cloud test endpoint for ibm_cloud
                             and to the SDK default for the other cloud types.

    Raises:
        RuntimeError: when the configuration is invalid or the token request fails.
    """
    from wxdi.common.auth import AuthConfig, AuthProvider, EnvironmentType

    env_name = (os.environ.get("PLATFORM_ENV") or "ibm_cloud").strip().lower()
    try:
        env_type = EnvironmentType(env_name)
    except ValueError:
        valid = ", ".join(e.value for e in EnvironmentType)
        raise RuntimeError(f"Invalid PLATFORM_ENV '{env_name}'. Expected one of: {valid}")

    params = {
        "environment_type": env_type,
        "api_key": os.environ.get("PLATFORM_API_KEY") or None,
    }
    if env_type == EnvironmentType.ON_PREM:
        params["url"] = os.environ.get("PLATFORM_URL", "").rstrip("/") or None
        params["username"] = os.environ.get("PLATFORM_USERNAME") or None
        params["password"] = os.environ.get("PLATFORM_PASSWORD") or None
    else:
        iam_url = os.environ.get("IAM_TOKEN_URL") or None
        if iam_url is None and env_type == EnvironmentType.IBM_CLOUD:
            iam_url = DEFAULT_IBM_CLOUD_IAM_URL
        params["url"] = iam_url
        if env_type == EnvironmentType.AWS_CLOUD:
            params["account_id"] = os.environ.get("PLATFORM_ACCOUNT_ID") or None

    try:
        token = AuthProvider(AuthConfig(**params)).get_token()
    except Exception as exc:
        raise RuntimeError(f"Failed to obtain {env_type.value} token: {exc}") from exc
    return f"Bearer {token}"


def extract_custom_properties(contract_file: str) -> list:
    """Parse contract file and return its top-level customProperties list."""
    try:
        with open(contract_file, "r", encoding="utf-8") as fh:
            content = fh.read()

        ext = os.path.splitext(contract_file)[1].lower()
        if ext == ".json":
            doc = json.loads(content)
        elif ext in (".yaml", ".yml"):
            if not _YAML_AVAILABLE:
                return []
            doc = yaml.safe_load(content)
        else:
            try:
                doc = json.loads(content)
            except json.JSONDecodeError:
                if _YAML_AVAILABLE:
                    doc = yaml.safe_load(content)
                else:
                    return []

        custom_props = doc.get("customProperties") if isinstance(doc, dict) else None
        if isinstance(custom_props, list):
            return custom_props
    except Exception:
        pass
    return []


def extract_project_id(contract_file: str, fallback: str) -> str:
    """Return the projectId from a contract file's top-level customProperties.

    Looks for:
        customProperties:
          - property: projectId
            value: <uuid>

    Works for both JSON (.json) and YAML (.yaml / .yml) contract files.
    Falls back to `fallback` when:
      - the file cannot be parsed
      - customProperties is absent
      - no entry with property == "projectId" exists

    Args:
        contract_file: Path to the contract file.
        fallback: Value to return when projectId is not found in the file.

    Returns:
        The projectId string from the file, or `fallback`.
    """
    custom_props = extract_custom_properties(contract_file)
    for prop in custom_props:
        if isinstance(prop, dict) and prop.get("property") == "projectId":
            value = prop.get("value")
            if value and isinstance(value, str):
                return value.strip()
    return fallback


# UUID v4 pattern: 8-4-4-4-12 lowercase hex digits separated by hyphens.
_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
)


def is_valid_draft_id(draft_id: str) -> bool:
    """True when draft_id is "<asset_uuid>@<catalog_uuid>" with both parts valid UUIDs."""
    parts = draft_id.split("@")
    if len(parts) != 2:
        return False
    return all(_UUID_RE.match(p.strip().lower()) for p in parts)


def get_draft_contract_info(dph, draft_id: str, data_product_id: str = "-") -> tuple:
    """Fetch draft details and return (existing_contract_id, resolved_contract_terms_id).

    Raises RuntimeError when the draft has no contract_terms or the terms have no id.
    """
    print(f"  Fetching draft {draft_id} ...")
    resp = dph.get_data_product_draft(
        data_product_id=data_product_id,
        draft_id=draft_id,
    )
    res = resp.get_result() if hasattr(resp, "get_result") else resp.result
    contract_terms_list = res.get("contract_terms") or []
    if not contract_terms_list:
        raise RuntimeError(f"No contract_terms found in draft {draft_id}")

    target_terms = contract_terms_list[0]
    resolved_terms_id = target_terms.get("id")
    if not resolved_terms_id:
        raise RuntimeError(f"Missing id in contract_terms for draft {draft_id}")

    existing_contract_id = target_terms.get("data_contract_id") or ""

    return existing_contract_id, resolved_terms_id


def _parse_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes")
    return False


def extract_target_info(contract_file: str) -> dict:
    """Return target container and DPH metadata from customProperties."""
    custom_props = extract_custom_properties(contract_file)
    props_map = {
        prop.get("property"): prop.get("value")
        for prop in custom_props
        if isinstance(prop, dict) and prop.get("property")
    }

    def _get_str(name: str, default: str = "") -> str:
        v = props_map.get(name)
        return v.strip() if isinstance(v, str) and v.strip() else default

    return {
        "is_dph": _parse_bool(props_map.get("isDPH")),
        "type": _get_str("type", "contract_template"),
        "draft_id": _get_str("draftId"),
        "catalog_id": _get_str("catalogId"),
        "project_id": _get_str("projectId"),
    }
