"""Tests for Document entity"""

from atlas_shared_app.entities import AtlasDocument, AtlasDocumentBase, AtlasDocumentReq, AtlasDocumentRes


def test_document_base_creation():
    """Test basic document base creation"""
    doc = AtlasDocumentBase(
        document_name="test_file.pdf",
        entity_type="case",
        entity_id="CASE001",
    )
    assert doc.document_name == "test_file.pdf"
    assert doc.entity_type == "case"
    assert doc.entity_id == "CASE001"


def test_document_creation():
    """Test full document creation with all fields"""
    doc = AtlasDocument(
        document_id="DOC002",
        document_name="contract.pdf",
        entity_type="case",
        entity_id="CASE002",
        bucket="my-bucket",
        fullpath="documents/contract.pdf",
        internal_only=True,
        deleted=False,
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER001",
        updater_name="John Doe",
    )
    assert doc.document_id == "DOC002"
    assert doc.document_name == "contract.pdf"
    assert doc.bucket == "my-bucket"
    assert doc.fullpath == "documents/contract.pdf"
    assert doc.internal_only is True
    assert doc.deleted is False


def test_document_default_values():
    """Test document default values"""
    doc = AtlasDocument(
        document_id="DOC003",
        document_name="report.xlsx",
        entity_type="remark",
        bucket="bucket",
        fullpath="reports/report.xlsx",
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER001",
        updater_name="John Doe",
    )
    assert doc.internal_only is True
    assert doc.deleted is False
    assert doc.entity_id is None


def test_document_req_creation():
    """Test document request model"""
    req = AtlasDocumentReq(
        document_name="spec.docx",
        entity_type="case",
        entity_id="CASE004",
    )
    assert req.document_name == "spec.docx"
    assert req.entity_type == "case"


def test_document_res_creation():
    """Test document response model"""
    res = AtlasDocumentRes(
        document_id="DOC005",
        document_name="invoice.pdf",
        entity_type="case",
        entity_id="CASE005",
        bucket="invoices-bucket",
        fullpath="invoices/2024/invoice.pdf",
        internal_only=False,
        deleted=False,
        creater_id="USER001",
        creater_name="John Doe",
        updater_id="USER002",
        updater_name="Jane Smith",
    )
    assert res.document_id == "DOC005"
    assert res.internal_only is False
    assert res.updater_name == "Jane Smith"
