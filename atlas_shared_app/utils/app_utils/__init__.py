"""FastAPI application utilities for atlas-shared-app

The create_app function is the recommended way to create a FastAPI application
with atlas-shared-app. It provides:
- CORS setup
- Logging configuration
- Optional rate limiting
- Optional automatic API registration for Case and Configs

Example:
    >>> async def get_engine():
    ...     return your_async_engine
    >>>
    >>> app = create_app(
    ...     register_case_apis=True,
    ...     register_configs_apis=True,
    ...     get_engine=get_engine
    ... )
"""

from .app import create_app
from .cors import setup_cors
from .rate_limiter import setup_throttling
from .security import verify_user

__all__ = ["create_app", "setup_cors", "setup_throttling", "verify_user"]