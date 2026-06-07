"""Tests for History entity"""

from atlas_shared_app.entities import AtlasHistory, AtlasHistoryBase, AtlasHistoryReq, AtlasHistoryRes


def test_history_base_creation():
    """Test basic history base creation"""
    history = AtlasHistoryBase(
        entity_type="case",
        entity_id="CASE001",
        action="CREATE",
        description="Case created",
        internal_only=True,
    )
    assert history.entity_type == "case"
    assert history.entity_id == "CASE001"
    assert history.action == "CREATE"
    assert history.description == "Case created"
    assert history.internal_only is True


def test_history_creation():
    """Test full history creation"""
    history = AtlasHistory(
        history_id="HIST002",
        entity_type="document",
        entity_id="DOC002",
        action="UPDATE",
        description="Document updated with new content",
        internal_only=False,
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER001",
        updater_name="John Doe",
    )
    assert history.history_id == "HIST002"
    assert history.entity_type == "document"
    assert history.action == "UPDATE"
    assert history.internal_only is False


def test_history_default_internal_only():
    """Test history default internal_only value"""
    history = AtlasHistoryBase(
        entity_type="case",
        entity_id="CASE003",
        action="DELETE",
        description="Case deleted",
    )
    assert history.internal_only is True


def test_history_no_entity_id():
    """Test history without entity_id"""
    history = AtlasHistoryBase(
        entity_type="system",
        action="SYSTEM_EVENT",
        description="System maintenance performed",
    )
    assert history.entity_id is None


def test_history_req_creation():
    """Test history request model"""
    req = AtlasHistoryReq(
        entity_type="case",
        entity_id="CASE005",
        action="UPDATE_STATUS",
        description="Case status changed to APPROVED",
        internal_only=True,
    )
    assert req.entity_type == "case"
    assert req.action == "UPDATE_STATUS"


def test_history_res_creation():
    """Test history response model"""
    res = AtlasHistoryRes(
        history_id="HIST006",
        entity_type="remark",
        entity_id="REM006",
        action="ADD_REMARK",
        description="New remark added",
        internal_only=True,
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER001",
        updater_name="John Doe",
    )
    assert res.history_id == "HIST006"
    assert res.action == "ADD_REMARK"
