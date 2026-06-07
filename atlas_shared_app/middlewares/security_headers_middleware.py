from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..settings.atlas_security_headers_settings import AtlasSecurityHeadersSettings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for adding security headers to all responses.

    This middleware adds security headers required for penetration testing compliance,
    including HSTS, CSP, X-Frame-Options, and other OWASP recommended headers.
    """

    def __init__(
        self,
        app,
        settings: AtlasSecurityHeadersSettings,
    ):
        """
        Initialize the security headers middleware.

        Args:
            app: The FastAPI application
            settings: Security headers settings containing header configuration
        """
        super().__init__(app)
        self.settings = settings
        self._headers, self._csp_header = self._build_headers()

    def _build_headers(self) -> tuple[dict[str, str], str | None]:
        """
        Pre-build all security headers for performance.

        Returns:
            Tuple of (headers dict, CSP header value or None)
        """
        headers = {}
        csp_header = None

        # Strict-Transport-Security (HSTS)
        hsts_value = self.settings.build_hsts_header()
        if hsts_value:
            headers["Strict-Transport-Security"] = hsts_value

        # X-Content-Type-Options
        if self.settings.x_content_type_options:
            headers["X-Content-Type-Options"] = self.settings.x_content_type_options

        # X-Frame-Options
        if self.settings.x_frame_options:
            headers["X-Frame-Options"] = self.settings.x_frame_options

        # X-XSS-Protection (legacy but expected by some pen tests)
        if self.settings.x_xss_protection:
            headers["X-XSS-Protection"] = self.settings.x_xss_protection

        # Content-Security-Policy (stored separately for path-based skipping)
        csp_header = self.settings.build_csp_header()

        # Referrer-Policy
        if self.settings.referrer_policy:
            headers["Referrer-Policy"] = self.settings.referrer_policy

        # Permissions-Policy
        if self.settings.permissions_policy:
            headers["Permissions-Policy"] = self.settings.permissions_policy

        # Cache-Control
        if self.settings.cache_control:
            headers["Cache-Control"] = self.settings.cache_control

        # Pragma
        if self.settings.pragma:
            headers["Pragma"] = self.settings.pragma

        # Cross-Origin-Opener-Policy
        if self.settings.cross_origin_opener_policy:
            headers["Cross-Origin-Opener-Policy"] = self.settings.cross_origin_opener_policy

        # Cross-Origin-Embedder-Policy
        if self.settings.cross_origin_embedder_policy:
            headers["Cross-Origin-Embedder-Policy"] = self.settings.cross_origin_embedder_policy

        # Cross-Origin-Resource-Policy
        if self.settings.cross_origin_resource_policy:
            headers["Cross-Origin-Resource-Policy"] = self.settings.cross_origin_resource_policy

        return headers, csp_header

    def _should_skip_csp(self, path: str) -> bool:
        """
        Check if CSP should be skipped for the given path.

        Args:
            path: The request path

        Returns:
            True if CSP should be skipped
        """
        # Skip CSP for Swagger/OpenAPI docs (needs inline scripts/styles)
        return path.startswith("/docs") or path.startswith("/openapi.json")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add security headers to the response.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response with security headers added
        """
        response = await call_next(request)

        # Add all pre-built security headers
        for header_name, header_value in self._headers.items():
            response.headers[header_name] = header_value

        # Add CSP header unless path should skip it
        if self._csp_header and not self._should_skip_csp(request.url.path):
            response.headers["Content-Security-Policy"] = self._csp_header

        return response
