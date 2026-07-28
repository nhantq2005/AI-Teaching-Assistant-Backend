from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import ProcessingStatus


class DocumentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    lecturer_id: int
    subject_id: int


class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    lecturer_id: int | None = None
    subject_id: int | None = None


class DocumentResponse(BaseModel):
    id: int
    title: str

    file_url: str | None
    file_type: str | None
    file_name: str | None

    lecturer_id: int
    subject_id: int
    process_status: ProcessingStatus

    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)