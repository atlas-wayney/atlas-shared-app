from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from ..entities.atlas_configs import AtlasConfigs


class AtlasConfigsRepository:
    """Repository class for Configs entity CRUD operations"""

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def create(self, configs: AtlasConfigs) -> AtlasConfigs:
        """Create a new config"""
        async with AsyncSession(self.engine) as session:
            session.add(configs)
            await session.commit()
            await session.refresh(configs)
            return configs

    async def get(self, entity_type: str) -> dict[str, AtlasConfigs]:
        """Get all configs for a config type as a dict keyed by field_name"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasConfigs).where(AtlasConfigs.entity_type == entity_type)
            result = await session.execute(statement)
            configs = result.scalars().all()
            return {config.field_name: config for config in configs}

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[AtlasConfigs]:
        """Get all configs"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasConfigs).offset(skip).limit(limit)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def update(self, entity_type: str, field_name: str, config_data: dict) -> Optional[AtlasConfigs]:
        """Update a config"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasConfigs).where(
                AtlasConfigs.entity_type == entity_type,
                AtlasConfigs.field_name == field_name
            )
            result = await session.execute(statement)
            configs = result.scalars().first()
            if not configs:
                return None

            for key, value in config_data.items():
                if hasattr(configs, key) and key not in ['entity_type', 'field_name']:
                    setattr(configs, key, value)

            session.add(configs)
            await session.commit()
            await session.refresh(configs)
            return configs

    async def delete(self, entity_type: str, field_name: str) -> bool:
        """Delete a config"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasConfigs).where(
                AtlasConfigs.entity_type == entity_type,
                AtlasConfigs.field_name == field_name
            )
            result = await session.execute(statement)
            configs = result.scalars().first()
            if not configs:
                return False

            await session.delete(configs)
            await session.commit()
            return True

    async def get_by_entity_type(self, entity_type: str) -> list[AtlasConfigs]:
        """Get all configs for a specific entity type"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasConfigs).where(AtlasConfigs.entity_type == entity_type)
            result = await session.execute(statement)
            return list(result.scalars().all())
