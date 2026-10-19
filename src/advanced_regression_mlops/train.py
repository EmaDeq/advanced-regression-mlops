"""Fit baselines and tuned HGBR, with a strict test holdout."""

import argparse
import json
from datetime import datetime, timezone

import joblib
import pandas as pd
import sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, RandomizedSearchCV, train_test_split

from advanced_regression_mlops.config import (
    DEFAULT_MODEL_PATH,
    FEATURES,
    METRICS_PATH,
    SEED,
    TARGET,
)
from advanced_regression_mlops.data import load_data
from advanced_regression_mlops.modeling import make_advanced_pipeline, make_baselines


def measure(y_true: pd.Series, predictions: object) -> dict[str, float]:
    return {
        "mae": round(float(mean_absolute_error(y_true, predictions)), 4),
        "rmse": round(float(mean_squared_error(y_true, predictions) ** 0.5), 4),
        "r2": round(float(r2_score(y_true, predictions)), 4),
    }


def train(n_iter: int = 8, cv_splits: int = 5) -> dict:
    if n_iter < 1 or cv_splits < 2:
        raise ValueError("n_iter must be >=1 and cv_splits >=2")
    frame = load_data()
    X, y = frame.loc[:, list(FEATURES)], frame[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=SEED)

    baseline_results = {}
    for name, baseline in make_baselines().items():
        baseline.fit(X_train, y_train)
        baseline_results[name] = measure(y_test, baseline.predict(X_test))

    search = RandomizedSearchCV(
        estimator=make_advanced_pipeline(),
        param_distributions={
            "regressor__learning_rate": [0.03, 0.05, 0.1],
            "regressor__max_iter": [150, 250, 350],
            "regressor__max_leaf_nodes": [15, 31],
            "regressor__min_samples_leaf": [10, 20],
            "regressor__l2_regularization": [0.0, 0.1, 1.0],
        },
        n_iter=n_iter,
        cv=KFold(n_splits=cv_splits, shuffle=True, random_state=SEED),
        scoring="neg_root_mean_squared_error",
        n_jobs=1,  # predictable resource usage on a private laptop / tiny free cloud
        random_state=SEED,
        refit=True,
    )
    search.fit(X_train, y_train)
    prediction = search.best_estimator_.predict(X_test)
    model_version = "v0.1.0"
    metrics = {
        "model_version": model_version,
        "model_type": "HistGradientBoostingRegressor",
        "dataset": "OpenML 531 (historical Boston Housing)",
        "n_rows": len(frame),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "features": list(FEATURES),
        "excluded_feature": "B (racially constructed variable)",
        "target": TARGET,
        "target_unit": "thousands of historic USD",
        "holdout": measure(y_test, prediction),
        "baselines": baseline_results,
        "best_cv_rmse": round(float(-search.best_score_), 4),
        "best_params": search.best_params_,
        "sklearn_version": sklearn.__version__,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    DEFAULT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"pipeline": search.best_estimator_, "features": list(FEATURES), "version": model_version},
        DEFAULT_MODEL_PATH,
    )
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Model saved: {DEFAULT_MODEL_PATH}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train historical Boston regression model")
    parser.add_argument("--n-iter", type=int, default=8)
    parser.add_argument("--cv-splits", type=int, default=5)
    args = parser.parse_args()
    train(n_iter=args.n_iter, cv_splits=args.cv_splits)


if __name__ == "__main__":
    main()
