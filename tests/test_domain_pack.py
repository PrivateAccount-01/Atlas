"""Domain pack loader tests."""
import pytest
from pathlib import Path
from atlascore.domain_pack.loader import load_domain_pack
from atlascore import errors


class TestDomainPackLoader:
    """Test domain pack loader."""

    def test_domain_pack_loads_successfully(self):
        """Test domain pack loads successfully."""
        pack = load_domain_pack("domain_packs/supply_chain")
        assert "entity_types" in pack
        assert "event_types" in pack
        assert "relationship_types" in pack
        assert "signals" in pack
        assert "prediction_targets" in pack

    def test_missing_domain_pack_fails(self):
        """Test missing domain pack directory fails."""
        with pytest.raises(errors.MissingDataError):
            load_domain_pack("domain_packs/nonexistent")

    def test_entity_types_loaded_from_pack(self):
        """Test entity types loaded from pack."""
        pack = load_domain_pack("domain_packs/supply_chain")
        assert "supplier" in pack["entity_types"]
        assert "shipment" in pack["entity_types"]

    def test_event_types_loaded_from_pack(self):
        """Test event types loaded from pack."""
        pack = load_domain_pack("domain_packs/supply_chain")
        assert "delivery_delay" in pack["event_types"]

    def test_relationship_types_loaded_from_pack(self):
        """Test relationship types loaded from pack."""
        pack = load_domain_pack("domain_packs/supply_chain")
        assert "supplies" in pack["relationship_types"]

    def test_signal_definitions_loaded_from_pack(self):
        """Test signal definitions loaded from pack."""
        pack = load_domain_pack("domain_packs/supply_chain")
        assert "on_time_rate" in pack["signals"]

    def test_prediction_targets_loaded_from_pack(self):
        """Test prediction targets loaded from pack."""
        pack = load_domain_pack("domain_packs/supply_chain")
        assert "delivery_delay_probability" in pack["prediction_targets"]
