from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from ..entities.atlas_history import AtlasHistory


class AtlasHistoryRepository:
    """Repository class for History entity CRUD operations"""

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def create(self, history: AtlasHistory) -> AtlasHistory:
        """Create a new history entry"""
        async with AsyncSession(self.engine) as session:
            session.add(history)
            await session.commit()
            await session.refresh(history)
            return history

    async def get_by_id(self, history_id: str) -> Optional[AtlasHistory]:
        """Get a history entry by ID"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasHistory).where(AtlasHistory.history_id == history_id)
            result = await session.execute(statement)
            return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100, client_id: Optional[str] = None) -> list[AtlasHistory]:
        """Get all history entries with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasHistory)
            if client_id is not None:
                statement = statement.where(AtlasHistory.client_id == client_id)
            statement = statement.offset(skip).limit(limit)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def update(self, history_id: str, history_data: dict) -> Optional[AtlasHistory]:
        """Update a history entry"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasHistory).where(AtlasHistory.history_id == history_id)
            result = await session.execute(statement)
            history = result.scalars().first()
            if not history:
                return None

            for key, value in history_data.items():
                if hasattr(history, key):
                    setattr(history, key, value)

            session.add(history)
            await session.commit()
            await session.refresh(history)
            return history

    async def delete(self, history_id: str) -> bool:
        """Delete a history entry"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasHistory).where(AtlasHistory.history_id == history_id)
            result = await session.execute(statement)
            history = result.scalars().first()
            if not history:
                return False

            await session.delete(history)
            await session.commit()
            return True

    async def get_by_entity_id(self, entity_id: str, client_id: Optional[str] = None) -> list[AtlasHistory]:
        """Get all history entries for a specific entity with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasHistory).where(AtlasHistory.entity_id == entity_id)
            if client_id is not None:
                statement = statement.where(AtlasHistory.client_id == client_id)
            result = await session.execute(statement)
            return list(result.scalars().all())
