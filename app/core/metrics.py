from prometheus_client import Counter

prediction_requests_total = Counter(
    "prediction_requests_total",
    "Total number of prediction requests",
    ["cache_hit", "model_version"],
)
