from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from ..entities.atlas_document import AtlasDocument


class AtlasDocumentRepository:
    """Repository class for Document entity CRUD operations"""

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def create(self, document: AtlasDocument) -> AtlasDocument:
        """Create a new document"""
        async with AsyncSession(self.engine) as session:
            session.add(document)
            await session.commit()
            await session.refresh(document)
            return document

    async def get_by_id(self, document_id: str) -> Optional[AtlasDocument]:
        """Get a document by ID"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasDocument).where(AtlasDocument.document_id == document_id)
            result = await session.execute(statement)
            return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100, client_id: Optional[str] = None) -> list[AtlasDocument]:
        """Get all documents with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasDocument)
            if client_id is not None:
                statement = statement.where(AtlasDocument.client_id == client_id)
            statement = statement.offset(skip).limit(limit)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def update(self, document_id: str, document_data: dict) -> Optional[AtlasDocument]:
        """Update a document"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasDocument).where(AtlasDocument.document_id == document_id)
            result = await session.execute(statement)
            document = result.scalars().first()
            if not document:
                return None

            for key, value in document_data.items():
                if hasattr(document, key):
                    setattr(document, key, value)

            session.add(document)
            await session.commit()
            await session.refresh(document)
            return document

    async def delete(self, document_id: str) -> bool:
        """Delete a document"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasDocument).where(AtlasDocument.document_id == document_id)
            result = await session.execute(statement)
            document = result.scalars().first()
            if not document:
                return False

            await session.delete(document)
            await session.commit()
            return True

    async def get_by_entity_id(self, entity_id: str, client_id: Optional[str] = None) -> list[AtlasDocument]:
        """Get all documents for a specific entity with optional client filtering"""
        async with AsyncSession(self.engine) as session:
            statement = select(AtlasDocument).where(AtlasDocument.entity_id == entity_id)
            if client_id is not None:
                statement = statement.where(AtlasDocument.client_id == client_id)
            result = await session.execute(statement)
            return list(result.scalars().all())
