from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AtlasWorkflowSettings(BaseSettings):
    secret_temporal_api_key: SecretStr = SecretStr("")
    temporal_namespace: str = ""
    temporal_address: str = ""
