import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.sort_values(["tenant_id", "sku_id", "date"]).copy()
    prepared["day_of_week"] = prepared["date"].dt.dayofweek
    prepared["is_weekend"] = (prepared["day_of_week"] >= 4).astype(int)
    prepared["lag_1"] = prepared.groupby(["tenant_id", "sku_id"])["units_sold"].shift(1)
    prepared["lag_7"] = prepared.groupby(["tenant_id", "sku_id"])["units_sold"].shift(7)
    prepared["rolling_mean_7"] = (
        prepared.groupby(["tenant_id", "sku_id"])["units_sold"].shift(1).rolling(7).mean()
    )
    return prepared.dropna()
