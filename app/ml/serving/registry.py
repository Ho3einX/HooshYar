from pathlib import Path
import json

import joblib


class ModelRegistry:
    def __init__(self, root: str):
        self.root = Path(root)
        self.pipeline = None
        self.metadata: dict = {"version": "unavailable"}

    def load_latest(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        versions = sorted([path for path in self.root.iterdir() if path.is_dir()])
        if not versions:
            self.pipeline = None
            self.metadata = {"version": "unavailable"}
            return

        latest = versions[-1]
        self.pipeline = joblib.load(latest / "model.joblib")
        self.metadata = json.loads((latest / "metadata.json").read_text(encoding="utf-8"))

    def predict(self, features: dict) -> float:
        if self.pipeline is None:
            raise ValueError("مدل فعال برای پیش‌بینی موجود نیست")

        import pandas as pd

        frame = pd.DataFrame([features])
        prediction = self.pipeline.predict(frame)[0]
        return float(prediction)
