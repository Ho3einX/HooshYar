from datetime import datetime, timezone

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.domain.schemas.auth import TokenResponse
from app.repositories.user_repository import UserRepository

settings = get_settings()


class AuthService:
    def __init__(self, user_repository: UserRepository, redis_client: Redis) -> None:
        self.user_repository = user_repository
        self.redis_client = redis_client

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("ایمیل یا رمز عبور نادرست است")
        if not user.is_active:
            raise ValueError("حساب کاربری غیرفعال است")
        if not verify_password(password, user.hashed_password):
            raise ValueError("ایمیل یا رمز عبور نادرست است")

        user_id = str(user.id)
        return TokenResponse(
            message="ورود موفقیت‌آمیز بود",
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("نوع توکن نامعتبر است")

        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("توکن معتبر نیست")

        user = await self.user_repository.get_by_id(int(user_id))
        if user is None or not user.is_active:
            raise ValueError("کاربر معتبر نیست")

        jti = payload.get("jti")
        exp = int(payload.get("exp", 0))
        if not jti:
            raise ValueError("توکن معتبر نیست")

        used_key = f"refresh:used:{jti}"
        already_used = await self.redis_client.get(used_key)
        if already_used:
            raise ValueError("توکن رفرش قبلا استفاده شده است")

        now_epoch = int(datetime.now(timezone.utc).timestamp())
        ttl = max(exp - now_epoch + settings.REFRESH_TOKEN_REUSE_GRACE_SECONDS, 1)
        await self.redis_client.set(used_key, "1", ex=ttl)

        return TokenResponse(
            message="توکن با موفقیت نوسازی شد",
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )
