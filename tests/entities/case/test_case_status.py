"""Tests for Case status related entities"""

from atlas_shared_app.entities import AtlasCaseStatus, AtlasCaseStatusReq
from atlas_shared_app.entities.atlas_case import AtlasCaseStatusBase, AtlasCaseBase, AtlasCaseReq, AtlasCaseRes


def test_case_status_enum_values():
    """Test AtlasCaseStatus enum values"""
    assert AtlasCaseStatus.SUBMITTED == "SUBMITTED"
    assert AtlasCaseStatus.PENDING_APPROVAL == "PENDING_APPROVAL"
    assert AtlasCaseStatus.PENDING_1ST_APPROVAL == "PENDING_1ST_APPROVAL"
    assert AtlasCaseStatus.PENDING_2ND_APPROVAL == "PENDING_2ND_APPROVAL"
    assert AtlasCaseStatus.PENDING_3RD_APPROVAL == "PENDING_3RD_APPROVAL"
    assert AtlasCaseStatus.APPROVED == "APPROVED"
    assert AtlasCaseStatus.REJECTED == "REJECTED"
    assert AtlasCaseStatus.CLOSED == "CLOSED"


def test_case_status_enum_membership():
    """Test AtlasCaseStatus enum membership"""
    assert hasattr(AtlasCaseStatus, "SUBMITTED")
    assert hasattr(AtlasCaseStatus, "PENDING_APPROVAL")
    assert hasattr(AtlasCaseStatus, "PENDING_1ST_APPROVAL")
    assert hasattr(AtlasCaseStatus, "PENDING_2ND_APPROVAL")
    assert hasattr(AtlasCaseStatus, "PENDING_3RD_APPROVAL")
    assert hasattr(AtlasCaseStatus, "APPROVED")
    assert hasattr(AtlasCaseStatus, "REJECTED")
    assert hasattr(AtlasCaseStatus, "CLOSED")


def test_case_status_enum_iteration():
    """Test AtlasCaseStatus enum iteration"""
    statuses = list(AtlasCaseStatus)
    assert len(statuses) == 9
    assert AtlasCaseStatus.DRAFT in statuses
    assert AtlasCaseStatus.SUBMITTED in statuses
    assert AtlasCaseStatus.CLOSED in statuses


def test_case_status_base_creation():
    """Test AtlasCaseStatusBase creation"""
    status_base = AtlasCaseStatusBase(
        case_status=AtlasCaseStatus.SUBMITTED,
        assigned_user_id="USER001",
        assigned_user_name="John Doe",
    )
    assert status_base.case_status == AtlasCaseStatus.SUBMITTED
    assert status_base.assigned_user_id == "USER001"
    assert status_base.assigned_user_name == "John Doe"


def test_case_status_req_creation():
    """Test AtlasCaseStatusReq creation"""
    req = AtlasCaseStatusReq(
        case_status=AtlasCaseStatus.APPROVED,
        assigned_user_id="USER002",
        assigned_user_name="Jane Smith",
        remark="Approved after review",
    )
    assert req.case_status == AtlasCaseStatus.APPROVED
    assert req.assigned_user_id == "USER002"
    assert req.assigned_user_name == "Jane Smith"
    assert req.remark == "Approved after review"


def test_case_base_creation():
    """Test AtlasCaseBase creation"""
    case_base = AtlasCaseBase(
        case_type="support",
        title="Test Case Title",
        case_status=AtlasCaseStatus.SUBMITTED,
        client_id="CLIENT001",
        client_name="Test Client",
        assigned_user_id="USER001",
        assigned_user_name="John Doe",
        data={"priority": "high"},
    )
    assert case_base.case_type == "support"
    assert case_base.title == "Test Case Title"
    assert case_base.client_id == "CLIENT001"
    assert case_base.data == {"priority": "high"}


def test_case_base_optional_entity_id():
    """Test AtlasCaseBase with optional entity_id"""
    case_base = AtlasCaseBase(
        case_type="request",
        title="Request Case",
        case_status=AtlasCaseStatus.PENDING_APPROVAL,
        client_id="CLIENT002",
        client_name="Another Client",
        assigned_user_id="USER002",
        assigned_user_name="Jane Doe",
        entity_id="REF001",
        data={},
    )
    assert case_base.entity_id == "REF001"


def test_case_base_no_entity_id():
    """Test AtlasCaseBase without entity_id"""
    case_base = AtlasCaseBase(
        case_type="inquiry",
        title="Inquiry Case",
        case_status=AtlasCaseStatus.SUBMITTED,
        client_id="CLIENT003",
        client_name="Third Client",
        assigned_user_id="USER003",
        assigned_user_name="Bob Smith",
        data={},
    )
    assert case_base.entity_id is None


def test_case_req_creation():
    """Test AtlasCaseReq creation"""
    req = AtlasCaseReq(
        case_type="support",
        title="Support Request",
        case_status=AtlasCaseStatus.SUBMITTED,
        client_id="CLIENT004",
        client_name="Client Four",
        assigned_user_id="USER004",
        assigned_user_name="Alice Johnson",
        data={"issue": "network problem"},
    )
    assert req.case_type == "support"
    assert req.title == "Support Request"


def test_case_res_creation():
    """Test AtlasCaseRes creation"""
    res = AtlasCaseRes(
        case_id="CASE005",
        case_type="support",
        title="Case Response",
        case_status=AtlasCaseStatus.APPROVED,
        client_id="CLIENT005",
        client_name="Client Five",
        assigned_user_id="USER005",
        assigned_user_name="Charlie Brown",
        data={"resolution": "fixed"},
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER002",
        updater_name="Jane Smith",
    )
    assert res.case_id == "CASE005"
    assert res.case_status == AtlasCaseStatus.APPROVED
    assert res.updater_name == "Jane Smith"
