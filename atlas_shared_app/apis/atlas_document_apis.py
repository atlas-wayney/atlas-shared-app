from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine

from ..database.atlas_asyncdb import get_engine
from ..entities.atlas_document import AtlasDocumentReq, AtlasDocumentRes
from ..entities.atlas_user import AtlasUserRes
from ..utils.app_utils.security import verify_viewer, verify_editor
from ..services.atlas_document_service import AtlasDocumentService
from ..settings.atlas_settings import get_document_settings
from ..settings.atlas_document_settings import AtlasDocumentSettings

router = APIRouter(prefix="/atlas-documents/v1", tags=["atlas-documents"])


def register_document_apis(app: FastAPI, prefix: str):
    """
    Register document APIs with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    logger.info("Register document APIs with the FastAPI app")
    app.include_router(router, prefix=prefix)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AtlasDocumentRes)
async def create_document(
    payload: AtlasDocumentReq,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)],
    document_settings: Annotated[AtlasDocumentSettings, Depends(get_document_settings)]
):
    """Create a new document"""
    service = AtlasDocumentService(engine)
    document = await service.create(payload, document_settings, curr_user)
    return document


@router.get("/{document_id}", response_model=AtlasDocumentRes)
async def get_document(
    document_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get a document by ID"""
    service = AtlasDocumentService(engine)
    document = await service.get_by_id(document_id, curr_user)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found")
    return document


@router.get("/", response_model=list[AtlasDocumentRes])
async def list_documents(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List all documents"""
    service = AtlasDocumentService(engine)
    return await service.get_all(skip=skip, limit=limit, curr_user=curr_user)


@router.put("/{document_id}", response_model=AtlasDocumentRes)
async def update_document(
    document_id: str,
    payload: AtlasDocumentReq,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)]
):
    """Update a document"""
    service = AtlasDocumentService(engine)

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updated = await service.update(document_id, update_data, curr_user)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found")
    return updated


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)]
):
    """Delete a document"""
    service = AtlasDocumentService(engine)

    success = await service.delete(document_id, curr_user)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found")
    return None


@router.get("/entity/{entity_id}", response_model=list[AtlasDocumentRes])
async def get_documents_by_entity(
    entity_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get all documents for a specific entity"""
    service = AtlasDocumentService(engine)
    return await service.get_by_entity_id(entity_id, curr_user)
