from typing import Optional
from sqlmodel import Field, SQLModel

from .atlas_base_model import AtlasBaseModel


# this class is created to adjust table column order only..
class AtlasHistoryPrimaryKey(SQLModel):
    history_id: str = Field(primary_key=True, max_length=50)

class AtlasHistoryBase(SQLModel):
    entity_type: str = Field(max_length=50)
    entity_id: Optional[str] = Field(index=True, default=None, max_length=50)
    entity_target_status: Optional[str] = Field(default=None, max_length=50)
    action: str = Field(max_length=500)
    description: str = Field(max_length=2000)
    internal_only: bool = True
    client_id: Optional[str] = Field(default=None, index=True, max_length=50)
    client_name: Optional[str] = Field(default=None, max_length=500)

class AtlasHistory(AtlasBaseModel, AtlasHistoryBase, AtlasHistoryPrimaryKey, table=True):
    pass

class AtlasHistoryReq(AtlasHistoryBase):
    pass

class AtlasHistoryRes(AtlasHistoryBase, AtlasBaseModel, AtlasHistoryPrimaryKey):
    pass