"""Train and log a regression experiment to local MLflow."""

import mlflow

from advanced_regression_mlops.config import (
    DEFAULT_MODEL_PATH,
    METRICS_PATH,
)
from advanced_regression_mlops.train import train


def main() -> None:
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Advanced Regression MLOps")

    with mlflow.start_run(run_name="histgradientboosting-local"):
        results = train(n_iter=8)

        mlflow.log_params(results["best_params"])
        mlflow.log_param("dataset", "openml-531")
        mlflow.log_param("model_version", results["model_version"])

        for metric, value in results["holdout"].items():
            mlflow.log_metric(f"holdout_{metric}", value)

        for name, baseline in results["baselines"].items():
            for metric, value in baseline.items():
                mlflow.log_metric(f"baseline_{name}_{metric}", value)

        mlflow.log_metric("cv_rmse", results["best_cv_rmse"])

        mlflow.log_artifact(str(DEFAULT_MODEL_PATH), artifact_path="model")
        mlflow.log_artifact(str(METRICS_PATH), artifact_path="evaluation")

        print(f"MLflow run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    main()
