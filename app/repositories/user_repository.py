from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).options(selectinload(User.role)).where(User.id == user_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).options(selectinload(User.role)).where(User.email == email).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
        role_id: int,
        full_name: str | None,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            role_id=role_id,
            full_name=full_name,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user, attribute_names=["role"])
        await self.session.commit()
        return user
