from pydantic_settings import BaseSettings


class AtlasCorsSettings(BaseSettings):
    allow_origin_regex: str = r'https://.*\.(atlas|qaatlas)\.com'
    allow_credentials: bool = False
    allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers: list[str] = ["*"]