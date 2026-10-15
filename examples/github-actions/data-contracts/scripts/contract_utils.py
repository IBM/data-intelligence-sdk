#!/usr/bin/env python3
"""
Shared utilities for data contract scripts.
"""

import json
import os

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


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
    try:
        with open(contract_file, "r", encoding="utf-8") as fh:
            content = fh.read()

        ext = os.path.splitext(contract_file)[1].lower()
        if ext == ".json":
            doc = json.loads(content)
        elif ext in (".yaml", ".yml"):
            if not _YAML_AVAILABLE:
                return fallback
            doc = yaml.safe_load(content)
        else:
            # Try JSON first, then YAML
            try:
                doc = json.loads(content)
            except json.JSONDecodeError:
                if _YAML_AVAILABLE:
                    doc = yaml.safe_load(content)
                else:
                    return fallback

        custom_props = doc.get("customProperties") if isinstance(doc, dict) else None
        if not custom_props:
            return fallback

        for prop in custom_props:
            if isinstance(prop, dict) and prop.get("property") == "projectId":
                value = prop.get("value")
                if value and isinstance(value, str):
                    return value.strip()

    except Exception:
        pass

    return fallback
