"""APIs module for atlas-shared-app"""

from .atlas_case_apis import register_case_apis
from .atlas_configs_apis import register_configs_apis
from .atlas_document_apis import register_document_apis
from .atlas_history_apis import register_history_apis
from .atlas_remark_apis import register_remark_apis

__all__ = [
    "register_case_apis",
    "register_configs_apis",
    "register_document_apis",
    "register_history_apis",
    "register_remark_apis",
]
