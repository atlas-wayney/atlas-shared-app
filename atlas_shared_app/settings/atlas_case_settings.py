from pydantic_settings import BaseSettings
from sqlmodel import SQLModel


class AtlasCaseSettings(BaseSettings):
    case_types: dict[str, type[SQLModel]] = {}
