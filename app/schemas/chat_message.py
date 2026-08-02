from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChatMessageCreate(BaseModel):
    question: str
    answer: str
    chat_session_id: int

class ChatMessageUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: int
    question: str
    answer: str
    chat_session_id: int

    model_config = ConfigDict(from_attributes=True)
