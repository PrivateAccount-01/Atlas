import pytest
from uuid import uuid4

from atlascore.contracts.models import Signal, ValidationResult
from atlascore import validators, errors


def make_signal(with_evidence: bool = False, with_provenance: bool = False) -> Signal:
    sig = Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()] if with_evidence else [])
    if with_provenance:
        sig.provenance = [
            sig.provenance.__class__(artifact_id=sig.id, action="ingest", actor="tester")
        ]
    return sig


def test_validate_signal_missing_evidence_raises():
    sig = make_signal(with_evidence=False, with_provenance=False)
    with pytest.raises(errors.MissingEvidenceError):
        validators.validate_signal(sig)


def test_validate_signal_passes_with_evidence_and_provenance():
    sig = Signal(source_refs=[uuid4()], metric="m", evidence=[uuid4()], validated=None)
    # attach provenance using ProvenanceLink constructor
    from atlascore.contracts.models import ProvenanceLink

    sig.provenance = [ProvenanceLink(artifact_id=sig.id, action="ingest", actor="tester")]
    vr = validators.validate_signal(sig)
    assert vr.passed is True
