from enum import StrEnum

__all__ = [
    "SharedEnum",
    "EntityStatus",
    "UserRole",
    "AppEnum",
]

### helper values, dont remove or update, should be adding new values only

### helper values for SharedEnum
class SharedEnum(StrEnum):
    PUBLIC = "PUBLIC"
    SYSTEM = "SYSTEM"
    ALL = "ALL"
    DEF = "DEFAULT"

### helper values for EntityStatus
class EntityStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_UPDATE = "PENDING_UPDATE"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

### helper values for UserRole, this is not all possible roles, just basic ones
class UserRole(StrEnum):
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"

### helper values for UserAccess, this is not all possible access levels, just basic ones
class UserAccess(StrEnum):
    ADMIN = "ADMIN"
    EDIT = "EDIT"
    VIEW = "VIEW"

### helper values for AppEnum
class AppEnum(StrEnum):
    ATLAS_APP_IDENTITY = "ATLAS_APP_IDENTITY"
    ATLAS_APP_NETWORK = "ATLAS_APP_NETWORK"
    ATLAS_APP_BILLING = "ATLAS_APP_BILLING"