"""Reproducible regression estimators and baselines."""

from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from advanced_regression_mlops.config import SEED


def make_advanced_pipeline() -> Pipeline:
    """Advanced nonlinear tree boosting with pipeline-owned imputation."""
    return Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            (
                "regressor",
                HistGradientBoostingRegressor(
                    random_state=SEED,
                    early_stopping=False,  # small historical dataset
                    max_iter=200,
                    min_samples_leaf=10,
                ),
            ),
        ]
    )


def make_baselines() -> dict[str, Pipeline]:
    return {
        "dummy_mean": Pipeline(
            [("impute", SimpleImputer(strategy="median")), ("regressor", DummyRegressor())]
        ),
        "ridge": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                ("regressor", Ridge(alpha=1.0)),
            ]
        ),
    }
