from typing import Optional
from sqlmodel import desc, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from ..entities.atlas_case import AtlasCase, AtlasCaseStatus


class AtlasCaseRepository:
    """Repository class for Case entity CRUD operations"""

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def create(self, case: AtlasCase) -> AtlasCase:
        """Create a new case"""
        async with AsyncSession(self.engine) as session:
            session.add(case)
            await session.commit()
            await session.refresh(case)
            return case

    async def get_by_id(self, case_id: str) -> Optional[AtlasCase]:
        """Get a case by ID"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasCase).where(AtlasCase.case_id == case_id)
            result = await session.execute(statement)
            return result.scalars().first()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        case_status: Optional[str] = None,
        client_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        assigned_user_id: Optional[str] = None
    ) -> list[AtlasCase]:
        """Get all cases with optional filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasCase)

            if case_status:
                statement = statement.where(AtlasCase.case_status == case_status)

            if client_id:
                statement = statement.where(AtlasCase.client_id == client_id)

            if entity_type:
                statement = statement.where(AtlasCase.entity_type == entity_type)

            if entity_id:
                statement = statement.where(AtlasCase.entity_id == entity_id)

            if assigned_user_id:
                statement = statement.where(AtlasCase.assigned_user_id == assigned_user_id)

            statement = statement.order_by(desc(AtlasCase.update_time)).offset(skip).limit(limit)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def update(self, case: AtlasCase) -> Optional[AtlasCase]:
        """Update a case"""
        async with AsyncSession(self.engine) as session:
            session.add(case)
            await session.commit()
            await session.refresh(case)
            return case

    async def delete(self, case_id: str) -> bool:
        """Delete a case"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasCase).where(AtlasCase.case_id == case_id)
            result = await session.execute(statement)
            case = result.scalars().first()
            if not case:
                return False

            await session.delete(case)
            await session.commit()
            return True

    async def get_by_client_id(self, client_id: str) -> list[AtlasCase]:
        """Get all cases for a specific client"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasCase).where(AtlasCase.client_id == client_id)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def get_by_assigned_user_id(self, user_id: str, client_id: Optional[str] = None) -> list[AtlasCase]:
        """Get all cases assigned to a specific user with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasCase).where(AtlasCase.assigned_user_id == user_id)
            if client_id is not None:
                statement = statement.where(AtlasCase.client_id == client_id)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def get_by_status(self, status: AtlasCaseStatus, client_id: Optional[str] = None) -> list[AtlasCase]:
        """Get all cases with a specific status with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasCase).where(AtlasCase.case_status == status.value)
            if client_id is not None:
                statement = statement.where(AtlasCase.client_id == client_id)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def has_non_closed_cases_for_entity(self, entity_type: str, entity_id: str) -> bool:
        """Check if there are any non-closed cases for a specific entity"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasCase).where(
                AtlasCase.entity_type == entity_type,
                AtlasCase.entity_id == entity_id,
                AtlasCase.case_status != AtlasCaseStatus.CLOSED.value
            ).limit(1)
            result = await session.execute(statement)
            return result.scalars().first() is not None
