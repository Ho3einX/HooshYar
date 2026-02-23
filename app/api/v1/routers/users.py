from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies.auth import get_current_user, require_roles
from app.api.v1.dependencies.services import get_user_service
from app.domain.schemas.user import UserCreate, UserOut
from app.services.user_service import UserService

router = APIRouter(prefix="/users")


def to_user_out(user) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/register", response_model=UserOut)
async def register_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserOut:
    safe_payload = payload.model_copy(update={"role_name": "User"})
    try:
        user = await service.create_user(safe_payload)
        return to_user_out(user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("", response_model=UserOut, dependencies=[Depends(require_roles("Admin"))])
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserOut:
    try:
        user = await service.create_user(payload)
        return to_user_out(user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)) -> UserOut:
    return to_user_out(current_user)
