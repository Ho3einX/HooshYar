from app.core.security import hash_password
from app.domain.entities import User
from app.domain.schemas.user import UserCreate
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def create_user(self, payload: UserCreate) -> User:
        existing = await self.user_repository.get_by_email(payload.email)
        if existing:
            raise ValueError("ایمیل قبلا ثبت شده است")

        role = await self.role_repository.get_by_name(payload.role_name)
        if role is None:
            raise ValueError("نقش درخواستی معتبر نیست")

        hashed = hash_password(payload.password)
        user = await self.user_repository.create(
            email=payload.email,
            hashed_password=hashed,
            role_id=role.id,
            full_name=payload.full_name,
        )
        return user

    async def get_active_user_by_id(self, user_id: int | str) -> User | None:
        user = await self.user_repository.get_by_id(int(user_id))
        if user and user.is_active:
            return user
        return None
