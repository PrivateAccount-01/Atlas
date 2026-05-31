import pytest
from uuid import uuid4
from datetime import datetime, timezone

from atlascore.contracts.models import (
    SourceRecord,
    RawDocument,
    CleanDocument,
    Signal,
    ValidationResult,
)


def test_source_and_raw_document_have_required_fields():
    s = SourceRecord(source_id="src-1", payload_ref="ref")
    r = RawDocument(body_ref="bref", format="json")
    assert s.id is not None
    assert r.ts.tzinfo is not None


def test_clean_document_links_to_raw():
    raw = RawDocument(body_ref="bref", format="json")
    clean = CleanDocument(derived_from=raw.id, normalized_fields={"k": "v"})
    assert clean.derived_from == raw.id


def test_signal_validation_result_attachable():
    vr = ValidationResult(rules_run=["r1"], passed=True)
    sig = Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()], validated=vr)
    assert sig.validated.passed is True
