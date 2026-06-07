"""Tests for security headers middleware"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from starlette.requests import Request
from starlette.responses import Response

from atlas_shared_app.middlewares.security_headers_middleware import SecurityHeadersMiddleware
from atlas_shared_app.settings.atlas_security_headers_settings import AtlasSecurityHeadersSettings


@pytest.fixture
def mock_app():
    """Create a mock app"""
    return MagicMock()


@pytest.fixture
def default_settings():
    """Create default security headers settings"""
    return AtlasSecurityHeadersSettings()


@pytest.fixture
def disabled_settings():
    """Create settings with security headers disabled"""
    return AtlasSecurityHeadersSettings(enabled=False)


@pytest.fixture
def custom_settings():
    """Create custom security headers settings"""
    return AtlasSecurityHeadersSettings(
        hsts_max_age=86400,
        hsts_include_subdomains=False,
        hsts_preload=True,
        x_frame_options="SAMEORIGIN",
        csp_default_src="'self' https://example.com",
        referrer_policy="no-referrer",
    )


@pytest.fixture
def mock_request():
    """Create a mock request"""
    request = MagicMock(spec=Request)
    request.url = MagicMock()
    request.url.path = "/api/test"
    return request


def test_middleware_init(mock_app, default_settings):
    """Test SecurityHeadersMiddleware initialization"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware.settings is not None
    assert middleware._headers is not None
    assert len(middleware._headers) > 0


def test_middleware_builds_hsts_header(mock_app, default_settings):
    """Test that HSTS header is built correctly"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert "Strict-Transport-Security" in middleware._headers
    hsts_value = middleware._headers["Strict-Transport-Security"]
    assert "max-age=63072000" in hsts_value
    assert "includeSubDomains" in hsts_value


def test_middleware_hsts_with_preload(mock_app):
    """Test HSTS header with preload enabled"""
    settings = AtlasSecurityHeadersSettings(hsts_preload=True)
    middleware = SecurityHeadersMiddleware(mock_app, settings)
    hsts_value = middleware._headers["Strict-Transport-Security"]
    assert "preload" in hsts_value


def test_middleware_hsts_disabled(mock_app):
    """Test that HSTS header is not added when disabled"""
    settings = AtlasSecurityHeadersSettings(hsts_enabled=False)
    middleware = SecurityHeadersMiddleware(mock_app, settings)
    assert "Strict-Transport-Security" not in middleware._headers


def test_middleware_builds_csp_header(mock_app, default_settings):
    """Test that CSP header is built correctly"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware._csp_header is not None
    assert "default-src 'self'" in middleware._csp_header
    assert "frame-ancestors 'none'" in middleware._csp_header


def test_middleware_csp_disabled(mock_app):
    """Test that CSP header is not added when disabled"""
    settings = AtlasSecurityHeadersSettings(csp_enabled=False)
    middleware = SecurityHeadersMiddleware(mock_app, settings)
    assert not middleware._csp_header  # Empty string or None


def test_middleware_x_frame_options(mock_app, default_settings):
    """Test X-Frame-Options header"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware._headers["X-Frame-Options"] == "DENY"


def test_middleware_x_content_type_options(mock_app, default_settings):
    """Test X-Content-Type-Options header"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware._headers["X-Content-Type-Options"] == "nosniff"


def test_middleware_x_xss_protection(mock_app, default_settings):
    """Test X-XSS-Protection header"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware._headers["X-XSS-Protection"] == "1; mode=block"


def test_middleware_referrer_policy(mock_app, default_settings):
    """Test Referrer-Policy header"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware._headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_middleware_permissions_policy(mock_app, default_settings):
    """Test Permissions-Policy header"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert "Permissions-Policy" in middleware._headers
    assert "geolocation=()" in middleware._headers["Permissions-Policy"]


def test_middleware_cache_control(mock_app, default_settings):
    """Test Cache-Control header"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware._headers["Cache-Control"] == "no-store, no-cache, must-revalidate, private"
    assert middleware._headers["Pragma"] == "no-cache"


