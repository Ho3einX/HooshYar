from datetime import datetime, timezone
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.ml.features.transform import build_features


def train_model(df: pd.DataFrame, output_root: str) -> dict:
    dataset = build_features(df)
    target_col = "units_sold"
    features = [
        "price",
        "discount",
        "inventory",
        "day_of_week",
        "is_weekend",
        "lag_1",
        "lag_7",
        "rolling_mean_7",
        "category",
        "city",
        "channel",
    ]

    x_data = dataset[features]
    y_data = dataset[target_col]

    numeric_features = ["price", "discount", "inventory", "lag_1", "lag_7", "rolling_mean_7"]
    categorical_features = ["category", "city", "channel", "day_of_week", "is_weekend"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    estimator = LGBMRegressor(
        n_estimators=600,
        learning_rate=0.03,
        num_leaves=63,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )

    pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])

    x_train, x_valid, y_train, y_valid = train_test_split(
        x_data, y_data, test_size=0.2, shuffle=False
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_valid)

    mae = float(mean_absolute_error(y_valid, predictions))
    rmse = float(np.sqrt(mean_squared_error(y_valid, predictions)))
    mape = float(np.mean(np.abs((y_valid - predictions) / np.maximum(y_valid, 1))) * 100)

    version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    artifact_dir = Path(output_root) / version
    artifact_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, artifact_dir / "model.joblib")
    metadata = {
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {"mae": mae, "rmse": rmse, "mape": mape},
        "features": features,
        "framework": "lightgbm",
    }
    (artifact_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
    return metadata
