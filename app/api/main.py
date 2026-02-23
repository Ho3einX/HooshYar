from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.middleware import SlowAPIMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.middlewares.request_context import RequestContextMiddleware
from app.api.v1.routers import auth, health, predictions, users
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.ml.serving.registry import ModelRegistry
from app.repositories.role_repository import RoleRepository

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    app.state.model_registry = ModelRegistry(settings.MODEL_REGISTRY_PATH)
    app.state.model_registry.load_latest()

    async with AsyncSessionLocal() as session:
        await RoleRepository(session).ensure_defaults()

    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.state.limiter = limiter

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    register_exception_handlers(app)
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["health"])
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
    app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["users"])
    app.include_router(predictions.router, prefix=settings.API_V1_PREFIX, tags=["predictions"])
    return app


app = create_app()
