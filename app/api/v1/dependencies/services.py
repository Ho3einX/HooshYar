from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis_client
from app.core.database import get_db_session
from app.repositories.audit_repository import AuditRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.services.prediction_service import PredictionService
from app.services.user_service import UserService


async def get_redis() -> AsyncGenerator[Redis, None]:
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


def get_role_repository(session: AsyncSession = Depends(get_db_session)) -> RoleRepository:
    return RoleRepository(session)


def get_prediction_repository(session: AsyncSession = Depends(get_db_session)) -> PredictionRepository:
    return PredictionRepository(session)


def get_audit_repository(session: AsyncSession = Depends(get_db_session)) -> AuditRepository:
    return AuditRepository(session)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    role_repository: RoleRepository = Depends(get_role_repository),
) -> UserService:
    return UserService(user_repository=user_repository, role_repository=role_repository)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    redis_client: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(user_repository=user_repository, redis_client=redis_client)


def get_audit_service(
    audit_repository: AuditRepository = Depends(get_audit_repository),
) -> AuditService:
    return AuditService(audit_repository=audit_repository)


def get_model_registry(request: Request):
    return request.app.state.model_registry


def get_prediction_service(
    prediction_repository: PredictionRepository = Depends(get_prediction_repository),
    audit_service: AuditService = Depends(get_audit_service),
    redis_client: Redis = Depends(get_redis),
    model_registry=Depends(get_model_registry),
) -> PredictionService:
    return PredictionService(
        prediction_repository=prediction_repository,
        audit_service=audit_service,
        redis_client=redis_client,
        model_registry=model_registry,
    )
