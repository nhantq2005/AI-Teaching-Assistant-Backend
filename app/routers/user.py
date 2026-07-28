# app/api/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from app.api.dependencies import get_current_user, get_user_service
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, user_service: UserService = Depends(get_user_service)) -> User:
    username = user_in.username.strip().lower()
    email = str(user_in.email).strip().lower()

    existing_user = (
        await user_service.get_user_by_username_or_email(username, email,)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username hoặc email đã tồn tại",
        )

    user_data = user_in.model_dump()
    user_data["username"] = username
    user_data["email"] = email

    return await user_service.create_user(user_data)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service)) -> Any:
    """
    API đăng nhập lấy JWT Token
    """
    # Gọi logic kiểm tra tài khoản và mật khẩu từ UserService
    user = await user_service.login(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Tạo token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> Any:
    """
    API lấy thông tin của chính User đang đăng nhập (Yêu cầu gửi kèm Token)
    """
    return current_user