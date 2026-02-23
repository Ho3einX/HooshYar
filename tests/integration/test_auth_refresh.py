import os

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="برای اجرای تست یکپارچه باید RUN_INTEGRATION_TESTS=1 تنظیم شود",
)


@pytest.mark.asyncio
async def test_refresh_token_rotation(async_client: AsyncClient):
    login_payload = {"email": "admin@example.com", "password": "Admin!12345"}
    login_resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    assert refresh_resp.json()["message"] == "توکن با موفقیت نوسازی شد"
