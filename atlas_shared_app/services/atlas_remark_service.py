from typing import Optional
from loguru import logger
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncEngine

from ..entities.atlas_history import AtlasHistoryBase
from ..entities.atlas_remark import AtlasRemark, AtlasRemarkBase
from ..entities.atlas_user import AtlasUserRes
from ..repositories.atlas_remark_repository import AtlasRemarkRepository
from .client_access import validate_client_access, get_client_filter_for_user


class AtlasRemarkService:
    """Service class for Remark entity business logic"""

    def __init__(self, engine: AsyncEngine):
        self.repository = AtlasRemarkRepository(engine)

    async def create(
        self,
        remark: AtlasRemarkBase,
        curr_user: AtlasUserRes,
        log_history: bool = True
    ) -> AtlasRemark:
        """Create a new remark with auto-generated UUID"""
        remark_data = remark.model_dump()
        # Set client info from request if not already provided
        if remark_data.get("client_id") is None:
            remark_data["client_id"] = curr_user.client_id
            remark_data["client_name"] = curr_user.client_name

        new_remark = AtlasRemark(
            **remark_data,
            remark_id=str(uuid4()),
            creater_id=curr_user.user_id,
            creater_name=curr_user.user_name,
            updater_id=curr_user.user_id,
            updater_name=curr_user.user_name
        )
        created_remark = await self.repository.create(new_remark)

        # Log history (skip for silent creates to avoid noise)
        if log_history:
            from ..services.atlas_history_service import AtlasHistoryService
            history = AtlasHistoryBase(
                entity_type=remark.entity_type,
                entity_id=remark.entity_id,
                action="ADD_REMARK",
                description=f"Remark added: {remark.remark[:50]}..." if len(remark.remark) > 50 else f"Remark added: {remark.remark}",
                internal_only=True,
                client_id=created_remark.client_id,
                client_name=created_remark.client_name
            )
            history_service = AtlasHistoryService(self.repository.engine)
            await history_service.create_silently(history, curr_user)

        return created_remark

    async def create_silently(
        self,
        remark: AtlasRemarkBase,
        curr_user: AtlasUserRes
    ) -> None:
        """Create a new remark silently - no return value and never raises errors"""
        try:
            await self.create(remark, curr_user, log_history=False)
            logger.debug(
                "Remark created silently: entity_id={}, entity_type={}",
                remark.entity_id,
                remark.entity_type
            )
        except Exception as e:
            logger.error(
                "Failed to create remark silently: entity_id={}, entity_type={}, error={}",
                remark.entity_id,
                remark.entity_type,
                str(e)
            )

    async def get_by_id(self, remark_id: str, curr_user: AtlasUserRes) -> Optional[AtlasRemark]:
        """Get a remark by ID with client access validation"""
        remark = await self.repository.get_by_id(remark_id)
        if remark:
            validate_client_access(curr_user, remark.client_id)
        return remark

    async def get_all(self, skip: int = 0, limit: int = 100, curr_user: Optional[AtlasUserRes] = None) -> list[AtlasRemark]:
        """Get all remarks with client filtering for external users"""
        client_filter = get_client_filter_for_user(curr_user) if curr_user else None
        return await self.repository.get_all(skip=skip, limit=limit, client_id=client_filter)

    async def delete(self, remark_id: str, curr_user: AtlasUserRes) -> bool:
        """Delete a remark with client access validation"""
        existing_remark = await self.repository.get_by_id(remark_id)

        # Validate access before delete
        if existing_remark:
            validate_client_access(curr_user, existing_remark.client_id)

        result = await self.repository.delete(remark_id)

        # Log history
        if existing_remark:
            from ..services.atlas_history_service import AtlasHistoryService
            history = AtlasHistoryBase(
                entity_type=existing_remark.entity_type,
                entity_id=existing_remark.entity_id,
                action="DELETE_REMARK",
                description=f"Remark deleted: {existing_remark.remark[:50]}..." if len(existing_remark.remark) > 50 else f"Remark deleted: {existing_remark.remark}",
                internal_only=True,
                client_id=existing_remark.client_id,
                client_name=existing_remark.client_name
            )
            history_service = AtlasHistoryService(self.repository.engine)
            await history_service.create_silently(history, curr_user)

        return result

    async def get_by_entity_id(self, entity_id: str, curr_user: AtlasUserRes) -> list[AtlasRemark]:
        """Get all remarks for a specific entity with client filtering"""
        client_filter = get_client_filter_for_user(curr_user)
        return await self.repository.get_by_entity_id(entity_id, client_id=client_filter)
