from pydantic_settings import BaseSettings


class AtlasThrottlingSettings(BaseSettings):
    enabled: bool = False
    global_limit_per_second: int = 1000
    ip_limit_per_second: int = 100