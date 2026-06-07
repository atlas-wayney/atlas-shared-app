from typing import Optional
from sqlmodel import Field, SQLModel

from .atlas_base_model import AtlasBaseModel


# this class is created to adjust table column order only..
class AtlasDocumentPrimaryKey(SQLModel):
    document_id: str = Field(primary_key=True, max_length=50)

class AtlasDocumentBase(SQLModel):
    document_name: str = Field(max_length=500)
    entity_type: str = Field(max_length=50)
    entity_id: Optional[str] = Field(index=True, default=None, max_length=50)
    client_id: Optional[str] = Field(default=None, index=True, max_length=50)
    client_name: Optional[str] = Field(default=None, max_length=500)

class AtlasDocumentFields(SQLModel):
    bucket: str = Field(max_length=500)
    fullpath: str = Field(max_length=500)
    internal_only: bool = True
    deleted: bool = False

class AtlasDocument(AtlasBaseModel, AtlasDocumentFields, AtlasDocumentBase, AtlasDocumentPrimaryKey, table=True):
    pass

class AtlasDocumentReq(AtlasDocumentBase):
    pass

class AtlasDocumentRes(AtlasBaseModel, AtlasDocumentFields, AtlasDocumentBase, AtlasDocumentPrimaryKey):
    pass
