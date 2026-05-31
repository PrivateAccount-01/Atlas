"""Pydantic contracts for AtlasCore foundation stage.

Minimal, explicit schemas including stable IDs, timestamps, schema_version,
validation_status, and provenance metadata.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any, Literal
from uuid import UUID, uuid4
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _validate_score(v: float) -> float:
    """Enforce score is in [0, 1]."""
    if not (0 <= v <= 1):
        raise ValueError(f"Score must be in [0, 1], got {v}")
    return v


def _validate_confidence(v: float) -> float:
    """Enforce confidence is in [0, 1]."""
    if not (0 <= v <= 1):
        raise ValueError(f"Confidence must be in [0, 1], got {v}")
    return v


def _validate_weight(v: float) -> float:
    """Enforce relationship weight is in [-1, 1]."""
    if not (-1 <= v <= 1):
        raise ValueError(f"Weight must be in [-1, 1], got {v}")
    return v


class ProvenanceLink(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    artifact_id: UUID
    action: str
    actor: str
    ts: datetime = Field(default_factory=_now_utc)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    ts: datetime = Field(default_factory=_now_utc)
    schema_version: int = 1
    validation_status: Literal["UNKNOWN", "VALID", "INVALID"] = "UNKNOWN"
    provenance: List[ProvenanceLink] = Field(default_factory=list)


class ValidationResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    rules_run: List[str]
    passed: bool
    failures: Optional[List[str]] = None
    ts: datetime = Field(default_factory=_now_utc)
    provenance: List[ProvenanceLink] = Field(default_factory=list)


class SourceRecord(BaseSchema):
    source_id: str
    payload_ref: str


class RawDocument(BaseSchema):
    body_ref: str
    format: str
    content_hash: str


class CleanDocument(BaseSchema):
    derived_from: UUID
    normalized_fields: Dict[str, Any]
    validation_result: Optional[ValidationResult] = None


class CanonicalEntity(BaseSchema):
    type: str
    attributes: Dict[str, Any]
    canonical_sources: List[UUID]


class DetectedEvent(BaseSchema):
    event_type: str
    participants: List[UUID]
    evidence_refs: List[UUID]
    event_ts: datetime


class RelationshipEdge(BaseSchema):
    from_id: UUID
    to_id: UUID
    type: str
    evidence_refs: List[UUID]
    ontology_version: int
    weight: float = 0.0
    
    @field_validator("weight")
    @classmethod
    def validate_weight_range(cls, v: float) -> float:
        return _validate_weight(v)


class Signal(BaseSchema):
    source_refs: List[UUID]
    metric: str
    evidence: List[UUID]
    score: float = 0.0
    confidence: float = 0.0
    validated: Optional[ValidationResult] = None
    
    @field_validator("score")
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        return _validate_score(v)
    
    @field_validator("confidence")
    @classmethod
    def validate_confidence_range(cls, v: float) -> float:
        return _validate_confidence(v)


class Prediction(BaseSchema):
    model_version: UUID
    input_signal_refs: List[UUID]
    prediction_ts: datetime
    status: Literal["DRAFT", "VALIDATED", "REJECTED"] = "DRAFT"
    score: Optional[float] = None
    confidence: Optional[float] = None
    
    @field_validator("score")
    @classmethod
    def validate_score_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            return _validate_score(v)
        return v
    
    @field_validator("confidence")
    @classmethod
    def validate_confidence_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            return _validate_confidence(v)
        return v


class FeedbackRecord(BaseSchema):
    related_id: UUID
    feedback_type: str
    payload: Dict[str, Any]


class ModelVersion(BaseSchema):
    name: str
    version: str
    created_ts: datetime = Field(default_factory=_now_utc)
    metadata: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "BaseSchema",
    "ProvenanceLink",
    "ValidationResult",
    "SourceRecord",
    "RawDocument",
    "CleanDocument",
    "CanonicalEntity",
    "DetectedEvent",
    "RelationshipEdge",
    "Signal",
    "Prediction",
    "FeedbackRecord",
    "ModelVersion",
]
