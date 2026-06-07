from typing import Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncEngine

from ..entities.atlas_document import AtlasDocument, AtlasDocumentBase
from ..entities.atlas_history import AtlasHistoryBase
from ..entities.atlas_user import AtlasUserRes
from ..repositories.atlas_document_repository import AtlasDocumentRepository
from ..settings.atlas_document_settings import AtlasDocumentSettings
from .client_access import validate_client_access, get_client_filter_for_user


class AtlasDocumentService:
    """Service class for Document entity business logic"""

    def __init__(self, engine: AsyncEngine):
        self.repository = AtlasDocumentRepository(engine)

    async def create(
        self,
        document: AtlasDocumentBase,
        document_settings: AtlasDocumentSettings,
        curr_user: AtlasUserRes
    ) -> AtlasDocument:
        """Create a new document with auto-generated UUID"""

        doc_id = str(uuid4())
        fullpath = f"{doc_id}/{document.document_name}"

        document_data = document.model_dump()
        # Set client info from request if not already provided
        if document_data.get("client_id") is None:
            document_data["client_id"] = curr_user.client_id
            document_data["client_name"] = curr_user.client_name

        new_document = AtlasDocument(
            **document_data,
            document_id=doc_id,
            bucket=document_settings.bucket,
            fullpath=fullpath,
            creater_id=curr_user.user_id,
            creater_name=curr_user.user_name,
            updater_id=curr_user.user_id,
            updater_name=curr_user.user_name
        )
        created_document = await self.repository.create(new_document)

        # Log history
        from ..services.atlas_history_service import AtlasHistoryService
        history = AtlasHistoryBase(
            entity_type=document.entity_type,
            entity_id=document.entity_id,
            action="UPLOAD",
            description=f"Document uploaded: {document.document_name}",
            internal_only=True,
            client_id=created_document.client_id,
            client_name=created_document.client_name
        )
        history_service = AtlasHistoryService(self.repository.engine)
        await history_service.create_silently(history, curr_user)

        return created_document

    async def get_by_id(self, document_id: str, curr_user: AtlasUserRes) -> Optional[AtlasDocument]:
        """Get a document by ID with client access validation"""
        document = await self.repository.get_by_id(document_id)
        if document:
            validate_client_access(curr_user, document.client_id)
        return document

    async def get_all(self, skip: int = 0, limit: int = 100, curr_user: Optional[AtlasUserRes] = None) -> list[AtlasDocument]:
        """Get all documents with client filtering for external users"""
        client_filter = get_client_filter_for_user(curr_user) if curr_user else None
        return await self.repository.get_all(skip=skip, limit=limit, client_id=client_filter)

    async def update(self, document_id: str, document_data: dict, curr_user: AtlasUserRes) -> Optional[AtlasDocument]:
        """Update a document with client access validation"""
        existing_document = await self.repository.get_by_id(document_id)

        # Validate access before update
        if existing_document:
            validate_client_access(curr_user, existing_document.client_id)

        document_data["updater_id"] = curr_user.user_id
        document_data["updater_name"] = curr_user.user_name
        updated_document = await self.repository.update(document_id, document_data)

        # Log history
        if existing_document:
            from ..services.atlas_history_service import AtlasHistoryService
            history = AtlasHistoryBase(
                entity_type=existing_document.entity_type,
                entity_id=existing_document.entity_id,
                action="UPDATE",
                description=f"Document updated: {existing_document.document_name}",
                internal_only=True,
                client_id=existing_document.client_id,
                client_name=existing_document.client_name
            )
            history_service = AtlasHistoryService(self.repository.engine)
            await history_service.create_silently(history, curr_user)

        return updated_document

    async def delete(self, document_id: str, curr_user: AtlasUserRes) -> bool:
        """Delete a document with client access validation"""
        existing_document = await self.repository.get_by_id(document_id)

        # Validate access before delete
        if existing_document:
            validate_client_access(curr_user, existing_document.client_id)

        result = await self.repository.delete(document_id)

        # Log history
        if existing_document:
            from ..services.atlas_history_service import AtlasHistoryService
            history = AtlasHistoryBase(
                entity_type=existing_document.entity_type,
                entity_id=existing_document.entity_id,
                action="DELETE",
                description=f"Document deleted: {existing_document.document_name}",
                internal_only=True,
                client_id=existing_document.client_id,
                client_name=existing_document.client_name
            )
            history_service = AtlasHistoryService(self.repository.engine)
            await history_service.create_silently(history, curr_user)

        return result

    async def get_by_entity_id(self, entity_id: str, curr_user: AtlasUserRes) -> list[AtlasDocument]:
        """Get all documents for a specific entity with client filtering"""
        client_filter = get_client_filter_for_user(curr_user)
        return await self.repository.get_by_entity_id(entity_id, client_id=client_filter)
