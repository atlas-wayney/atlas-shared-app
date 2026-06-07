from sqlmodel import Field, Column, SQLModel
from sqlalchemy import JSON

from .atlas_base_model import AtlasBaseModel

class AtlasConfigsBase(SQLModel):
    entity_type: str = Field(primary_key=True, max_length=50)
    field_name: str = Field(primary_key=True, max_length=500)
    options: dict[str, str] = Field(sa_column=Column(JSON))

class AtlasConfigs(AtlasBaseModel, AtlasConfigsBase, table=True):
    pass

class AtlasConfigsReq(AtlasConfigsBase):
    pass

class AtlasConfigsRes(AtlasConfigsBase, AtlasBaseModel):
    pass
