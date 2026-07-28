from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
# Giả sử bạn import model User từ models.user
from app.models.user import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        # Cách viết mới: Tạo statement trước, execute sau
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)

        # Lấy ra phần tử đầu tiên, hoặc trả về None nếu không tìm thấy
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict) -> User:
        try:
            hashed_password = get_password_hash(
                user_data["password"]
            )

            new_user = User(
                name=user_data["name"],
                gender=user_data["gender"],
                username=user_data["username"].strip().lower(),
                email=str(user_data["email"]).strip().lower(),
                password=hashed_password,
                role=user_data.get("role", "STUDENT"),
            )

            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)

            return new_user

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)  # Đánh dấu xóa
        await self.session.commit()  # Thực thi xóa

    async def login(self, username: str, password: str) -> User | None:
        # 1. Chỉ query theo username
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        # 2. Kiểm tra user tồn tại và so sánh mật khẩu
        if user and verify_password(password, user.password):
            return user
        return None

    async def get_user_by_username_or_email(self, username: str, email: str,
    ) -> User | None:
        stmt = select(User).where(
            or_(
                User.username == username,
                User.email == email,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()
