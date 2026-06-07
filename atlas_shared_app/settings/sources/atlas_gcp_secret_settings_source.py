from loguru import logger
from typing import Any, Dict, Tuple, Type

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
)

class AtlasGcpSecretSettingsSource(PydanticBaseSettingsSource):

    def get_field_value(
        self, field: FieldInfo, field_name: str, parent_key: str = ""
    ) -> Tuple[Any, str, bool]:
        field_key = parent_key + "__" + field_name if parent_key else field_name

        # Check if this is a nested BaseSettings model
        if self._is_nested_settings(field) and field.annotation is not None:
            return self._process_model_fields(field.annotation, parent_key=field_key), field_name, False

        # Only process secret_ prefixed fields
        if not field_name.startswith("secret_"):
            return None, field_name, False

        # TODO: need to fetch value from GCP Secret Manager here and return it
        logger.debug(f"Fetching secret for key: {field_key}")
        return None, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def _is_nested_settings(self, field: FieldInfo) -> bool:
        """Check if a field's annotation is a BaseSettings subclass."""
        annotation = field.annotation
        try:
            return isinstance(annotation, type) and issubclass(annotation, BaseSettings)
        except TypeError:
            return False

    def _process_model_fields(self, model_cls: Type[BaseSettings], parent_key: str = "") -> Dict[str, Any]:
        """Recursively process fields of a model."""
        d: Dict[str, Any] = {}

        for field_name, field in model_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name, parent_key
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d

    def __call__(self) -> Dict[str, Any]:
        return self._process_model_fields(self.settings_cls, parent_key=self._current_state.get('app_id') or "")
