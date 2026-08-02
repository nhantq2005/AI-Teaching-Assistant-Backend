from fastapi import Depends, HTTPException, status
from typing import List

from app.api.dependencies import get_current_user
from app.models.user import UserRole, User


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập API này"
            )
        return user