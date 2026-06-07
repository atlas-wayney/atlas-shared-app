from contextlib import asynccontextmanager
from typing import Optional
from loguru import logger

from fastapi import FastAPI
from starlette.types import Lifespan

from atlas_shared_app.database.atlas_asyncdb import AtlasAsyncdb

from .cors import setup_cors
from .rate_limiter import setup_throttling
from ..logging_utils import setup_logging
from ...middlewares import AuthMiddleware, RequestContextMiddleware, SecurityHeadersMiddleware
from ...settings.atlas_settings import AtlasSettings

def create_app(
    settings: AtlasSettings
) -> FastAPI:
    """
    Create a FastAPI application with middleware and API registration.

    Args:
        settings: AtlasSettings configuration

    Returns:
        Configured FastAPI application
    """

    setup_logging(settings.logging_settings, settings.is_local)

    logger.info("Application settings loaded: {}", settings.model_dump())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # startup
        logger.info("Application starting up...")
        app.state.atlas_settings = settings
        app.state.atlas_asyncdb = AtlasAsyncdb(
            db_settings=settings.db_settings,
        )
        logger.info("Application startup complete")

        yield

        # shutdown
        logger.info("Application shutting down...")
        app.state.atlas_settings = None
        if app.state.atlas_asyncdb:
            await app.state.atlas_asyncdb.dispose()
        app.state.atlas_asyncdb = None
        logger.info("Application shutdown complete")


    app = FastAPI(lifespan=lifespan)

    # Middleware execution order: later added = outer = runs first on request
    # RequestContextMiddleware needs user info from AuthMiddleware, so add it first (inner)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(AuthMiddleware, settings=settings.identity_settings)

    if settings.security_headers_settings.enabled:
        app.add_middleware(
            SecurityHeadersMiddleware,
            settings=settings.security_headers_settings,
        )

    setup_cors(app, settings.cors_settings)

    if settings.throttling_settings.enabled:
        setup_throttling(app, settings.throttling_settings)

    if settings.enable_default_apis:
        from ...apis import (
            register_case_apis,
            register_configs_apis,
            register_document_apis,
            register_history_apis,
            register_remark_apis,
        )
        register_case_apis(app, settings.api_prefix)
        register_configs_apis(app, settings.api_prefix)
        register_document_apis(app, settings.api_prefix)
        register_history_apis(app, settings.api_prefix)
        register_remark_apis(app, settings.api_prefix)

    return app
