import copy

import pytest

from advanced_regression_mlops.config import FEATURES
from advanced_regression_mlops.release_quality import verify_release_quality


@pytest.fixture
def quality_metrics():
    return {
        "dataset": "OpenML 531 (historical Boston Housing)",
        "features": list(FEATURES),
        "n_rows": 506,
        "n_train": 404,
        "n_test": 102,
        "holdout": {"mae": 2.1019, "rmse": 3.02, "r2": 0.8756},
        "baselines": {
            "dummy_mean": {"mae": 6.2558, "rmse": 8.6629},
            "ridge": {"mae": 3.1074, "rmse": 4.7761},
        },
    }


def test_accepts_reproducible_historical_holdout(quality_metrics):
    assert verify_release_quality(quality_metrics)["r2"] == 0.8756


@pytest.mark.parametrize("metric,value", [("r2", 0.5), ("mae", 4.0), ("rmse", 5.0)])
def test_rejects_quality_regression(quality_metrics, metric, value):
    bad = copy.deepcopy(quality_metrics)
    bad["holdout"][metric] = value
    with pytest.raises(ValueError, match="Holdout quality gate failed"):
        verify_release_quality(bad)


def test_rejects_models_not_beating_ridge(quality_metrics):
    quality_metrics["baselines"]["ridge"]["mae"] = 1.9
    with pytest.raises(ValueError, match="must beat ridge"):
        verify_release_quality(quality_metrics)


def test_rejects_bad_feature_schema(quality_metrics):
    quality_metrics["features"].append("B")
    with pytest.raises(ValueError, match="Unexpected input schema"):
        verify_release_quality(quality_metrics)
