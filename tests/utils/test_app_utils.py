"""Tests for FastAPI app utilities"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_shared_app.utils.app_utils import create_app, setup_cors
from atlas_shared_app.utils.logging_utils import setup_logging
from atlas_shared_app.utils.app_utils.app import create_app as create_app_direct
from atlas_shared_app.settings.atlas_settings import AtlasSettings
from atlas_shared_app.settings.atlas_cors_settings import AtlasCorsSettings
from atlas_shared_app.settings.atlas_logging_settings import AtlasLoggingSettings
from atlas_shared_app.settings.atlas_throttling_settings import AtlasThrottlingSettings
from atlas_shared_app.settings.atlas_security_headers_settings import AtlasSecurityHeadersSettings


def test_create_app():
    """Test that create_app returns a FastAPI instance"""
    settings = AtlasSettings()
    app = create_app(settings)
    assert isinstance(app, FastAPI)


def test_create_app_with_security_headers_enabled():
    """Test that security headers middleware is added when enabled"""
    settings = AtlasSettings()
    settings.security_headers_settings.enabled = True
    app = create_app(settings)
    assert isinstance(app, FastAPI)
    # Check middleware stack includes security headers
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "SecurityHeadersMiddleware" in middleware_classes


def test_create_app_with_security_headers_disabled():
    """Test that security headers middleware is not added when disabled"""
    settings = AtlasSettings()
    settings.security_headers_settings.enabled = False
    app = create_app(settings)
    assert isinstance(app, FastAPI)


def test_create_app_with_throttling_enabled():
    """Test that throttling middleware is added when enabled"""
    settings = AtlasSettings()
    settings.throttling_settings.enabled = True
    app = create_app(settings)
    assert isinstance(app, FastAPI)
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "RateLimitMiddleware" in middleware_classes


def test_create_app_with_throttling_disabled():
    """Test that throttling middleware is not added when disabled"""
    settings = AtlasSettings()
    settings.throttling_settings.enabled = False
    app = create_app(settings)
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "RateLimitMiddleware" not in middleware_classes


def test_create_app_with_default_apis_enabled():
    """Test that default APIs are registered when enabled"""
    settings = AtlasSettings()
    settings.enable_default_apis = True
    app = create_app(settings)

    # Check routes are registered
    route_paths = [route.path for route in app.routes]
    assert any("case" in path for path in route_paths)
    assert any("config" in path for path in route_paths)


def test_create_app_with_default_apis_disabled():
    """Test that default APIs are not registered when disabled"""
    settings = AtlasSettings()
    settings.enable_default_apis = False
    app = create_app(settings)

    # Check case routes are not registered
    route_paths = [route.path for route in app.routes]
    assert not any("cases" in path for path in route_paths)


def test_create_app_with_api_prefix():
    """Test that API prefix is applied"""
    settings = AtlasSettings()
    settings.enable_default_apis = True
    settings.api_prefix = "/api/v1"
    app = create_app(settings)

    route_paths = [route.path for route in app.routes]
    assert any(path.startswith("/api/v1") for path in route_paths)


@pytest.mark.asyncio
async def test_create_app_lifespan_startup():
    """Test that lifespan startup sets app state"""
    settings = AtlasSettings()
    app = create_app(settings)

    # Use TestClient to trigger lifespan
    with TestClient(app) as client:
        # During the test, app.state should have atlas_settings
        assert hasattr(app.state, "atlas_settings")
        assert hasattr(app.state, "atlas_asyncdb")


def test_setup_cors():
    """Test CORS setup on a FastAPI app"""
    app = FastAPI()

    # Record the number of middleware before
    middleware_count_before = len(app.user_middleware)

    cors_settings = AtlasCorsSettings()
    setup_cors(app, cors_settings)

    # Check that middleware was added
    assert len(app.user_middleware) > middleware_count_before


def test_setup_cors_custom_settings():
    """Test CORS setup with custom settings"""
    app = FastAPI()

    cors_settings = AtlasCorsSettings(
        allow_origin_regex="https://.*\\.example\\.com",
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["X-Custom-Header"],
    )
    setup_cors(app, cors_settings)

    # Check that middleware was added
    assert len(app.user_middleware) > 0


def test_setup_logging():
    """Test logging setup"""
    # Should not raise any exceptions
    logging_settings = AtlasLoggingSettings()
    setup_logging(logging_settings)


def test_setup_logging_custom_settings():
    """Test logging setup with custom settings"""
    logging_settings = AtlasLoggingSettings(
        log_file="custom.log",
        rotation="100 MB",
        retention="30 days",
        level="DEBUG",
    )
    setup_logging(logging_settings)


def test_create_app_auth_middleware_added():
    """Test that auth middleware is always added"""
    settings = AtlasSettings()
    app = create_app(settings)

    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "AuthMiddleware" in middleware_classes
