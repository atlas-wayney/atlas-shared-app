from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from ..entities.atlas_remark import AtlasRemark


class AtlasRemarkRepository:
    """Repository class for Remark entity CRUD operations"""

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def create(self, remark: AtlasRemark) -> AtlasRemark:
        """Create a new remark"""
        async with AsyncSession(self.engine) as session:
            session.add(remark)
            await session.commit()
            await session.refresh(remark)
            return remark

    async def get_by_id(self, remark_id: str) -> Optional[AtlasRemark]:
        """Get a remark by ID"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasRemark).where(AtlasRemark.remark_id == remark_id)
            result = await session.execute(statement)
            return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100, client_id: Optional[str] = None) -> list[AtlasRemark]:
        """Get all remarks with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasRemark)
            if client_id is not None:
                statement = statement.where(AtlasRemark.client_id == client_id)
            statement = statement.offset(skip).limit(limit)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def update(self, remark_id: str, remark_data: dict) -> Optional[AtlasRemark]:
        """Update a remark"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasRemark).where(AtlasRemark.remark_id == remark_id)
            result = await session.execute(statement)
            remark = result.scalars().first()
            if not remark:
                return None

            for key, value in remark_data.items():
                if hasattr(remark, key):
                    setattr(remark, key, value)

            session.add(remark)
            await session.commit()
            await session.refresh(remark)
            return remark

    async def delete(self, remark_id: str) -> bool:
        """Delete a remark"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasRemark).where(AtlasRemark.remark_id == remark_id)
            result = await session.execute(statement)
            remark = result.scalars().first()
            if not remark:
                return False

            await session.delete(remark)
            await session.commit()
            return True

    async def get_by_entity_id(self, entity_id: str, client_id: Optional[str] = None) -> list[AtlasRemark]:
        """Get all remarks for a specific entity with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasRemark).where(AtlasRemark.entity_id == entity_id)
            if client_id is not None:
                statement = statement.where(AtlasRemark.client_id == client_id)
            result = await session.execute(statement)
            return list(result.scalars().all())
