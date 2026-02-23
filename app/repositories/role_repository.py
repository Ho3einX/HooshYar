from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Role


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_defaults(self) -> None:
        existing = await self.session.execute(select(Role.name))
        names = {row[0] for row in existing.all()}
        for role_name in ("Admin", "User"):
            if role_name not in names:
                self.session.add(Role(name=role_name, description=f"{role_name} role"))
        await self.session.commit()
