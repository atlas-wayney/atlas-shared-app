from fastapi import Request
from typing import Tuple, Type

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from .sources.atlas_gcp_secret_settings_source import AtlasGcpSecretSettingsSource

from .atlas_case_settings import AtlasCaseSettings
from .atlas_cors_settings import AtlasCorsSettings
from .atlas_db_settings import AtlasDbSettings
from .atlas_document_settings import AtlasDocumentSettings
from .atlas_logging_settings import AtlasLoggingSettings
from .atlas_throttling_settings import AtlasThrottlingSettings
from .atlas_identity_settings import AtlasIdentitySettings
from .atlas_security_headers_settings import AtlasSecurityHeadersSettings
from .atlas_workflow_settings import AtlasWorkflowSettings


class AtlasSettings(BaseSettings):
    is_local: bool = False
    app_id: str = ""
    api_prefix: str = ""
    enable_default_apis: bool = True
    db_settings: AtlasDbSettings = AtlasDbSettings()
    identity_settings: AtlasIdentitySettings = AtlasIdentitySettings()
    case_settings: AtlasCaseSettings = AtlasCaseSettings()
    document_settings: AtlasDocumentSettings = AtlasDocumentSettings()
    cors_settings: AtlasCorsSettings = AtlasCorsSettings()
    logging_settings: AtlasLoggingSettings = AtlasLoggingSettings()
    throttling_settings: AtlasThrottlingSettings = AtlasThrottlingSettings()
    security_headers_settings: AtlasSecurityHeadersSettings = AtlasSecurityHeadersSettings()
    workflow_settings: AtlasWorkflowSettings = AtlasWorkflowSettings()

    # This tells pydantic to read from .env file
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore", env_nested_delimiter="__")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            file_secret_settings,
            dotenv_settings,
            AtlasGcpSecretSettingsSource(settings_cls),
        )


def get_settings(request: Request) -> AtlasSettings:
    atlas_settings: "AtlasSettings" = request.app.state.atlas_settings
    if not atlas_settings:
        raise ValueError("AtlasSettings is not initialized in app state")

    return atlas_settings

def get_identity_settings(request: Request) -> AtlasIdentitySettings:
    atlas_settings: "AtlasSettings" = request.app.state.atlas_settings
    if not atlas_settings:
        raise ValueError("AtlasSettings is not initialized in app state")

    if not atlas_settings.identity_settings:
        raise ValueError("AtlasIdentitySettings is not initialized properly")

    return atlas_settings.identity_settings


def get_case_settings(request: Request) -> AtlasCaseSettings:
    atlas_settings: "AtlasSettings" = request.app.state.atlas_settings
    if not atlas_settings:
        raise ValueError("AtlasSettings is not initialized in app state")

    if not atlas_settings.case_settings:
        raise ValueError("AtlasCaseSettings is not initialized properly")

    return atlas_settings.case_settings

def get_document_settings(request: Request) -> AtlasDocumentSettings:
    atlas_settings: "AtlasSettings" = request.app.state.atlas_settings
    if not atlas_settings:
        raise ValueError("AtlasSettings is not initialized in app state")

    if not atlas_settings.document_settings:
        raise ValueError("AtlasDocumentSettings is not initialized properly")

    return atlas_settings.document_settings

def get_workflow_settings(request: Request) -> AtlasWorkflowSettings:
    atlas_settings: "AtlasSettings" = request.app.state.atlas_settings
    if not atlas_settings:
        raise ValueError("AtlasSettings is not initialized in app state")

    if not atlas_settings.workflow_settings:
        raise ValueError("AtlasWorkflowSettings is not initialized properly")

    return atlas_settings.workflow_settings

