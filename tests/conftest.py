"""Pytest configuration and fixtures"""

import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import StaticPool

# Import all entities to register them with SQLModel metadata
from atlas_shared_app.entities.atlas_case import AtlasCase
from atlas_shared_app.entities.atlas_document import AtlasDocument
from atlas_shared_app.entities.atlas_history import AtlasHistory
from atlas_shared_app.entities.atlas_remark import AtlasRemark
from atlas_shared_app.entities.atlas_configs import AtlasConfigs


@pytest_asyncio.fixture(scope="function")
async def engine():
    """Create an in-memory SQLite async engine for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()