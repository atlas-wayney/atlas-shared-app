from datetime import datetime
from typing import List
from sqlmodel import Field, Column, SQLModel
from sqlalchemy import JSON

from .atlas_base_enums import AppEnum, EntityStatus
from .atlas_base_model import AtlasBaseModel

# this class is created to adjust table column order only..
class AtlasClientPrimaryKey(SQLModel):
    client_id: str = Field(primary_key=True, max_length=50)

### same as company, business entity etc.
class AtlasClientBase(SQLModel):
    client_name: str = Field(max_length=500)
    client_status: str = Field(default=EntityStatus.DRAFT, max_length=50)
    supported_email_domains: list[str] = Field(sa_column=Column(JSON))
    allowed_apps: List[AppEnum] = Field(sa_column=Column(JSON))
    tags: list[str] = Field(sa_column=Column(JSON))
    terms_acceptances: dict[str, datetime] = Field(default_factory=dict, sa_column=Column(JSON))

# leave this table to atlas-app-identity
class AtlasClient(AtlasBaseModel, AtlasClientBase, AtlasClientPrimaryKey, table=False):
    pass

class AtlasClientReq(AtlasClientBase):
    pass

class AtlasClientRes(AtlasClientBase, AtlasBaseModel, AtlasClientPrimaryKey):
    pass
