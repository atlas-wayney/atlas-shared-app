from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AtlasDbSettings(BaseSettings):
    host_with_port: str = ""
    name: str = ""
    user: str = ""
    secret_password: SecretStr = SecretStr("")
    protocol: str = "postgresql+asyncpg://"
    echo: bool = False
    pool_size: int = 5
    pool_timeout: int = 30
    max_overflow: int = 10
