from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.v1.dependencies.services import get_auth_service
from app.core.rate_limit import limiter
from app.domain.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    _ = request
    try:
        return await service.login(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("15/minute")
async def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    _ = request
    try:
        return await service.refresh(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
