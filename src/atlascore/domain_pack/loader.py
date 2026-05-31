"""Domain-pack loader using PyYAML.

This loader performs strict schema and ontology validation and refuses to load
packs that contain data artifacts. Domain packs are configuration and ontology, not data.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Set

import yaml

from ..errors import SchemaViolationError, MissingDataError, DomainPackInvalidError


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load and validate YAML file exists and is not empty."""
    if not path.exists():
        raise MissingDataError(f"Domain pack file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise SchemaViolationError(f"Domain pack file must be mapping: {path}")
    if not data:
        raise DomainPackInvalidError(f"Domain pack file is empty: {path}")
    return data


def load_entity_types(pack_dir: Path) -> Set[str]:
    """Load entity_types.yaml and return set of entity type names."""
    data = _load_yaml(pack_dir / "entity_types.yaml")
    if "entity_types" not in data:
        raise DomainPackInvalidError("entity_types.yaml missing 'entity_types' key")
    entity_types = data["entity_types"]
    if not isinstance(entity_types, list):
        raise SchemaViolationError("entity_types must be a list")
    if not entity_types:
        raise DomainPackInvalidError("entity_types list is empty")
    names = set()
    for et in entity_types:
        if not isinstance(et, dict) or "name" not in et:
            raise SchemaViolationError("Each entity_type must have a 'name'")
        names.add(et["name"])
    if len(names) != len(entity_types):
        raise DomainPackInvalidError("Duplicate entity type names detected")
    return names


def load_event_types(pack_dir: Path, entity_types: Set[str]) -> Set[str]:
    """Load event_types.yaml and validate against entity_types."""
    data = _load_yaml(pack_dir / "event_types.yaml")
    if "event_types" not in data:
        raise DomainPackInvalidError("event_types.yaml missing 'event_types' key")
    event_types = data["event_types"]
    if not isinstance(event_types, list):
        raise SchemaViolationError("event_types must be a list")
    if not event_types:
        raise DomainPackInvalidError("event_types list is empty")
    names = set()
    for et in event_types:
        if not isinstance(et, dict) or "name" not in et:
            raise SchemaViolationError("Each event_type must have a 'name'")
        names.add(et["name"])
        participants = et.get("participants", [])
        if isinstance(participants, list):
            for p in participants:
                if p not in entity_types:
                    raise DomainPackInvalidError(
                        f"Unknown entity type '{p}' in event_type '{et['name']}'"
                    )
    if len(names) != len(event_types):
        raise DomainPackInvalidError("Duplicate event type names detected")
    return names


def load_relationship_types(pack_dir: Path, entity_types: Set[str]) -> Set[str]:
    """Load relationship_types.yaml and validate against entity_types."""
    data = _load_yaml(pack_dir / "relationship_types.yaml")
    if "relationship_types" not in data:
        raise DomainPackInvalidError("relationship_types.yaml missing 'relationship_types' key")
    relationship_types = data["relationship_types"]
    if not isinstance(relationship_types, list):
        raise SchemaViolationError("relationship_types must be a list")
    if not relationship_types:
        raise DomainPackInvalidError("relationship_types list is empty")
    names = set()
    for rt in relationship_types:
        if not isinstance(rt, dict) or "name" not in rt:
            raise SchemaViolationError("Each relationship_type must have a 'name'")
        names.add(rt["name"])
        from_entity = rt.get("from_entity")
        to_entity = rt.get("to_entity")
        if from_entity and from_entity not in entity_types:
            raise DomainPackInvalidError(
                f"Unknown entity type '{from_entity}' in relationship_type '{rt['name']}'"
            )
        if to_entity and to_entity not in entity_types:
            raise DomainPackInvalidError(
                f"Unknown entity type '{to_entity}' in relationship_type '{rt['name']}'"
            )
    if len(names) != len(relationship_types):
        raise DomainPackInvalidError("Duplicate relationship type names detected")
    return names


def load_signal_definitions(pack_dir: Path) -> Set[str]:
    """Load signal_definitions.yaml and return set of signal names."""
    data = _load_yaml(pack_dir / "signal_definitions.yaml")
    if "signals" not in data:
        raise DomainPackInvalidError("signal_definitions.yaml missing 'signals' key")
    signals = data["signals"]
    if not isinstance(signals, list):
        raise SchemaViolationError("signals must be a list")
    if not signals:
        raise DomainPackInvalidError("signals list is empty")
    names = set()
    for sig in signals:
        if not isinstance(sig, dict) or "name" not in sig:
            raise SchemaViolationError("Each signal must have a 'name'")
        names.add(sig["name"])
    if len(names) != len(signals):
        raise DomainPackInvalidError("Duplicate signal names detected")
    return names


def load_prediction_targets(pack_dir: Path) -> Set[str]:
    """Load prediction_targets.yaml and return set of target names."""
    data = _load_yaml(pack_dir / "prediction_targets.yaml")
    if "prediction_targets" not in data:
        raise DomainPackInvalidError("prediction_targets.yaml missing 'prediction_targets' key")
    targets = data["prediction_targets"]
    if not isinstance(targets, list):
        raise SchemaViolationError("prediction_targets must be a list")
    if not targets:
        raise DomainPackInvalidError("prediction_targets list is empty")
    names = set()
    for target in targets:
        if not isinstance(target, dict) or "name" not in target:
            raise SchemaViolationError("Each prediction_target must have a 'name'")
        names.add(target["name"])
    if len(names) != len(targets):
        raise DomainPackInvalidError("Duplicate prediction target names detected")
    return names


def load_domain_pack(pack_dir: str) -> Dict[str, Any]:
    """Load and validate an entire domain pack with all required files."""
    pack_path = Path(pack_dir)
    if not pack_path.exists():
        raise MissingDataError(f"Domain pack directory not found: {pack_dir}")
    
    # Load ontology first
    ontology_data = _load_yaml(pack_path / "ontology.yaml")
    
    # Load all components with validation
    entity_types = load_entity_types(pack_path)
    event_types = load_event_types(pack_path, entity_types)
    relationship_types = load_relationship_types(pack_path, entity_types)
    signal_defs = load_signal_definitions(pack_path)
    prediction_targets = load_prediction_targets(pack_path)
    
    return {
        "ontology": ontology_data,
        "entity_types": entity_types,
        "event_types": event_types,
        "relationship_types": relationship_types,
        "signals": signal_defs,
        "prediction_targets": prediction_targets,
    }
