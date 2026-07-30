from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChatCitationCreate(BaseModel):
    similarity_score: float
    document_chunk_id: int
    chat_message_id: int

class ChatCitationUpdate(BaseModel):
    similarity_score: Optional[float] = None
    document_chunk_id: Optional[int] = None
    chat_message_id: Optional[int] = None

class ChatCitationResponse(BaseModel):
    id: int
    similarity_score: float
    document_chunk_id: int
    chat_message_id: int

    model_config = ConfigDict(from_attributes=True)
