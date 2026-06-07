"""Tests for Case entity"""

from atlas_shared_app.entities import AtlasCase, AtlasCaseStatus


def test_case_creation():
    """Test basic case creation"""
    case = AtlasCase(
        case_id="CASE001",
        case_type="support",
        title="Test Case Title",
        case_status=AtlasCaseStatus.SUBMITTED,
        client_id="CLIENT001",
        client_name="Test Client",
        assigned_user_id="USER001",
        assigned_user_name="John Doe",
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER001",
        updater_name="John Doe",
        data={"priority": "high"},
    )
    assert case.case_id == "CASE001"
    assert case.case_type == "support"
    assert case.title == "Test Case Title"
    assert case.case_status == AtlasCaseStatus.SUBMITTED
    assert case.client_id == "CLIENT001"
    assert case.client_name == "Test Client"
    assert case.data == {"priority": "high"}


def test_case_status_enum():
    """Test AtlasCaseStatus enum values"""
    assert hasattr(AtlasCaseStatus, "SUBMITTED")
    assert hasattr(AtlasCaseStatus, "APPROVED")
    assert hasattr(AtlasCaseStatus, "REJECTED")
    assert hasattr(AtlasCaseStatus, "CLOSED")
    assert AtlasCaseStatus.SUBMITTED == "SUBMITTED"
    assert AtlasCaseStatus.CLOSED == "CLOSED"