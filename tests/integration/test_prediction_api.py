import os

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="برای اجرای تست یکپارچه باید RUN_INTEGRATION_TESTS=1 تنظیم شود",
)


@pytest.mark.asyncio
async def test_predict_endpoint_returns_persian_message(async_client: AsyncClient):
    auth_payload = {"email": "admin@example.com", "password": "Admin!12345"}
    login_response = await async_client.post("/api/v1/auth/login", json=auth_payload)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "sku_id": "SKU-1001",
        "price": 120000.0,
        "discount": 0.1,
        "inventory": 250,
        "category": "beauty",
        "city": "tehran",
        "channel": "marketplace",
        "horizon_days": 30,
    }
    response = await async_client.post("/api/v1/predictions/predict", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "پیش‌بینی با موفقیت انجام شد"
