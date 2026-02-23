from app.ml.serving.registry import ModelRegistry


class Predictor:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def predict(self, features: dict) -> float:
        return self.registry.predict(features)
