"""Contract and model tests for AtlasCore foundation."""
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from atlascore.contracts.models import (
    SourceRecord,
    RawDocument,
    CleanDocument,
    Signal,
    ValidationResult,
    RelationshipEdge,
    Prediction,
    ProvenanceLink,
)
from atlascore import errors


class TestSourceRecord:
    """Test SourceRecord contract."""

    def test_source_record_has_required_fields(self):
        """Test SourceRecord valid creation."""
        s = SourceRecord(source_id="src-1", payload_ref="ref-1")
        assert s.id is not None
        assert s.ts is not None
        assert s.schema_version == 1
        assert s.validation_status == "UNKNOWN"
        assert s.source_id == "src-1"

    def test_source_record_has_provenance(self):
        """Test SourceRecord has provenance list."""
        s = SourceRecord(source_id="src-1", payload_ref="ref-1")
        assert isinstance(s.provenance, list)
        assert len(s.provenance) == 0


class TestRawDocument:
    """Test RawDocument contract."""

    def test_raw_document_requires_content_hash(self):
        """Test RawDocument requires content hash."""
        with pytest.raises(Exception):  # Pydantic validation error
            RawDocument(body_ref="bref", format="json")  # missing content_hash

    def test_raw_document_valid_with_hash(self):
        """Test RawDocument valid creation with content hash."""
        doc = RawDocument(body_ref="bref", format="json", content_hash="sha256-abc123")
        assert doc.content_hash == "sha256-abc123"
        assert doc.body_ref == "bref"


class TestCleanDocument:
    """Test CleanDocument contract."""

    def test_clean_document_links_to_raw(self):
        """Test CleanDocument links to RawDocument."""
        raw = RawDocument(body_ref="bref", format="json", content_hash="hash")
        clean = CleanDocument(derived_from=raw.id, normalized_fields={"k": "v"})
        assert clean.derived_from == raw.id


class TestSignal:
    """Test Signal contract with score and confidence validation."""

    def test_signal_valid_score_confidence(self):
        """Test Signal with valid score and confidence."""
        sig = Signal(
            source_refs=[uuid4()],
            metric="m",
            evidence=[uuid4()],
            score=0.8,
            confidence=0.9,
        )
        assert sig.score == 0.8
        assert sig.confidence == 0.9

    def test_signal_invalid_score_rejected(self):
        """Test invalid score rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            Signal(
                source_refs=[uuid4()],
                metric="m",
                evidence=[uuid4()],
                score=1.5,  # out of range
                confidence=0.5,
            )

    def test_signal_invalid_confidence_rejected(self):
        """Test invalid confidence rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            Signal(
                source_refs=[uuid4()],
                metric="m",
                evidence=[uuid4()],
                score=0.5,
                confidence=-0.1,  # out of range
            )

    def test_signal_validation_result_attachable(self):
        """Test Signal can attach ValidationResult."""
        vr = ValidationResult(rules_run=["r1"], passed=True)
        sig = Signal(
            source_refs=[uuid4()],
            metric="m",
            evidence=[uuid4()],
            validated=vr,
        )
        assert sig.validated.passed is True


class TestRelationshipEdge:
    """Test RelationshipEdge contract with weight validation."""

    def test_relationship_edge_valid_weight(self):
        """Test RelationshipEdge with valid weight."""
        edge = RelationshipEdge(
            from_id=uuid4(),
            to_id=uuid4(),
            type="supplies",
            evidence_refs=[uuid4()],
            ontology_version=1,
            weight=0.8,
        )
        assert edge.weight == 0.8

    def test_relationship_edge_invalid_weight_rejected(self):
        """Test invalid relationship weight rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            RelationshipEdge(
                from_id=uuid4(),
                to_id=uuid4(),
                type="supplies",
                evidence_refs=[uuid4()],
                ontology_version=1,
                weight=1.5,  # out of range
            )

    def test_relationship_edge_negative_weight_valid(self):
        """Test RelationshipEdge allows negative weights."""
        edge = RelationshipEdge(
            from_id=uuid4(),
            to_id=uuid4(),
            type="supplies",
            evidence_refs=[uuid4()],
            ontology_version=1,
            weight=-0.5,
        )
        assert edge.weight == -0.5


class TestPrediction:
    """Test Prediction contract with score and confidence."""

    def test_prediction_valid_score_confidence(self):
        """Test Prediction with valid score and confidence."""
        pred = Prediction(
            model_version=uuid4(),
            input_signal_refs=[uuid4()],
            prediction_ts=datetime.now(timezone.utc),
            status="VALIDATED",
            score=0.7,
            confidence=0.85,
        )
        assert pred.score == 0.7
        assert pred.confidence == 0.85

    def test_prediction_invalid_score_rejected(self):
        """Test Prediction with invalid score rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            Prediction(
                model_version=uuid4(),
                input_signal_refs=[uuid4()],
                prediction_ts=datetime.now(timezone.utc),
                score=2.0,  # out of range
            )

    def test_prediction_invalid_confidence_rejected(self):
        """Test Prediction with invalid confidence rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            Prediction(
                model_version=uuid4(),
                input_signal_refs=[uuid4()],
                prediction_ts=datetime.now(timezone.utc),
                confidence=-0.5,  # out of range
            )

    def test_prediction_optional_score_none(self):
        """Test Prediction allows None score."""
        pred = Prediction(
            model_version=uuid4(),
            input_signal_refs=[uuid4()],
            prediction_ts=datetime.now(timezone.utc),
            score=None,
        )
        assert pred.score is None

