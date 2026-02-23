from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import PredictionHistory


class PredictionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: int,
        sku_id: str,
        request_hash: str,
        features: dict,
        predicted_value: float,
        model_version: str,
        latency_ms: int,
        cache_hit: bool,
    ) -> PredictionHistory:
        row = PredictionHistory(
            user_id=user_id,
            sku_id=sku_id,
            request_hash=request_hash,
            features=features,
            predicted_value=predicted_value,
            model_version=model_version,
            latency_ms=latency_ms,
            cache_hit=cache_hit,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        await self.session.commit()
        return row

    async def list_by_user(
        self,
        *,
        user_id: int,
        page: int,
        page_size: int,
        sku_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> tuple[list[PredictionHistory], int]:
        conditions = [PredictionHistory.user_id == user_id]
        if sku_id:
            conditions.append(PredictionHistory.sku_id == sku_id)
        if created_from:
            conditions.append(PredictionHistory.created_at >= created_from)
        if created_to:
            conditions.append(PredictionHistory.created_at <= created_to)

        total_stmt = select(func.count(PredictionHistory.id)).where(*conditions)
        total_result = await self.session.execute(total_stmt)
        total = int(total_result.scalar_one())

        stmt = (
            select(PredictionHistory)
            .where(*conditions)
            .order_by(PredictionHistory.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows, total
