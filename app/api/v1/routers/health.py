from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session

router = APIRouter(prefix="/health")


@router.get("/live")
async def liveness() -> dict:
    return {"message": "سرویس فعال است"}


@router.get("/ready")
async def readiness(session: AsyncSession = Depends(get_db_session)) -> dict:
    await session.execute(text("SELECT 1"))
    return {"message": "سرویس آماده پاسخ‌گویی است"}
