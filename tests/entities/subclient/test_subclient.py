"""Tests for Subclient entity"""

from atlas_shared_app.entities import AtlasSubclient


def test_subclient_creation():
    """Test basic subclient creation"""
    subclient = AtlasSubclient(
        subclient_id="SUBCLIENT001",
        subclient_name="Acme Corporation",
        subclient_status="active",
        parent_subclient_id="PARENT001",
        client_id="CLIENT001",
        client_name="Acme Group",
        country="USA",
        region="North America",
        tags=["tag1", "tag2"],
        creater_id="ADMIN001",
        creater_name="Admin User",
        updater_id="ADMIN001",
        updater_name="Admin User",
    )
    assert subclient.subclient_id == "SUBCLIENT001"
    assert subclient.subclient_name == "Acme Corporation"
    assert subclient.subclient_status == "active"
    assert subclient.client_id == "CLIENT001"
    assert subclient.client_name == "Acme Group"
    assert subclient.country == "USA"
    assert subclient.region == "North America"
    assert subclient.tags == ["tag1", "tag2"]


def test_subclient_with_client():
    """Test subclient with client"""
    subclient = AtlasSubclient(
        subclient_id="SUBCLIENT002",
        subclient_name="Tech Corp",
        subclient_status="active",
        parent_subclient_id="PARENT001",
        client_id="CLIENT002",
        client_name="Tech Group",
        country="UK",
        region="Europe",
        tags=["tag3"],
        creater_id="ADMIN001",
        creater_name="Admin User",
        updater_id="ADMIN001",
        updater_name="Admin User",
    )
    assert subclient.client_id == "CLIENT002"
    assert subclient.client_name == "Tech Group"
    assert subclient.country == "UK"
    assert subclient.region == "Europe"
