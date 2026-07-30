from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class NotificationCreate(BaseModel):
    title: str
    content: str
    subject_id: Optional[int] = None

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject_id: Optional[int] = None

class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    created_date: datetime
    subject_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
