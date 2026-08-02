from typing import Optional
from pydantic import BaseModel, ConfigDict

class EnrollmentCreate(BaseModel):
    semester: int
    user_id: int
    subject_id: int

class EnrollmentUpdate(BaseModel):
    semester: Optional[int] = None
    user_id: Optional[int] = None
    subject_id: Optional[int] = None

class EnrollmentResponse(BaseModel):
    id: int
    semester: int
    user_id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)
