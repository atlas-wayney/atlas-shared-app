"""Tests for base model"""

from datetime import datetime
from atlas_shared_app.entities import AtlasBaseModel
from atlas_shared_app.entities.atlas_base_model import AtlasEntity


def test_atlas_entity_fields():
    """Test AtlasEntity has required fields"""
    # AtlasEntity is abstract, test its field definitions
    assert "id" in AtlasEntity.model_fields
    assert "name" in AtlasEntity.model_fields


def test_atlas_base_model_fields():
    """Test AtlasBaseModel has required fields"""
    assert "create_time" in AtlasBaseModel.model_fields
    assert "creater_id" in AtlasBaseModel.model_fields
    assert "creater_name" in AtlasBaseModel.model_fields
    assert "update_time" in AtlasBaseModel.model_fields
    assert "updater_id" in AtlasBaseModel.model_fields
    assert "updater_name" in AtlasBaseModel.model_fields


def test_atlas_base_model_field_types():
    """Test AtlasBaseModel field types"""
    fields = AtlasBaseModel.model_fields

    # Check creater/updater fields are strings
    assert fields["creater_id"].annotation == str
    assert fields["creater_name"].annotation == str
    assert fields["updater_id"].annotation == str
    assert fields["updater_name"].annotation == str

    # Check time fields are datetime
    assert fields["create_time"].annotation == datetime
    assert fields["update_time"].annotation == datetime
