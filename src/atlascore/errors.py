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
