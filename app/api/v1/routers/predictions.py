from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.v1.dependencies.auth import require_roles
from app.api.v1.dependencies.pagination import get_pagination_params
from app.api.v1.dependencies.services import get_prediction_service
from app.core.rate_limit import limiter
from app.domain.schemas.common import PaginatedResponse, PaginationParams
from app.domain.schemas.prediction import PredictionCreate, PredictionOut
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions")


@router.post("/predict", response_model=PredictionOut)
@limiter.limit("30/minute")
async def predict(
    request: Request,
    payload: PredictionCreate,
    current_user=Depends(require_roles("Admin", "User")),
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionOut:
    _ = request
    try:
        return await service.predict(user_id=current_user.id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/history", response_model=PaginatedResponse[PredictionOut])
async def history(
    pagination: PaginationParams = Depends(get_pagination_params),
    sku_id: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    current_user=Depends(require_roles("Admin", "User")),
    service: PredictionService = Depends(get_prediction_service),
) -> PaginatedResponse[PredictionOut]:
    return await service.list_history(
        user_id=current_user.id,
        page=pagination.page,
        page_size=pagination.page_size,
        sku_id=sku_id,
        created_from=created_from,
        created_to=created_to,
    )
