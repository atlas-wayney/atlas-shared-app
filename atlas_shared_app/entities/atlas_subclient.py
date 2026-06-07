from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON

from .atlas_base_enums import EntityStatus
from .atlas_base_model import AtlasBaseModel

# this class is created to adjust table column order only..
class AtlasSubclientPrimaryKey(SQLModel):
    subclient_id: str = Field(primary_key=True, max_length=50)

### same as company, business entity etc.
class AtlasSubclientBase(SQLModel):
    subclient_name: str = Field(max_length=500)
    subclient_status: str = Field(default=EntityStatus.DRAFT, max_length=50)
    parent_subclient_id: str = Field(index=True, max_length=50)
    client_id: str = Field(index=True, max_length=50)
    client_name: str = Field(max_length=500)
    country: str = Field(max_length=500)
    region: str = Field(max_length=500)
    tags: list[str] = Field(sa_column=Column(JSON))

# leave this table to atlas-app-identity
class AtlasSubclient(AtlasBaseModel, AtlasSubclientBase, AtlasSubclientPrimaryKey, table=False):
    pass

class AtlasSubclientReq(AtlasSubclientBase):
    pass

class AtlasSubclientRes(AtlasSubclientBase, AtlasBaseModel, AtlasSubclientPrimaryKey):
    pass
