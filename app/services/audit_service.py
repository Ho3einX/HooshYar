from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, audit_repository: AuditRepository) -> None:
        self.audit_repository = audit_repository

    async def log_action(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata_json: dict | None = None,
    ) -> None:
        await self.audit_repository.create(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata_json,
        )
