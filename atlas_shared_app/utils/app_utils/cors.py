from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ...settings import AtlasCorsSettings


def setup_cors(app: FastAPI, settings: AtlasCorsSettings):
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=settings.allow_origin_regex,
        allow_credentials=settings.allow_credentials,
        allow_methods=settings.allow_methods,
        allow_headers=settings.allow_headers,
    )
