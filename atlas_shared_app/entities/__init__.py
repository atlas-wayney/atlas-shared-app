"""Entities module"""

from .atlas_base_model import AtlasBaseModel, AtlasEntity, AtlasEntityStatusReq, AtlasBaseRes
from .atlas_base_enums import AppEnum, EntityStatus, SharedEnum, UserRole, UserAccess
from .atlas_case import AtlasCase, AtlasCaseBase, AtlasCaseReq, AtlasCaseRes, AtlasCaseStatus, AtlasCaseStatusBase, AtlasCaseStatusReq, AtlasCaseWorkflowEntity, AtlasCaseWorkflowResultEntity
from .atlas_document import AtlasDocument, AtlasDocumentBase, AtlasDocumentReq, AtlasDocumentRes
from .atlas_history import AtlasHistory, AtlasHistoryBase, AtlasHistoryReq, AtlasHistoryRes
from .atlas_remark import AtlasRemark, AtlasRemarkBase, AtlasRemarkReq, AtlasRemarkRes
from .atlas_configs import AtlasConfigs, AtlasConfigsBase, AtlasConfigsReq, AtlasConfigsRes
from .atlas_user import AtlasUser, AtlasUserBase, AtlasUserReq, AtlasUserRes
from .atlas_subclient import AtlasSubclient, AtlasSubclientBase, AtlasSubclientReq, AtlasSubclientRes
from .atlas_client import AtlasClient, AtlasClientBase, AtlasClientReq, AtlasClientRes

__all__ = [
    # Base model
    "AtlasBaseModel",
    "AtlasEntity",
    "AtlasEntityStatusReq",
    "AtlasBaseRes",
    "AppEnum",
    "EntityStatus",
    "SharedEnum",
    "UserRole",
    "UserAccess",
    # Case entities
    "AtlasCase",
    "AtlasCaseBase",
    "AtlasCaseReq",
    "AtlasCaseRes",
    "AtlasCaseStatus",
    "AtlasCaseStatusBase",
    "AtlasCaseStatusReq",
    "AtlasCaseWorkflowEntity",
    "AtlasCaseWorkflowResultEntity",
    # Document entities
    "AtlasDocument",
    "AtlasDocumentBase",
    "AtlasDocumentReq",
    "AtlasDocumentRes",
    # History entities
    "AtlasHistory",
    "AtlasHistoryBase",
    "AtlasHistoryReq",
    "AtlasHistoryRes",
    # Remark entities
    "AtlasRemark",
    "AtlasRemarkBase",
    "AtlasRemarkReq",
    "AtlasRemarkRes",
    # Configs entities
    "AtlasConfigs",
    "AtlasConfigsBase",
    "AtlasConfigsReq",
    "AtlasConfigsRes",
    # User entities
    "AtlasUser",
    "AtlasUserBase",
    "AtlasUserReq",
    "AtlasUserRes",
    # Subclient entities
    "AtlasSubclient",
    "AtlasSubclientBase",
    "AtlasSubclientReq",
    "AtlasSubclientRes",
    # Client entities
    "AtlasClient",
    "AtlasClientBase",
    "AtlasClientReq",
    "AtlasClientRes",
]
