
from dataclasses import dataclass
from sqlmodel import Field, Column, SQLModel, Index
from sqlalchemy import JSON
from enum import StrEnum
from typing import Any, Optional

from .atlas_base_enums import EntityStatus
from .atlas_base_model import AtlasBaseModel

### helper values for CaseStatus
class AtlasCaseStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    PENDING_1ST_APPROVAL = "PENDING_1ST_APPROVAL"
    PENDING_2ND_APPROVAL = "PENDING_2ND_APPROVAL"
    PENDING_3RD_APPROVAL = "PENDING_3RD_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"

@dataclass
class AtlasCaseWorkflowEntity:
    curr_user_id: str
    curr_user_name: str
    case_id: str
    entity_type: str
    entity_id: Optional[str]
    data: Optional[dict[str, Any]]

@dataclass
class AtlasCaseWorkflowResultEntity():
    success: bool
    case_id: str
    entity_type: str
    entity_id: Optional[str]
    message: str

# this class is created to adjust table column order only..
class AtlasCasePrimaryKey(SQLModel):
    case_id: str = Field(primary_key=True, max_length=50)

class AtlasCaseStatusBase(SQLModel):
    case_status: str = Field(default=EntityStatus.PENDING_APPROVAL, index=True, max_length=50)
    assigned_user_id: str = Field(index=True, max_length=50)
    assigned_user_name: str = Field(max_length=500)

class AtlasCaseBase(AtlasCaseStatusBase):
    case_type: str = Field(index=True, max_length=50)
    title: str = Field(max_length=200)
    client_id: Optional[str] = Field(default=None, index=True, max_length=50)
    client_name: Optional[str] = Field(default=None, max_length=500)
    entity_type: str = Field(default=None, index=True, max_length=50)
    ### entity id to the entity this case created after approval, e.g. Rack Id or Cross Connect Id
    entity_id: Optional[str] = Field(default=None, index=True, max_length=50) 
    data: dict[str, Any] = Field(sa_column=Column(JSON))

## the sequence of the inherited classes matter to adjust the table column order, last is first in the table
class AtlasCase(AtlasBaseModel, AtlasCaseBase, AtlasCasePrimaryKey, table=True):
    __table_args__ = (
        Index("idx_client_id_and_case_type", "client_id", "case_type"),
        Index("idx_client_id_and_case_status", "client_id", "case_status"),
        Index("idx_client_id_and_case_type_and_case_status", "client_id", "case_type", "case_status"),
        Index("idx_assigned_user_id_and_case_type", "assigned_user_id", "case_type"),
        Index("idx_assigned_user_id_and_case_status", "assigned_user_id", "case_status"),
        Index("idx_assigned_user_id_and_case_type_and_case_status", "assigned_user_id", "case_type", "case_status"),
    )
    pass

class AtlasCaseReq(AtlasCaseBase):
    pass

class AtlasCaseStatusReq(AtlasCaseStatusBase):
    remark: str = Field(max_length=2000)
    pass

class AtlasCaseRes(AtlasCaseBase, AtlasBaseModel, AtlasCasePrimaryKey):
    pass