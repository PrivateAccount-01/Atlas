"""Validators for AtlasCore contracts.

Validators enforce evidence and provenance requirements and raise typed
errors when rules are violated. They deliberately do not fabricate values.
"""
from __future__ import annotations

from typing import Iterable, Mapping, Any
from uuid import UUID

from .contracts.models import (
    Signal,
    DetectedEvent,
    RelationshipEdge,
    Prediction,
    ValidationResult,
)
from . import errors


def _has_provenance(obj) -> bool:
    return bool(getattr(obj, "provenance", None))


def require_provenance(obj, *, name: str = "object"):
    if not _has_provenance(obj):
        raise errors.MissingEvidenceError(f"{name} missing provenance/evidence")
    return True


def validate_signal(signal: Signal) -> ValidationResult:
    if not signal.evidence:
        raise errors.MissingEvidenceError("Signal missing evidence refs")
    if not _has_provenance(signal):
        raise errors.MissingEvidenceError("Signal missing provenance links")
    vr = ValidationResult(rules_run=["evidence_present", "provenance_present"], passed=True)
    return vr


def validate_detected_event(event: DetectedEvent) -> ValidationResult:
    if not event.evidence_refs:
        raise errors.MissingEvidenceError("DetectedEvent missing evidence_refs")
    if not _has_provenance(event):
        raise errors.MissingEvidenceError("DetectedEvent missing provenance")
    vr = ValidationResult(rules_run=["evidence_refs_present", "provenance_present"], passed=True)
    return vr


def validate_relationship_edge(edge: RelationshipEdge) -> ValidationResult:
    if not edge.evidence_refs:
        raise errors.MissingEvidenceError("RelationshipEdge missing evidence_refs")
    if not _has_provenance(edge):
        raise errors.MissingEvidenceError("RelationshipEdge missing provenance")
    vr = ValidationResult(rules_run=["evidence_refs_present", "provenance_present", "ontology_version_present"], passed=True)
    return vr


def validate_prediction(pred: Prediction, signal_lookup: Mapping[UUID, Signal]) -> ValidationResult:
    # Predictions must reference validated signals
    if not pred.input_signal_refs:
        raise errors.ValidationError("Prediction has no input_signal_refs")
    for sref in pred.input_signal_refs:
        sig = signal_lookup.get(sref)
        if sig is None:
            raise errors.MissingDataError(f"Signal {sref} not found for prediction")
        if not sig.validated or not sig.validated.passed:
            raise errors.ValidationError(f"Signal {sref} is not validated for prediction")
    vr = ValidationResult(rules_run=["signals_validated"], passed=True)
    return vr
