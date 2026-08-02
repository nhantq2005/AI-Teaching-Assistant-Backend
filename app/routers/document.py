from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.api.dependencies import get_document_service
from app.schemas.document import DocumentRequest, DocumentResponse, DocumentUpdateRequest
from fastapi import UploadFile, File
from app.services.document_service import DocumentService

router = APIRouter(tags=["documents"])

@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_api(
    title: str = Form(...),
    lecturer_id: int = Form(...),
    subject_id: int = Form(...),
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service)):
    document_request = DocumentRequest(
        title=title,
        lecturer_id=lecturer_id,
        subject_id=subject_id,
    )

    return await document_service.create_document(document_request=document_request, file=file)

@router.get("/subjects/{subject_id}/documents", response_model=List[DocumentResponse])
async def get_documents_by_subject_api(subject_id: int, document_service: DocumentService = Depends(get_document_service)):
    documents = await document_service.get_documents_by_subject(subject_id)
    return documents



@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents_api(params: dict, document_service: DocumentService = Depends(get_document_service)):
    params = {
        "title": params.get("title"),
        "created_date": params.get("created_date"),
        "skip": params.get("skip"),
        "limit": params.get("limit"),
    }
    params = {k: v for k, v in params.items() if v is not None}
    return await document_service.get_all_documents(params)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document_api(document_id: int, document_service: DocumentService = Depends(get_document_service)):
    document = await document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    return document


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document_api(
    document_id: int,
    title: str | None = Form(None),
    lecturer_id: int | None = Form(None),
    subject_id: int | None = Form(None),
    file: UploadFile | None = File(None),
    document_service: DocumentService = Depends(get_document_service),
):
    document_request = DocumentUpdateRequest(
        title=title,
        lecturer_id=lecturer_id,
        subject_id=subject_id,
    )
    document = await document_service.update_document(document_id, document_request, file)
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu để cập nhật")
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_api(document_id: int, document_service: DocumentService = Depends(get_document_service)):
    success = await document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu để xóa")
    return None
