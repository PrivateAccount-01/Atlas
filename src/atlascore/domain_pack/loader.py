"""Simple domain-pack loader using PyYAML.

This loader performs schema-level checks only and refuses to load packs that
contain data artifacts. Domain packs are configuration and ontology, not data.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from ..errors import SchemaViolationError, MissingDataError


def load_domain_pack(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise MissingDataError(f"Domain pack not found: {path}")
    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    # Basic validation: must have a `name` and `version` and must not include raw data
    if not isinstance(data, dict):
        raise SchemaViolationError("Domain pack must be mapping")
    if "name" not in data or "version" not in data:
        raise SchemaViolationError("Domain pack missing name/version")
    if data.get("contains_data", False):
        raise SchemaViolationError("Domain packs must not contain production data")
    return data
