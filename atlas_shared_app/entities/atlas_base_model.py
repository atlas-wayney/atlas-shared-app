from abc import ABC
from sqlalchemy import func
from sqlmodel import Field, SQLModel
from datetime import datetime

class AtlasBaseRes(SQLModel):
    detail: str = Field(max_length=500)

class AtlasEntity(SQLModel, ABC):
    id: str = Field(max_length=50)
    name: str = Field(max_length=500)

class AtlasBaseModel(SQLModel, ABC):
    create_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs=dict(server_default=func.now()))
    creater_id: str = Field(max_length=50)
    creater_name: str = Field(max_length=500)
    update_time: datetime = Field(default_factory=datetime.now, sa_column_kwargs=dict(server_default=func.now(), onupdate=func.now()))
    updater_id: str = Field(max_length=50)
    updater_name: str = Field(max_length=500)

class AtlasEntityStatusReq(SQLModel):
    entity_type: str = Field(max_length=50)
    entity_id: str = Field(max_length=50)
    status: str = Field(max_length=50)
    remark: str = Field(max_length=2000)
