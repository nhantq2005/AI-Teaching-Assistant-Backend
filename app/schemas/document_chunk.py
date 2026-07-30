from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DocumentChunkCreate(BaseModel):
    content: str
    page_number: Optional[int] = None
    chunk_index: int
    vector_id: Optional[str] = None
    document_id: int

class DocumentChunkUpdate(BaseModel):
    content: Optional[str] = None
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    vector_id: Optional[str] = None
    document_id: Optional[int] = None

class DocumentChunkResponse(BaseModel):
    id: int
    content: str
    page_number: Optional[int] = None
    chunk_index: int
    vector_id: Optional[str] = None
    created_date: datetime
    updated_date: datetime
    document_id: int

    model_config = ConfigDict(from_attributes=True)
