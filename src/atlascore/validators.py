"""Validators for AtlasCore contracts.

Validators enforce evidence and provenance requirements and raise typed
errors when rules are violated. They deliberately do not fabricate values.
"""
from __future__ import annotations

from typing import Iterable, Mapping, Any, Set
from uuid import UUID
from pathlib import Path

from .contracts.models import (
    Signal,
    DetectedEvent,
    RelationshipEdge,
    Prediction,
    ValidationResult,
    SourceRecord,
    RawDocument,
)
from . import errors


def _has_provenance(obj) -> bool:
    return bool(getattr(obj, "provenance", None))


def _has_evidence(obj) -> bool:
    ev = getattr(obj, "evidence", None)
    return bool(ev) if isinstance(ev, (list, tuple)) else False


def _is_mock_data(path: str) -> bool:
    """Check if path is outside tests/fixtures."""
    p = Path(path).resolve()
    fixtures = Path("tests/fixtures").resolve()
    try:
        p.relative_to(fixtures)
        return False  # inside fixtures, OK
    except ValueError:
        return True  # outside fixtures, mock data forbidden


def require_provenance(obj, *, name: str = "object"):
    if not _has_provenance(obj):
        raise errors.MissingEvidenceError(f"{name} missing provenance/evidence")
    return True


def validate_raw_document(doc: RawDocument) -> ValidationResult:
    """Validate RawDocument has content hash."""
    if not doc.content_hash:
        raise errors.InvalidRawDocumentError("RawDocument missing content_hash")
    if not doc.body_ref:
        raise errors.InvalidRawDocumentError("RawDocument missing body_ref")
    if not doc.format:
        raise errors.InvalidRawDocumentError("RawDocument missing format")
    vr = ValidationResult(
        rules_run=["content_hash_present", "body_ref_present", "format_present"],
        passed=True,
    )
    return vr


def validate_score(score: float) -> None:
    """Enforce score is in [0, 1]."""
    if not (0 <= score <= 1):
        raise errors.InvalidScoreError(f"Score must be in [0, 1], got {score}")


def validate_confidence(confidence: float) -> None:
    """Enforce confidence is in [0, 1]."""
    if not (0 <= confidence <= 1):
        raise errors.InvalidConfidenceError(f"Confidence must be in [0, 1], got {confidence}")


def validate_weight(weight: float) -> None:
    """Enforce relationship weight is in [-1, 1]."""
    if not (-1 <= weight <= 1):
        raise errors.OntologyValidationFailedError(f"Weight must be in [-1, 1], got {weight}")


def validate_signal(
    signal: Signal,
    entity_types: Set[str] | None = None,
    event_types: Set[str] | None = None,
) -> ValidationResult:
    """Validate Signal has evidence and provenance."""
    if not signal.evidence:
        raise errors.SignalValidationFailedError("Signal missing evidence refs")
    if not _has_provenance(signal):
        raise errors.ProvenanceChainBrokenError("Signal missing provenance links")
    if signal.score < 0 or signal.score > 1:
        raise errors.InvalidScoreError(f"Signal score out of range: {signal.score}")
    if signal.confidence < 0 or signal.confidence > 1:
        raise errors.InvalidConfidenceError(f"Signal confidence out of range: {signal.confidence}")
    vr = ValidationResult(
        rules_run=[
            "evidence_present",
            "provenance_present",
            "score_valid",
            "confidence_valid",
        ],
        passed=True,
    )
    return vr


def validate_detected_event(
    event: DetectedEvent, entity_types: Set[str] | None = None, event_types: Set[str] | None = None
) -> ValidationResult:
    """Validate DetectedEvent has evidence, provenance, and valid types."""
    if not event.evidence_refs:
        raise errors.InsufficientEvidenceError("DetectedEvent missing evidence_refs")
    if not _has_provenance(event):
        raise errors.ProvenanceChainBrokenError("DetectedEvent missing provenance")
    if event_types and event.event_type not in event_types:
        raise errors.UnknownEventTypeError(f"Unknown event_type: {event.event_type}")
    vr = ValidationResult(
        rules_run=["evidence_refs_present", "provenance_present", "event_type_valid"],
        passed=True,
    )
    return vr


def validate_relationship_edge(
    edge: RelationshipEdge,
    entity_types: Set[str] | None = None,
    relationship_types: Set[str] | None = None,
) -> ValidationResult:
    """Validate RelationshipEdge has evidence, provenance, valid types, and weight."""
    if not edge.evidence_refs:
        raise errors.InsufficientEvidenceError("RelationshipEdge missing evidence_refs")
    if not _has_provenance(edge):
        raise errors.ProvenanceChainBrokenError("RelationshipEdge missing provenance")
    if relationship_types and edge.type not in relationship_types:
        raise errors.OntologyValidationFailedError(f"Unknown relationship_type: {edge.type}")
    validate_weight(edge.weight)
    vr = ValidationResult(
        rules_run=[
            "evidence_refs_present",
            "provenance_present",
            "relationship_type_valid",
            "weight_valid",
        ],
        passed=True,
    )
    return vr


def validate_prediction(
    pred: Prediction, signal_lookup: Mapping[UUID, Signal]
) -> ValidationResult:
    """Validate Prediction references validated signals and has valid scores."""
    if not pred.input_signal_refs:
        raise errors.PredictionValidationFailedError("Prediction has no input_signal_refs")
    for sref in pred.input_signal_refs:
        sig = signal_lookup.get(sref)
        if sig is None:
            raise errors.MissingDataError(f"Signal {sref} not found for prediction")
        if not sig.validated or not sig.validated.passed:
            raise errors.PredictionValidationFailedError(
                f"Signal {sref} is not validated for prediction"
            )
    if pred.score is not None:
        validate_score(pred.score)
    if pred.confidence is not None:
        validate_confidence(pred.confidence)
    vr = ValidationResult(
        rules_run=["signals_validated", "score_valid", "confidence_valid"],
        passed=True,
    )
    return vr


def reject_mock_data(path: str, location_hint: str = "artifact") -> None:
    """Reject mock data outside tests/fixtures."""
    if _is_mock_data(path):
        raise errors.MockDataForbiddenError(
            f"Mock {location_hint} outside tests/fixtures forbidden: {path}"
        )
