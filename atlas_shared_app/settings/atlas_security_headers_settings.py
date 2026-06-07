from pydantic_settings import BaseSettings


class AtlasSecurityHeadersSettings(BaseSettings):
    """
    Settings for security headers middleware.

    These headers comply with common penetration testing standards including OWASP.
    """

    enabled: bool = True

    # HSTS (Strict-Transport-Security)
    hsts_enabled: bool = True
    hsts_max_age: int = 63072000  # 2 years in seconds
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False

    # Content-Type Options
    x_content_type_options: str = "nosniff"

    # Frame Options (clickjacking protection)
    x_frame_options: str = "DENY"

    # XSS Protection (legacy but still expected by some pen tests)
    x_xss_protection: str = "1; mode=block"

    # Content Security Policy
    csp_enabled: bool = True
    csp_default_src: str = "'self'"
    csp_script_src: str = "'self'"
    csp_style_src: str = "'self' 'unsafe-inline'"
    csp_img_src: str = "'self' data:"
    csp_font_src: str = "'self'"
    csp_connect_src: str = "'self'"
    csp_frame_ancestors: str = "'none'"
    csp_form_action: str = "'self'"
    csp_base_uri: str = "'self'"
    csp_object_src: str = "'none'"

    # Referrer Policy
    referrer_policy: str = "strict-origin-when-cross-origin"

    # Permissions Policy (formerly Feature-Policy)
    permissions_policy: str = "geolocation=(), microphone=(), camera=(), payment=()"

    # Cache Control for sensitive responses
    cache_control: str = "no-store, no-cache, must-revalidate, private"
    pragma: str = "no-cache"

    # Cross-Origin policies
    cross_origin_opener_policy: str = "same-origin"
    cross_origin_embedder_policy: str = "require-corp"
    cross_origin_resource_policy: str = "same-origin"

    def build_csp_header(self) -> str:
        """Build the Content-Security-Policy header value."""
        if not self.csp_enabled:
            return ""

        directives = [
            f"default-src {self.csp_default_src}",
            f"script-src {self.csp_script_src}",
            f"style-src {self.csp_style_src}",
            f"img-src {self.csp_img_src}",
            f"font-src {self.csp_font_src}",
            f"connect-src {self.csp_connect_src}",
            f"frame-ancestors {self.csp_frame_ancestors}",
            f"form-action {self.csp_form_action}",
            f"base-uri {self.csp_base_uri}",
            f"object-src {self.csp_object_src}",
        ]
        return "; ".join(directives)

    def build_hsts_header(self) -> str:
        """Build the Strict-Transport-Security header value."""
        if not self.hsts_enabled:
            return ""

        parts = [f"max-age={self.hsts_max_age}"]
        if self.hsts_include_subdomains:
            parts.append("includeSubDomains")
        if self.hsts_preload:
            parts.append("preload")
        return "; ".join(parts)