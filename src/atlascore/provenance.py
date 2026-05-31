"""Provenance chain helpers.

Helpers to create and verify `ProvenanceLink` objects without mutating raw
artifacts. These functions return new provenance lists or small value objects
to be attached to derived artifacts.
"""
from __future__ import annotations

from typing import Dict, Any, List
from uuid import UUID

from .contracts.models import ProvenanceLink


def make_provenance_link(artifact_id: UUID, action: str, actor: str, metadata: Dict[str, Any] | None = None) -> ProvenanceLink:
    return ProvenanceLink(artifact_id=artifact_id, action=action, actor=actor, metadata=metadata or {})


def append_provenance(existing: List[ProvenanceLink], link: ProvenanceLink) -> List[ProvenanceLink]:
    # Do not mutate inputs; return new list
    return [*existing, link]


def verify_provenance_chain(provenance: List[ProvenanceLink]) -> bool:
    return bool(provenance)
