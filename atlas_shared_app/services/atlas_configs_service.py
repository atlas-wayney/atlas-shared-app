from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine

from ..entities.atlas_configs import AtlasConfigs, AtlasConfigsBase
from ..entities.atlas_history import AtlasHistoryBase
from ..entities.atlas_user import AtlasUserRes
from ..repositories.atlas_configs_repository import AtlasConfigsRepository


class AtlasConfigsService:
    """Service class for Configs entity business logic"""

    def __init__(self, engine: AsyncEngine):
        self.repository = AtlasConfigsRepository(engine)

    async def create(
        self,
        configs: AtlasConfigsBase,
        curr_user: AtlasUserRes
    ) -> AtlasConfigs:
        """Create a new config (composite key: entity_type + field_name)"""
        new_configs = AtlasConfigs(
            **configs.model_dump(),
            creater_id=curr_user.user_id,
            creater_name=curr_user.user_name,
            updater_id=curr_user.user_id,
            updater_name=curr_user.user_name
        )
        created_config = await self.repository.create(new_configs)

        # Log history
        from ..services.atlas_history_service import AtlasHistoryService
        history = AtlasHistoryBase(
            entity_type="config",
            entity_id=f"{configs.entity_type}:{configs.field_name}",
            action="CREATE",
            description=f"Config created: {configs.entity_type}.{configs.field_name}",
            internal_only=True
        )
        history_service = AtlasHistoryService(self.repository.engine)
        await history_service.create_silently(history, curr_user)

        return created_config

    async def get(self, entity_type: str, curr_user: AtlasUserRes) -> dict[str, AtlasConfigs]:
        """Get all configs for an entity type as a dict keyed by field_name"""
        return await self.repository.get(entity_type)

    async def get_all(self, skip: int = 0, limit: int = 100, curr_user: Optional[AtlasUserRes] = None) -> list[AtlasConfigs]:
        """Get all configs"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, entity_type: str, field_name: str, config_data: dict, curr_user: AtlasUserRes) -> Optional[AtlasConfigs]:
        """Update a config"""
        config_data["updater_id"] = curr_user.user_id
        config_data["updater_name"] = curr_user.user_name
        updated_config = await self.repository.update(entity_type, field_name, config_data)

        # Log history
        from ..services.atlas_history_service import AtlasHistoryService
        history = AtlasHistoryBase(
            entity_type="config",
            entity_id=f"{entity_type}:{field_name}",
            action="UPDATE",
            description=f"Config updated: {entity_type}.{field_name}",
            internal_only=True
        )
        history_service = AtlasHistoryService(self.repository.engine)
        await history_service.create_silently(history, curr_user)

        return updated_config

    async def delete(self, entity_type: str, field_name: str, curr_user: AtlasUserRes) -> bool:
        """Delete a config"""
        result = await self.repository.delete(entity_type, field_name)

        # Log history
        from ..services.atlas_history_service import AtlasHistoryService
        history = AtlasHistoryBase(
            entity_type="config",
            entity_id=f"{entity_type}:{field_name}",
            action="DELETE",
            description=f"Config deleted: {entity_type}.{field_name}",
            internal_only=True
        )
        history_service = AtlasHistoryService(self.repository.engine)
        await history_service.create_silently(history, curr_user)

        return result

    async def get_by_entity_type(self, entity_type: str, curr_user: AtlasUserRes) -> list[AtlasConfigs]:
        """Get all configs for a specific entity type"""
        return await self.repository.get_by_entity_type(entity_type)
