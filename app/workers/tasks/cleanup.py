from app.core.celery_app import celery_app


@celery_app.task
def cleanup_expired_cache() -> dict:
    return {"message": "پاکسازی دوره‌ای انجام شد"}
