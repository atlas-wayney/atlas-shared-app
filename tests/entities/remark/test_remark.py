"""Tests for Remark entity"""

from atlas_shared_app.entities import AtlasRemark, AtlasRemarkBase, AtlasRemarkReq, AtlasRemarkRes


def test_remark_base_creation():
    """Test basic remark base creation"""
    remark = AtlasRemarkBase(
        entity_type="case",
        entity_id="CASE001",
        remark="This is a test remark",
        internal_only=True,
    )
    assert remark.entity_type == "case"
    assert remark.entity_id == "CASE001"
    assert remark.remark == "This is a test remark"
    assert remark.internal_only is True


def test_remark_creation():
    """Test full remark creation"""
    remark = AtlasRemark(
        remark_id="REM002",
        entity_type="document",
        entity_id="DOC002",
        remark="Document needs review",
        internal_only=False,
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER001",
        updater_name="John Doe",
    )
    assert remark.remark_id == "REM002"
    assert remark.entity_type == "document"
    assert remark.remark == "Document needs review"
    assert remark.internal_only is False


def test_remark_default_internal_only():
    """Test remark default internal_only value"""
    remark = AtlasRemarkBase(
        entity_type="case",
        entity_id="CASE003",
        remark="Default internal only test",
    )
    assert remark.internal_only is True


def test_remark_no_entity_id():
    """Test remark without entity_id"""
    remark = AtlasRemarkBase(
        entity_type="general",
        remark="General system remark",
    )
    assert remark.entity_id is None


def test_remark_long_content():
    """Test remark with longer content"""
    long_remark = "This is a very long remark " * 50
    remark = AtlasRemarkBase(
        entity_type="case",
        entity_id="CASE005",
        remark=long_remark,
    )
    assert len(remark.remark) > 1000


def test_remark_req_creation():
    """Test remark request model"""
    req = AtlasRemarkReq(
        entity_type="case",
        entity_id="CASE006",
        remark="Request remark content",
        internal_only=True,
    )
    assert req.entity_type == "case"
    assert req.remark == "Request remark content"


def test_remark_res_creation():
    """Test remark response model"""
    res = AtlasRemarkRes(
        remark_id="REM007",
        entity_type="case",
        entity_id="CASE007",
        remark="Response remark content",
        internal_only=False,
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER002",
        updater_name="Jane Smith",
    )
    assert res.remark_id == "REM007"
    assert res.updater_name == "Jane Smith"
