import structlog

logger = structlog.get_logger(__name__)


def log_prediction_monitoring(
    *,
    tenant_id: int,
    model_version: str,
    predicted_value: float,
    actual_value: float | None = None,
) -> None:
    payload = {
        "tenant_id": tenant_id,
        "model_version": model_version,
        "predicted_value": predicted_value,
    }
    if actual_value is not None:
        payload["actual_value"] = actual_value
    logger.info("ml_prediction_monitoring", **payload)
