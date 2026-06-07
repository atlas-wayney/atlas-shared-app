
from typing import Optional, Callable, Awaitable
from fastapi import Request
from loguru import logger

from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from ..settings import AtlasDbSettings


async def get_engine(request: Request) -> AsyncEngine:
    atlas_asyncdb: AtlasAsyncdb = request.app.state.atlas_asyncdb
    if not atlas_asyncdb:
        logger.error("AtlasAsyncdb is not initialized in app state")
        raise ValueError("AtlasAsyncdb is not initialized in app state")

    engine = await atlas_asyncdb.get_engine()
    if not engine:
        logger.error("AsyncEngine is not initialized properly")
        raise ValueError("AsyncEngine is not initialized properly")

    return engine


async def get_engine_from_settings(db_settings: AtlasDbSettings):
    atlas_asyncdb = AtlasAsyncdb(
        db_settings=db_settings,
    )

    engine = await atlas_asyncdb.get_engine()
    if not engine:
        logger.error("AsyncEngine is not initialized properly")
        raise ValueError("AsyncEngine is not initialized properly")

    return engine


class AtlasAsyncdb:
    def __init__(
        self,
        db_settings: AtlasDbSettings,
    ):
        self.db_settings = db_settings
        self.engine: Optional[AsyncEngine] = None

    async def init_db(self):
        logger.info("Initializing database connection pool")
        await self.dispose()

        logger.debug(
            "Database config: host={}, name={}, pool_size={}, max_overflow={}",
            self.db_settings.host_with_port,
            self.db_settings.name,
            self.db_settings.pool_size,
            self.db_settings.max_overflow
        )

        connection_string = f"{self.db_settings.protocol}{self.db_settings.user}:{self.db_settings.secret_password.get_secret_value()}@{self.db_settings.host_with_port}/{self.db_settings.name}"
        engine = create_async_engine(
            connection_string,
            echo=self.db_settings.echo,
            pool_size=self.db_settings.pool_size,
            pool_timeout=self.db_settings.pool_timeout,
            max_overflow=self.db_settings.max_overflow,
        )

        self.engine = engine
        logger.info("Database connection pool initialized successfully")

    async def dispose(self):
        if self.engine:
            logger.info("Disposing database connection pool")
            await self.engine.dispose()
            self.engine = None
            logger.debug("Database connection pool disposed")

    async def get_engine(self) -> Optional[AsyncEngine]:
        if not self.engine:
            await self.init_db()

        # Try to create a session and test the connection
        try:
            # Test the connection by executing a simple query
            if self.engine:
                self.engine.connect()
            return self.engine
        except (OperationalError, DatabaseError) as e:
            # Database error (possibly wrong password) - reinitialize and retry once
            logger.warning("Database connection error, attempting reconnect: {}", str(e))
            try:
                await self.init_db()
                if self.engine:
                    self.engine.connect()
                logger.info("Database reconnection successful")
                return self.engine
            except (OperationalError, DatabaseError):
                logger.error("Database reconnection failed: {}", str(e))
                # Re-raise the original error if retry fails
                raise e