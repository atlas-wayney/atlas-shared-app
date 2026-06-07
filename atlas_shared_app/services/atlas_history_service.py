from typing import Optional
from loguru import logger
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncEngine

from ..entities.atlas_history import AtlasHistory, AtlasHistoryBase
from ..entities.atlas_user import AtlasUserRes
from ..repositories.atlas_history_repository import AtlasHistoryRepository
from .client_access import validate_client_access, get_client_filter_for_user


class AtlasHistoryService:
    """Service class for History entity business logic"""

    def __init__(self, engine: AsyncEngine):
        self.repository = AtlasHistoryRepository(engine)

    async def create(
        self,
        history: AtlasHistoryBase,
        curr_user: AtlasUserRes
    ) -> AtlasHistory:
        """Create a new history entry with auto-generated UUID"""
        history_data = history.model_dump()
        # Set client info from request if not already provided
        if history_data.get("client_id") is None:
            history_data["client_id"] = curr_user.client_id
            history_data["client_name"] = curr_user.client_name

        new_history = AtlasHistory(
            **history_data,
            history_id=str(uuid4()),
            creater_id=curr_user.user_id,
            creater_name=curr_user.user_name,
            updater_id=curr_user.user_id,
            updater_name=curr_user.user_name
        )
        return await self.repository.create(new_history)

    async def create_silently(
        self,
        history: AtlasHistoryBase,
        curr_user: AtlasUserRes
    ) -> None:
        """Create a new history entry silently - no return value and never raises errors"""
        try:
            await self.create(history, curr_user)
            logger.debug(
                "History entry created silently: entity_id={}, entity_type={}, action={}",
                history.entity_id,
                history.entity_type,
                history.action
            )
        except Exception as e:
            logger.error(
                "Failed to create history entry silently: entity_id={}, entity_type={}, action={}, error={}",
                history.entity_id,
                history.entity_type,
                history.action,
                str(e)
            )

    async def get_by_id(self, history_id: str, curr_user: AtlasUserRes) -> Optional[AtlasHistory]:
        """Get a history entry by ID with client access validation"""
        history = await self.repository.get_by_id(history_id)
        if history:
            validate_client_access(curr_user, history.client_id)
        return history

    async def get_all(self, skip: int = 0, limit: int = 100, curr_user: Optional[AtlasUserRes] = None) -> list[AtlasHistory]:
        """Get all history entries with client filtering for external users"""
        client_filter = get_client_filter_for_user(curr_user) if curr_user else None
        return await self.repository.get_all(skip=skip, limit=limit, client_id=client_filter)

    async def get_by_entity_id(self, entity_id: str, curr_user: AtlasUserRes) -> list[AtlasHistory]:
        """Get all history entries for a specific entity with client filtering"""
        client_filter = get_client_filter_for_user(curr_user)
        return await self.repository.get_by_entity_id(entity_id, client_id=client_filter)
