from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("bazaarmind", broker=settings.REDIS_DSN, backend=settings.REDIS_DSN)
celery_app.conf.task_routes = {
    "app.workers.tasks.train_model.*": {"queue": "ml-training"},
    "app.workers.tasks.cleanup.*": {"queue": "maintenance"},
}
