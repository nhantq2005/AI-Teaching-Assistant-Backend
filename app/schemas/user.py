from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from app.models.user import UserRole, Gender


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    gender: Gender = Gender.MALE
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.STUDENT


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id : int
    name: str
    gender: Optional[Gender] = None
    email: EmailStr
    username : str
    email : str
    role : Optional[UserRole]
    is_active : bool

    """UserResponse của bạn đang kế thừa từ BaseModel của pydantic.v1. Để FastAPI có thể tự động chuyển đổi object User 
    (SQLAlchemy) thành UserResponse trả về cho client, model này cần được cấu hình orm_mode."""
    model_config = ConfigDict(from_attributes=True)
