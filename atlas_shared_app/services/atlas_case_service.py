from typing import Any, Optional
from uuid import uuid4

from loguru import logger
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine

from ..settings.atlas_case_settings import AtlasCaseSettings
from ..entities.atlas_case import AtlasCase, AtlasCaseBase, AtlasCaseReq, AtlasCaseStatus, AtlasCaseStatusReq
from ..entities.atlas_history import AtlasHistoryBase
from ..entities.atlas_remark import AtlasRemarkBase
from ..entities.atlas_user import AtlasUserRes
from ..repositories.atlas_case_repository import AtlasCaseRepository
from .client_access import is_external_user, validate_client_access, get_client_filter_for_user


class CaseValidationError(Exception):
    """Exception raised when case data validation fails"""

    def __init__(self, field_name: str, error_message: str):
        self.field_name = field_name
        self.error_message = error_message
        super().__init__(f"Validation error on field '{field_name}': {error_message}")


class AtlasCaseService:
    """Service class for Case entity business logic"""

    def __init__(self, engine: AsyncEngine):
        self.repository = AtlasCaseRepository(engine)

    async def create(
        self,
        case: AtlasCaseBase,
        case_settings: AtlasCaseSettings,
        curr_user: AtlasUserRes
    ) -> AtlasCase:
        """Create a new case with auto-generated UUID"""
        logger.debug("Creating case: type={}, title={}", case.case_type, case.title)

        # Validate case data against the model for case_type
        self.validate_model(case.case_type, case.data, case_settings)

        new_case = AtlasCase(
            **case.model_dump(),
            case_id=str(uuid4()),
            creater_id=curr_user.user_id,
            creater_name=curr_user.user_name,
            updater_id=curr_user.user_id,
            updater_name=curr_user.user_name
        )
        created_case = await self.repository.create(new_case)

        logger.info(
            "Case created: case_id={}, type={}, status={}",
            created_case.case_id,
            created_case.case_type,
            created_case.case_status
        )

        # Log history
        from ..services.atlas_history_service import AtlasHistoryService
        history = AtlasHistoryBase(
            entity_type=created_case.case_type,
            entity_id=created_case.case_id,
            entity_target_status=created_case.case_status,
            action="CREATE",
            description=f"Case [{created_case.title}] created with status {created_case.case_status}",
            internal_only=True,
            client_id=created_case.client_id,
            client_name=created_case.client_name
        )
        history_service = AtlasHistoryService(self.repository.engine)
        await history_service.create_silently(history, curr_user)

        return created_case

    async def get_by_id(self, case_id: str, curr_user: AtlasUserRes) -> Optional[AtlasCase]:
        """Get a case by ID with client access validation"""
        case = await self.repository.get_by_id(case_id)
        if case:
            validate_client_access(curr_user, case.client_id)
        return case

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        case_status: Optional[str] = None,
        client_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        assigned_user_id: Optional[str] = None,
        curr_user: Optional[AtlasUserRes] = None
    ) -> list[AtlasCase]:
        """Get all cases with optional filtering and client access control"""
        # Override client_id for external users to ensure they only see their own client's data
        effective_client_id = client_id
        if curr_user and is_external_user(curr_user):
            effective_client_id = curr_user.client_id

        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            case_status=case_status,
            client_id=effective_client_id,
            entity_type=entity_type,
            entity_id=entity_id,
            assigned_user_id=assigned_user_id
        )

    async def update(
        self,
        case_id: str,
        case_data: AtlasCaseReq,
        case_settings: AtlasCaseSettings,
        curr_user: AtlasUserRes
    ) -> Optional[AtlasCase]:
        """Update a case with client access validation"""
        logger.debug("Updating case: {}", case_id)

        existing_case = await self.repository.get_by_id(case_id)
        if existing_case:
            # Validate access before update
            validate_client_access(curr_user, existing_case.client_id)
            self.validate_model(existing_case.case_type, case_data.data, case_settings)
        else:
            logger.warning("Case not found for update: {}", case_id)
            raise ValueError(f"Case with id {case_id} does not exist.")

        existing_case.data.update(case_data.data)
        existing_case.updater_id = curr_user.user_id
        existing_case.updater_name = curr_user.user_name

        updated_case = await self.repository.update(existing_case)

        logger.info("Case updated: case_id={}, type={}", case_id, existing_case.case_type)

        # Log history
        from ..services.atlas_history_service import AtlasHistoryService
        history = AtlasHistoryBase(
            entity_type=existing_case.case_type,
            entity_id=case_id,
            action="UPDATE",
            description=f"Case [{existing_case.title}] data updated",
            internal_only=True,
            client_id=existing_case.client_id,
            client_name=existing_case.client_name
        )
        history_service = AtlasHistoryService(self.repository.engine)
        await history_service.create_silently(history, curr_user)

        return updated_case

    async def delete(self, case_id: str, curr_user: AtlasUserRes) -> bool:
        """Delete a case with client access validation"""
        logger.debug("Deleting case: {}", case_id)
        existing_case = await self.repository.get_by_id(case_id)

        # Validate access before delete
        if existing_case:
            validate_client_access(curr_user, existing_case.client_id)
        else:
            logger.warning("Case not found for deletion: {}", case_id)

        result = await self.repository.delete(case_id)

        # Log history
        if existing_case:
            logger.info(
                "Case deleted: case_id={}, type={}, title={}",
                case_id,
                existing_case.case_type,
                existing_case.title
            )
            from ..services.atlas_history_service import AtlasHistoryService
            history = AtlasHistoryBase(
                entity_type=existing_case.case_type,
                entity_id=case_id,
                action="DELETE",
                description=f"Case [{existing_case.title}] deleted (was status: {existing_case.case_status})",
                internal_only=True,
                client_id=existing_case.client_id,
                client_name=existing_case.client_name
            )
            history_service = AtlasHistoryService(self.repository.engine)
            await history_service.create_silently(history, curr_user)

        return result

    async def get_by_client_id(self, client_id: str, curr_user: AtlasUserRes) -> list[AtlasCase]:
        """Get all cases for a specific client with access validation"""
        # External users can only query their own client
        if is_external_user(curr_user) and curr_user.client_id != client_id:
            return []
        return await self.repository.get_by_client_id(client_id)

    async def get_by_assigned_user_id(self, user_id: str, curr_user: AtlasUserRes) -> list[AtlasCase]:
        """Get all cases assigned to a specific user with client filtering"""
        client_filter = get_client_filter_for_user(curr_user)
        return await self.repository.get_by_assigned_user_id(user_id, client_id=client_filter)

    async def get_by_status(self, status: AtlasCaseStatus, curr_user: AtlasUserRes) -> list[AtlasCase]:
        """Get all cases with a specific status with client filtering"""
        client_filter = get_client_filter_for_user(curr_user)
        return await self.repository.get_by_status(status, client_id=client_filter)

    async def update_status(
        self,
        case_id: str,
        status_req: AtlasCaseStatusReq,
        curr_user: AtlasUserRes
    ) -> AtlasCase:
        """
        Update case status, assigned user, and add a remark.

        Args:
            case_id: The ID of the case to update
            status_req: Status update request containing case_status, assigned_user_id, assigned_user_name, and remark
            curr_user: The current user making the update

        Returns:
            The updated case

        Raises:
            ValueError: If case with given ID does not exist
        """
        logger.debug(
            "Updating case status: case_id={}, new_status={}, assigned_to={}",
            case_id,
            status_req.case_status,
            status_req.assigned_user_id
        )

        existing_case = await self.repository.get_by_id(case_id)
        if not existing_case:
            logger.warning("Case not found for status update: {}", case_id)
            raise ValueError(f"Case with id {case_id} does not exist.")

        # Validate access before update
        validate_client_access(curr_user, existing_case.client_id)

        old_status = existing_case.case_status
        existing_case.case_status = status_req.case_status
        existing_case.assigned_user_id = status_req.assigned_user_id
        existing_case.assigned_user_name = status_req.assigned_user_name
        existing_case.updater_id = curr_user.user_id
        existing_case.updater_name = curr_user.user_name

        updated_case = await self.repository.update(existing_case)
        if not updated_case:
            logger.error("Failed to update case status: {}", case_id)
            raise ValueError(f"Failed to update case with id {case_id}.")

        logger.info(
            "Case status updated: case_id={}, old_status={}, new_status={}, assigned_to={}",
            case_id,
            old_status,
            status_req.case_status,
            status_req.assigned_user_name
        )

        # Create a remark entry for the status change
        if status_req.remark:
            from ..services.atlas_remark_service import AtlasRemarkService
            new_remark = AtlasRemarkBase(
                entity_type=existing_case.case_type,
                entity_id=case_id,
                remark=status_req.remark,
                internal_only=True,
                client_id=existing_case.client_id,
                client_name=existing_case.client_name
            )
            remark_service = AtlasRemarkService(self.repository.engine)
            await remark_service.create_silently(new_remark, curr_user)

        # Log history
        from ..services.atlas_history_service import AtlasHistoryService
        history = AtlasHistoryBase(
            entity_type=existing_case.case_type,
            entity_id=case_id,
            entity_target_status=status_req.case_status,
            action="UPDATE_STATUS",
            description=f"Case [{existing_case.title}] status changed to {status_req.case_status}, assigned to {status_req.assigned_user_name}",
            internal_only=True,
            client_id=existing_case.client_id,
            client_name=existing_case.client_name
        )
        history_service = AtlasHistoryService(self.repository.engine)
        await history_service.create_silently(history, curr_user)

        return updated_case

    async def has_non_closed_cases_for_entity(self, entity_type: str, entity_id: str) -> bool:
        """Check if an entity has any non-closed cases"""
        return await self.repository.has_non_closed_cases_for_entity(entity_type, entity_id)

    @staticmethod
    def validate_model(case_type: str, data: dict[str, Any], case_settings: AtlasCaseSettings) -> bool:
        """
        Validate data against the SQLModel for the given case_type.

        Args:
            case_type: The type of case to validate against
            data: The data dictionary to validate
            case_settings: Case settings containing case_models

        Returns:
            True if validation passes

        Raises:
            CaseValidationError: If validation fails, with field_name and error_message
            ValueError: If case_type is not found in case_models
        """
        model_class = case_settings.case_types[case_type]
        if not model_class:
            raise ValueError(f"Unknown case_type: {case_type}. Available types: {list(case_settings.case_types.keys())}")

        try:
            model_class.model_validate(data)
            return True
        except ValidationError as e:
            # Get the first validation error
            error = e.errors()[0]
            field_name = ".".join(str(loc) for loc in error["loc"])
            error_message = error["msg"]
            raise CaseValidationError(field_name, error_message)
