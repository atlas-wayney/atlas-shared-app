from pydantic_settings import BaseSettings


class AtlasDocumentSettings(BaseSettings):
    bucket: str = ""
    project_id: str = ""
    credentials_path: str = ""
    signed_url_expiration: int = 3600
