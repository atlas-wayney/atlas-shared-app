"""Tests for Configs entity"""

from atlas_shared_app.entities import AtlasConfigs, AtlasConfigsBase, AtlasConfigsReq, AtlasConfigsRes


def test_configs_base_creation():
    """Test basic configs base creation"""
    config = AtlasConfigsBase(
        entity_type="case",
        field_name="priority",
        options={"low": "Low", "medium": "Medium", "high": "High"},
    )
    assert config.entity_type == "case"
    assert config.field_name == "priority"
    assert config.options == {"low": "Low", "medium": "Medium", "high": "High"}


def test_configs_creation():
    """Test full configs creation"""
    config = AtlasConfigs(
        entity_type="document",
        field_name="document_type",
        options={"contract": "Contract", "invoice": "Invoice", "report": "Report", "other": "Other"},
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER001",
        updater_name="John Doe",
    )
    assert config.entity_type == "document"
    assert config.field_name == "document_type"
    assert len(config.options) == 4
    assert "contract" in config.options


def test_configs_empty_options():
    """Test configs with empty options dict"""
    config = AtlasConfigsBase(
        entity_type="case",
        field_name="custom_field",
        options={},
    )
    assert config.options == {}


def test_configs_single_option():
    """Test configs with single option"""
    config = AtlasConfigsBase(
        entity_type="case",
        field_name="single_choice",
        options={"only_option": "Only Option"},
    )
    assert len(config.options) == 1


def test_configs_req_creation():
    """Test configs request model"""
    req = AtlasConfigsReq(
        entity_type="remark",
        field_name="remark_type",
        options={"note": "Note", "warning": "Warning", "error": "Error"},
    )
    assert req.entity_type == "remark"
    assert req.field_name == "remark_type"


def test_configs_res_creation():
    """Test configs response model"""
    res = AtlasConfigsRes(
        entity_type="case",
        field_name="status",
        options={"open": "Open", "closed": "Closed", "pending": "Pending"},
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER002",
        updater_name="Jane Smith",
    )
    assert res.entity_type == "case"
    assert res.field_name == "status"
    assert res.updater_name == "Jane Smith"
