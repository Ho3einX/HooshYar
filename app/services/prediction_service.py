import hashlib
import json
import time
from datetime import datetime

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.metrics import prediction_requests_total
from app.domain.schemas.common import PaginatedResponse
from app.domain.schemas.prediction import PredictionCreate, PredictionOut
from app.repositories.prediction_repository import PredictionRepository
from app.services.audit_service import AuditService

settings = get_settings()


class PredictionService:
    def __init__(
        self,
        prediction_repository: PredictionRepository,
        audit_service: AuditService,
        redis_client: Redis,
        model_registry,
    ) -> None:
        self.prediction_repository = prediction_repository
        self.audit_service = audit_service
        self.redis_client = redis_client
        self.model_registry = model_registry

    @staticmethod
    def _request_hash(payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def predict(self, *, user_id: int, payload: PredictionCreate) -> PredictionOut:
        features = payload.model_dump()
        request_hash = self._request_hash(features)
        model_version = self.model_registry.metadata["version"]
        cache_key = f"pred:{model_version}:{user_id}:{request_hash}"
        started = time.perf_counter()

        cached = await self.redis_client.get(cache_key)
        cache_hit = cached is not None
        if cache_hit:
            predicted_value = float(cached)
        else:
            predicted_value = self.model_registry.predict(features)
            await self.redis_client.set(
                cache_key,
                str(predicted_value),
                ex=settings.PREDICTION_CACHE_TTL_SECONDS,
            )

        latency_ms = int((time.perf_counter() - started) * 1000)
        row = await self.prediction_repository.create(
            user_id=user_id,
            sku_id=payload.sku_id,
            request_hash=request_hash,
            features=features,
            predicted_value=predicted_value,
            model_version=model_version,
            latency_ms=latency_ms,
            cache_hit=cache_hit,
        )

        await self.audit_service.log_action(
            actor_user_id=user_id,
            action="PREDICTION_CREATED",
            target_type="prediction_history",
            target_id=str(row.id),
            metadata_json={"sku_id": payload.sku_id, "model_version": model_version},
        )

        prediction_requests_total.labels(cache_hit=str(cache_hit).lower(), model_version=model_version).inc()

        return PredictionOut(
            message="پیش‌بینی با موفقیت انجام شد",
            id=row.id,
            sku_id=row.sku_id,
            predicted_demand=float(row.predicted_value),
            model_version=row.model_version,
            cache_hit=row.cache_hit,
            created_at=row.created_at,
        )

    async def list_history(
        self,
        *,
        user_id: int,
        page: int,
        page_size: int,
        sku_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> PaginatedResponse[PredictionOut]:
        rows, total = await self.prediction_repository.list_by_user(
            user_id=user_id,
            page=page,
            page_size=page_size,
            sku_id=sku_id,
            created_from=created_from,
            created_to=created_to,
        )

        items = [
            PredictionOut(
                message="رکورد پیش‌بینی",
                id=row.id,
                sku_id=row.sku_id,
                predicted_demand=float(row.predicted_value),
                model_version=row.model_version,
                cache_hit=row.cache_hit,
                created_at=row.created_at,
            )
            for row in rows
        ]
        return PaginatedResponse(
            message="لیست تاریخچه پیش‌بینی با موفقیت دریافت شد",
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
