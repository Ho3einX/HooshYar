import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.main import create_app


class FakeModelRegistry:
    def __init__(self) -> None:
        self.metadata = {"version": "test-model-v1"}

    def predict(self, _: dict) -> float:
        return 100.0


@pytest.fixture
def test_app():
    app = create_app()
    app.state.model_registry = FakeModelRegistry()
    return app


@pytest_asyncio.fixture
async def async_client(test_app):
    transport = ASGITransport(app=test_app, lifespan="off")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
