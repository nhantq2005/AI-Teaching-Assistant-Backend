from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class NotificationReadCreate(BaseModel):
    user_id: int
    notification_id: int
    is_read: bool = False
    read_date: Optional[datetime] = None

class NotificationReadUpdate(BaseModel):
    is_read: Optional[bool] = None
    read_date: Optional[datetime] = None

class NotificationReadResponse(BaseModel):
    id: int
    is_read: bool
    read_date: Optional[datetime] = None
    user_id: int
    notification_id: int

    model_config = ConfigDict(from_attributes=True)
