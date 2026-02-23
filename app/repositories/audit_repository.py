from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata_json: dict | None = None,
    ) -> AuditLog:
        row = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata_json,
        )
        self.session.add(row)
        await self.session.commit()
        return row
