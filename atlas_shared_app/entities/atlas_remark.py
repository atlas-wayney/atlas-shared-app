from typing import Optional
from sqlmodel import Field, SQLModel

from .atlas_base_model import AtlasBaseModel


# this class is created to adjust table column order only..
class AtlasRemarkPrimaryKey(SQLModel):
    remark_id: str = Field(primary_key=True, max_length=50)

class AtlasRemarkBase(SQLModel):
    entity_type: str = Field(max_length=50)
    entity_id: Optional[str] = Field(index=True, default=None, max_length=50)
    remark: str = Field(max_length=2000)
    internal_only: bool = True
    client_id: Optional[str] = Field(default=None, index=True, max_length=50)
    client_name: Optional[str] = Field(default=None, max_length=500)

class AtlasRemark(AtlasBaseModel, AtlasRemarkBase, AtlasRemarkPrimaryKey, table=True):
    pass

class AtlasRemarkReq(AtlasRemarkBase):
    pass

class AtlasRemarkRes(AtlasRemarkBase, AtlasBaseModel, AtlasRemarkPrimaryKey):
    pass