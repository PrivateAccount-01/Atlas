"""Typed error classes for AtlasCore foundation stage.

All exceptions carry structured payloads suitable for programmatic handling and
for returning typed error responses when inputs are missing or invalid.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AtlasCoreError(Exception):
    code = "atlascore.error"

    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None):
        self.id = uuid4()
        self.ts = _now_utc()
        self.message = message
        self.details = details or {}
        super().__init__(f"{self.code}: {message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "ts": self.ts.isoformat(),
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(AtlasCoreError):
    code = "atlascore.validation_error"


class MissingEvidenceError(ValidationError):
    code = "atlascore.missing_evidence"


class ImmutableRawDataError(AtlasCoreError):
    code = "atlascore.immutable_raw_data"


class SchemaViolationError(ValidationError):
    code = "atlascore.schema_violation"


class OutOfScopeError(AtlasCoreError):
    code = "atlascore.out_of_scope"


class MissingDataError(AtlasCoreError):
    code = "atlascore.missing_data"


class DataSourceUnavailableError(AtlasCoreError):
    code = "atlascore.data_source_unavailable"


class RateLimitExceededError(AtlasCoreError):
    code = "atlascore.rate_limit_exceeded"


class InvalidRawDocumentError(ValidationError):
    code = "atlascore.invalid_raw_document"


class DuplicateDocumentError(ValidationError):
    code = "atlascore.duplicate_document"


class CleaningFailedError(ValidationError):
    code = "atlascore.cleaning_failed"


class EntityResolutionFailedError(ValidationError):
    code = "atlascore.entity_resolution_failed"


class UnknownEntityTypeError(ValidationError):
    code = "atlascore.unknown_entity_type"


class UnknownEventTypeError(ValidationError):
    code = "atlascore.unknown_event_type"


class OntologyValidationFailedError(ValidationError):
    code = "atlascore.ontology_validation_failed"


class InsufficientEvidenceError(ValidationError):
    code = "atlascore.insufficient_evidence"


class GraphEdgeRejectedError(ValidationError):
    code = "atlascore.graph_edge_rejected"


class SignalValidationFailedError(ValidationError):
    code = "atlascore.signal_validation_failed"


class PredictionValidationFailedError(ValidationError):
    code = "atlascore.prediction_validation_failed"


class ModelNotAvailableError(AtlasCoreError):
    code = "atlascore.model_not_available"


class FeedbackWindowNotCompletedError(AtlasCoreError):
    code = "atlascore.feedback_window_not_completed"


class MockDataForbiddenError(AtlasCoreError):
    code = "atlascore.mock_data_forbidden"


class ProvenanceChainBrokenError(ValidationError):
    code = "atlascore.provenance_chain_broken"


class InvalidScoreError(ValidationError):
    code = "atlascore.invalid_score"


class InvalidConfidenceError(ValidationError):
    code = "atlascore.invalid_confidence"


class DomainPackInvalidError(SchemaViolationError):
    code = "atlascore.domain_pack_invalid"