def test_middleware_cross_origin_policies(mock_app, default_settings):
    """Test Cross-Origin policy headers"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)
    assert middleware._headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert middleware._headers["Cross-Origin-Embedder-Policy"] == "require-corp"
    assert middleware._headers["Cross-Origin-Resource-Policy"] == "same-origin"


def test_custom_settings_applied(mock_app, custom_settings):
    """Test that custom settings are applied correctly"""
    middleware = SecurityHeadersMiddleware(mock_app, custom_settings)
    assert middleware._headers["X-Frame-Options"] == "SAMEORIGIN"
    assert middleware._headers["Referrer-Policy"] == "no-referrer"
    hsts_value = middleware._headers["Strict-Transport-Security"]
    assert "max-age=86400" in hsts_value
    assert "includeSubDomains" not in hsts_value
    assert "preload" in hsts_value


@pytest.mark.asyncio
async def test_dispatch_adds_headers(mock_app, default_settings, mock_request):
    """Test that dispatch adds security headers to response"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)

    original_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=original_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 200
    assert response.headers.get("Strict-Transport-Security") is not None
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Content-Security-Policy") is not None
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_dispatch_preserves_existing_headers(mock_app, default_settings, mock_request):
    """Test that dispatch preserves existing response headers"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)

    original_response = Response(content="OK", status_code=200)
    original_response.headers["X-Custom-Header"] = "custom-value"
    call_next = AsyncMock(return_value=original_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.headers.get("X-Custom-Header") == "custom-value"
    assert response.headers.get("Strict-Transport-Security") is not None


@pytest.mark.asyncio
async def test_dispatch_with_error_response(mock_app, default_settings, mock_request):
    """Test that dispatch adds headers even on error responses"""
    middleware = SecurityHeadersMiddleware(mock_app, default_settings)

    error_response = Response(content="Error", status_code=500)
    call_next = AsyncMock(return_value=error_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 500
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


class TestAtlasSecurityHeadersSettings:
    """Tests for AtlasSecurityHeadersSettings"""

    def test_default_values(self):
        """Test default settings values"""
        settings = AtlasSecurityHeadersSettings()
        assert settings.enabled is True
        assert settings.hsts_enabled is True
        assert settings.hsts_max_age == 63072000
        assert settings.hsts_include_subdomains is True
        assert settings.hsts_preload is False
        assert settings.x_content_type_options == "nosniff"
        assert settings.x_frame_options == "DENY"
        assert settings.csp_enabled is True

    def test_build_hsts_header_default(self):
        """Test building HSTS header with defaults"""
        settings = AtlasSecurityHeadersSettings()
        hsts = settings.build_hsts_header()
        assert hsts == "max-age=63072000; includeSubDomains"

    def test_build_hsts_header_with_preload(self):
        """Test building HSTS header with preload"""
        settings = AtlasSecurityHeadersSettings(hsts_preload=True)
        hsts = settings.build_hsts_header()
        assert "preload" in hsts

    def test_build_hsts_header_disabled(self):
        """Test building HSTS header when disabled"""
        settings = AtlasSecurityHeadersSettings(hsts_enabled=False)
        hsts = settings.build_hsts_header()
        assert hsts == ""

    def test_build_csp_header(self):
        """Test building CSP header"""
        settings = AtlasSecurityHeadersSettings()
        csp = settings.build_csp_header()
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "object-src 'none'" in csp

    def test_build_csp_header_disabled(self):
        """Test building CSP header when disabled"""
        settings = AtlasSecurityHeadersSettings(csp_enabled=False)
        csp = settings.build_csp_header()
        assert csp == ""

    def test_custom_csp_values(self):
        """Test custom CSP values"""
        settings = AtlasSecurityHeadersSettings(
            csp_default_src="'self' https://cdn.example.com",
            csp_script_src="'self' 'unsafe-inline'",
        )
        csp = settings.build_csp_header()
        assert "default-src 'self' https://cdn.example.com" in csp
        assert "script-src 'self' 'unsafe-inline'" in csp
