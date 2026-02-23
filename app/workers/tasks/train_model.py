from app.core.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def retrain_tenant_model(self, tenant_id: int) -> dict:
    return {"message": "آموزش مدل در صف قرار گرفت", "tenant_id": tenant_id}
