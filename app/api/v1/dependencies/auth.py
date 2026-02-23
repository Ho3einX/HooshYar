from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.v1.dependencies.services import get_user_service
from app.core.security import decode_token
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
):
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر است",
        ) from exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نوع توکن معتبر نیست",
        )

    user = await user_service.get_active_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کاربر معتبر نیست",
        )
    return user


def require_roles(*allowed_roles: str):
    async def checker(current_user=Depends(get_current_user)):
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="دسترسی مجاز نیست",
            )
        return current_user

    return checker
