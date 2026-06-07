from typing import List, Optional
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from pydantic import field_validator

from .atlas_base_enums import AppEnum, EntityStatus, UserRole
from .atlas_base_model import AtlasBaseModel


# this class is created to adjust table column order only..
class AtlasUserPrimaryKey(SQLModel):
    user_id: str = Field(primary_key=True, max_length=50)

class AtlasUserBase(SQLModel):
    login_id: str = Field(max_length=50)
    user_name: str = Field(max_length=500)
    user_status: str = Field(default=EntityStatus.DRAFT, max_length=50)
    email: str = Field(max_length=500)
    phone: str = Field(max_length=500)
    internal: bool = True
    client_id: Optional[str] = Field(default=None, index=True, max_length=50)
    client_name: Optional[str] = Field(default=None, max_length=500)
    roles: dict[AppEnum, str] = Field(sa_column=Column(JSON))

    @field_validator('roles', mode='before')
    @classmethod
    def convert_roles_keys_to_enum(cls, v):
        """Convert string keys to AppEnum to avoid serialization warnings."""
        if v is None:
            return {}
        return {AppEnum(k) if isinstance(k, str) else k: val for k, val in v.items()}

# leave this table to atlas-app-identity
class AtlasUser(AtlasBaseModel, AtlasUserBase, AtlasUserPrimaryKey, table=False):
    pass

class AtlasUserReq(AtlasUserBase):
    pass

class AtlasUserRes(AtlasUserBase, AtlasBaseModel, AtlasUserPrimaryKey):
    scopes: dict[AppEnum, list[str]] = {} # roles mapped to scopes

    @field_validator('scopes', mode='before')
    @classmethod
    def convert_scopes_keys_to_enum(cls, v):
        """Convert string keys to AppEnum to avoid serialization warnings."""
        if v is None:
            return {}
        return {AppEnum(k) if isinstance(k, str) else k: val for k, val in v.items()}
