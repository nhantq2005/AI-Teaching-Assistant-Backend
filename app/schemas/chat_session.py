from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChatSessionCreate(BaseModel):
    title: str
    user_id: int
    created_date: datetime
    updated_date: datetime

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    updated_date: Optional[datetime] = None

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_date: datetime
    updated_date: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)
