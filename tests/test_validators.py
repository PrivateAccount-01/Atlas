"""Validator tests for AtlasCore foundation."""
import pytest
from uuid import uuid4

from atlascore.contracts.models import (
    Signal,
    ValidationResult,
    RelationshipEdge,
    DetectedEvent,
    ProvenanceLink,
)
from atlascore import validators, errors


class TestSignalValidation:
    """Test Signal validation."""

    def test_signal_without_evidence_rejected(self):
        """Test signal without evidence fails."""
        sig = Signal(source_refs=[uuid4()], metric="m", evidence=[])
        with pytest.raises(errors.SignalValidationFailedError):
            validators.validate_signal(sig)

    def test_signal_without_provenance_rejected(self):
        """Test signal without provenance fails."""
        sig = Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()], provenance=[])
        with pytest.raises(errors.ProvenanceChainBrokenError):
            validators.validate_signal(sig)

    def test_signal_with_evidence_and_provenance_passes(self):
        """Test signal with evidence and provenance passes."""
        sig = Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()])
        sig.provenance = [ProvenanceLink(artifact_id=sig.id, action="ingest", actor="tester")]
        vr = validators.validate_signal(sig)
        assert vr.passed is True

    def test_signal_with_invalid_score_rejected(self):
        """Test signal with invalid score fails."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()], score=1.5)

    def test_signal_with_invalid_confidence_rejected(self):
        """Test signal with invalid confidence fails."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()], confidence=-0.1)


class TestPredictionValidation:
    """Test Prediction validation."""

    def test_prediction_without_signal_refs_rejected(self):
        """Test prediction without signal refs fails."""
        from atlascore.contracts.models import Prediction
        from datetime import datetime, timezone

        pred = Prediction(
            model_version=uuid4(),
            input_signal_refs=[],
            prediction_ts=datetime.now(timezone.utc),
        )
        with pytest.raises(errors.PredictionValidationFailedError):
            validators.validate_prediction(pred, {})

    def test_prediction_with_unvalidated_signal_rejected(self):
        """Test prediction with unvalidated signal fails."""
        from atlascore.contracts.models import Prediction
        from datetime import datetime, timezone

        sig_id = uuid4()
        sig = Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()])
        pred = Prediction(
            model_version=uuid4(),
            input_signal_refs=[sig_id],
            prediction_ts=datetime.now(timezone.utc),
        )
        with pytest.raises(errors.MissingDataError):
            validators.validate_prediction(pred, {})

    def test_prediction_with_validated_signal_passes(self):
        """Test prediction with validated signal passes."""
        from atlascore.contracts.models import Prediction
        from datetime import datetime, timezone

        sig_id = uuid4()
        vr = ValidationResult(rules_run=["test"], passed=True)
        sig = Signal(
            source_refs=[uuid4()], metric="m", evidence=[uuid4()], validated=vr, id=sig_id
        )
        pred = Prediction(
            model_version=uuid4(),
            input_signal_refs=[sig_id],
            prediction_ts=datetime.now(timezone.utc),
        )
        vr2 = validators.validate_prediction(pred, {sig_id: sig})
        assert vr2.passed is True


class TestRelationshipEdgeValidation:
    """Test RelationshipEdge validation."""

    def test_relationship_edge_without_evidence_rejected(self):
        """Test relationship edge without evidence fails."""
        edge = RelationshipEdge(
            from_id=uuid4(), to_id=uuid4(), type="supplies", evidence_refs=[], ontology_version=1
        )
        with pytest.raises(errors.InsufficientEvidenceError):
            validators.validate_relationship_edge(edge)

    def test_relationship_edge_without_provenance_rejected(self):
        """Test relationship edge without provenance fails."""
        edge = RelationshipEdge(
            from_id=uuid4(),
            to_id=uuid4(),
            type="supplies",
            evidence_refs=[uuid4()],
            ontology_version=1,
            provenance=[],
        )
        with pytest.raises(errors.ProvenanceChainBrokenError):
            validators.validate_relationship_edge(edge)

    def test_relationship_edge_with_invalid_type_rejected(self):
        """Test relationship edge with unknown type fails."""
        edge = RelationshipEdge(
            from_id=uuid4(),
            to_id=uuid4(),
            type="unknown_type",
            evidence_refs=[uuid4()],
            ontology_version=1,
        )
        edge.provenance = [ProvenanceLink(artifact_id=edge.id, action="test", actor="tester")]
        with pytest.raises(errors.OntologyValidationFailedError):
            validators.validate_relationship_edge(edge, relationship_types={"supplies"})

    def test_relationship_edge_with_invalid_weight_rejected(self):
        """Test relationship edge with invalid weight fails."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            RelationshipEdge(
                from_id=uuid4(),
                to_id=uuid4(),
                type="supplies",
                evidence_refs=[uuid4()],
                ontology_version=1,
                weight=1.5,
            )

    def test_relationship_edge_passes_with_valid_data(self):
        """Test relationship edge passes with valid data."""
        edge = RelationshipEdge(
            from_id=uuid4(),
            to_id=uuid4(),
            type="supplies",
            evidence_refs=[uuid4()],
            ontology_version=1,
            weight=0.8,
        )
        edge.provenance = [ProvenanceLink(artifact_id=edge.id, action="test", actor="tester")]
        vr = validators.validate_relationship_edge(edge, relationship_types={"supplies"})
        assert vr.passed is True


class TestDetectedEventValidation:
    """Test DetectedEvent validation."""

    def test_detected_event_without_evidence_rejected(self):
        """Test detected event without evidence fails."""
        from datetime import datetime, timezone

        event = DetectedEvent(
            event_type="delivery_delay",
            participants=[uuid4()],
            evidence_refs=[],
            event_ts=datetime.now(timezone.utc),
        )
        with pytest.raises(errors.InsufficientEvidenceError):
            validators.validate_detected_event(event)

    def test_detected_event_with_unknown_type_rejected(self):
        """Test detected event with unknown type fails."""
        from datetime import datetime, timezone

        event = DetectedEvent(
            event_type="unknown_event",
            participants=[uuid4()],
            evidence_refs=[uuid4()],
            event_ts=datetime.now(timezone.utc),
        )
        event.provenance = [ProvenanceLink(artifact_id=event.id, action="test", actor="tester")]
        with pytest.raises(errors.UnknownEventTypeError):
            validators.validate_detected_event(event, event_types={"delivery_delay"})

    def test_detected_event_passes_with_valid_data(self):
        """Test detected event passes with valid data."""
        from datetime import datetime, timezone

        event = DetectedEvent(
            event_type="delivery_delay",
            participants=[uuid4()],
            evidence_refs=[uuid4()],
            event_ts=datetime.now(timezone.utc),
        )
        event.provenance = [ProvenanceLink(artifact_id=event.id, action="test", actor="tester")]
        vr = validators.validate_detected_event(event, event_types={"delivery_delay"})
        assert vr.passed is True


class TestMockDataDetection:
    """Test mock data rejection."""

    def test_mock_data_outside_fixtures_rejected(self):
        """Test mock data outside tests/fixtures rejected."""
        path = "data/production_data.json"
        with pytest.raises(errors.MockDataForbiddenError):
            validators.reject_mock_data(path, "production_data")

    def test_mock_data_in_fixtures_allowed(self):
        """Test mock data in tests/fixtures allowed."""
        path = "tests/fixtures/synthetic_data.json"
        # Should not raise
        validators.reject_mock_data(path, "test_fixture")

