"""Tests for Client entity"""

from datetime import datetime

from atlas_shared_app.entities import AtlasClient, AppEnum


def test_client_creation():
    """Test basic client creation"""
    client = AtlasClient(
        client_id="CLIENT001",
        client_name="Acme Corporation",
        client_status="active",
        supported_email_domains=["acme.com", "acme.io"],
        allowed_apps=[AppEnum.ATLAS_APP_IDENTITY, AppEnum.ATLAS_APP_NETWORK],
        tags=["tag1", "tag2"],
        terms_acceptances={"terms_v1": datetime(2024, 1, 15)},
        creater_id="ADMIN001",
        creater_name="Admin User",
        updater_id="ADMIN001",
        updater_name="Admin User",
    )
    assert client.client_id == "CLIENT001"
    assert client.client_name == "Acme Corporation"
    assert client.client_status == "active"
    assert client.supported_email_domains == ["acme.com", "acme.io"]
    assert client.allowed_apps == [AppEnum.ATLAS_APP_IDENTITY, AppEnum.ATLAS_APP_NETWORK]
    assert client.tags == ["tag1", "tag2"]


def test_client_email_domains():
    """Test client with multiple email domains"""
    client = AtlasClient(
        client_id="CLIENT002",
        client_name="Tech Corp",
        client_status="active",
        supported_email_domains=["tech.com", "tech.org", "tech.net"],
        allowed_apps=[AppEnum.ATLAS_APP_IDENTITY],
        tags=["tag3"],
        terms_acceptances={"terms_v1": datetime(2024, 1, 15)},
        creater_id="ADMIN001",
        creater_name="Admin User",
        updater_id="ADMIN001",
        updater_name="Admin User",
    )
    assert len(client.supported_email_domains) == 3
    assert "tech.com" in client.supported_email_domains
