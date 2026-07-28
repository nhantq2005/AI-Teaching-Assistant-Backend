from fastapi import UploadFile, Form, File, Depends, HTTPException, status
from pathlib import Path
from sqlalchemy import cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.document import Document, ProcessingStatus
from app.schemas.document import DocumentRequest, DocumentUpdateRequest
from typing import List, Optional

from app.utils.cloudinary_utils import upload_file_to_cloudinary

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}


class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, document_request: DocumentRequest, file: UploadFile,) -> Document:
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên file không hợp lệ")

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("Chỉ hỗ trợ định dạng PDF, Word và PowerPoint")
            )

        try:
            await file.seek(0)

            upload_result = await upload_file_to_cloudinary(file=file,folder="documents")

            file_url = upload_result.get("secure_url")

            if not file_url:
                raise RuntimeError("Cloudinary không trả về secure_url")

            document = Document(
                title=document_request.title,
                lecturer_id=document_request.lecturer_id,
                subject_id=document_request.subject_id,
                file_url=file_url,
                file_type=extension.removeprefix("."),
                file_name=file.filename,
                process_status=ProcessingStatus.PENDING,
            )

            self.session.add(document)
            await self.session.commit()
            await self.session.refresh(document)

            return document

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể tạo tài liệu: {str(e)}",
            )

    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        stm = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stm)
        return result.scalars().first()

    async def get_all_documents(self, params: dict) -> List[Document]:
        skip = params.get('skip', 0)
        limit = params.get('limit', 100)

        stm = select(Document)

        if 'title' in params:
            stm = stm.where(Document.title.ilike(f"%{params['title']}%"))

        if 'created_date' in params:
            stm = stm.where(cast(Document.created_date, Date) == params['created_date'])

        if 'start_date' in params:
            stm = stm.where(cast(Document.created_date, Date) >= params['start_date'])
        if 'end_date' in params:
            stm = stm.where(cast(Document.created_date, Date) <= params['end_date'])

        stm = stm.offset(skip).limit(limit)
        result = await self.session.execute(stm)
        return list(result.scalars().all())

    async def update_document(
            self,
            document_id: int,
            document_request: DocumentUpdateRequest,
            file: UploadFile | None = None,
    ) -> Document:
        db_document = await self.get_document_by_id(document_id)

        if db_document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Không tìm thấy document với id: {document_id}")

        try:
            update_data = document_request.model_dump(
                exclude_unset=True,
                exclude_none=True,
            )

            for field_name, value in update_data.items():
                setattr(db_document, field_name, value)

            if file is not None:
                if not file.filename:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Tên file không hợp lệ",
                    )

                extension = Path(file.filename).suffix.lower()

                if extension not in ALLOWED_EXTENSIONS:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            "Định dạng file không được hỗ trợ. "
                            "Chỉ chấp nhận PDF, DOC, DOCX, PPT và PPTX"
                        ),
                    )

                await file.seek(0)

                upload_result = await upload_file_to_cloudinary(
                    file=file,
                    folder="documents",
                )

                file_url = upload_result.get("secure_url")

                if not file_url:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Cloudinary không trả về secure_url",
                    )

                db_document.file_url = file_url
                db_document.file_type = extension.removeprefix(".")
                db_document.file_name = file.filename
                db_document.process_status = ProcessingStatus.PENDING

            await self.session.commit()
            await self.session.refresh(db_document)

            return db_document

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể cập nhật tài liệu: {str(e)}",
            )

    async def delete_document(self, document_id: int) -> bool:
        try:
            db_document = await self.get_document_by_id(document_id)
            if not db_document:
                raise Exception(f"Không tìm thấy document với id: {document_id}")

            await self.session.delete(db_document)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e
