"""Verify the DVC dataset snapshot and log a single trained CI release to MLflow."""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from advanced_regression_mlops.config import (
    DATA_PATH,
    DEFAULT_MODEL_PATH,
    METRICS_PATH,
    PROJECT_ROOT,
)

REPORT_PATH = PROJECT_ROOT / "reports" / "release-provenance.json"
DVC_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "boston.csv.dvc"
MODEL_CHECKSUM_PATH = PROJECT_ROOT / "artifacts" / "model.sha256"


def file_hash(path: Path, algorithm: str) -> str:
    """Hash file contents without loading large artifacts into memory."""
    hasher = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def dvc_expected_snapshot(pointer: Path) -> tuple[str, int]:
    """Read the single output MD5 and size from this repository's DVC pointer."""
    content = pointer.read_text(encoding="utf-8")
    hashes = re.findall(r"(?m)^- md5: ([a-f0-9]{32})\s*$", content)
    sizes = re.findall(r"(?m)^  size: ([0-9]+)\s*$", content)
    if len(hashes) != 1 or len(sizes) != 1:
        raise ValueError("Expected one DVC dataset output with MD5 and size")
    return hashes[0], int(sizes[0])


def verified_dataset(dataset: Path, pointer: Path) -> dict:
    """Reject a release trained using bytes differing from the tracked DVC snapshot."""
    expected_md5, expected_size = dvc_expected_snapshot(pointer)
    actual_md5 = file_hash(dataset, "md5")
    actual_size = dataset.stat().st_size
    if actual_md5 != expected_md5 or actual_size != expected_size:
        raise ValueError(
            "CI dataset differs from the DVC-tracked snapshot. "
            f"Expected md5={expected_md5} size={expected_size}; "
            f"got md5={actual_md5} size={actual_size}. "
            "Do not publish this candidate until provenance is reconciled."
        )
    return {
        "source": "OpenML 531 (historical educational Boston benchmark)",
        "dvc_pointer": "data/raw/boston.csv.dvc",
        "dvc_md5": expected_md5,
        "size_bytes": expected_size,
        "sha256": file_hash(dataset, "sha256"),
    }


def verified_model(model: Path, checksum_path: Path) -> dict:
    """Confirm the serialized model matches the digest Docker will package."""
    expected = checksum_path.read_text(encoding="utf-8").split()[0]
    actual = file_hash(model, "sha256")
    if not re.fullmatch(r"[a-f0-9]{64}", expected) or expected != actual:
        raise ValueError("Model SHA256 does not match artifacts/model.sha256")
    return {"sha256": actual, "checksum_file": "artifacts/model.sha256"}


def main() -> None:
    """Create an MLflow run from the model already trained by the release workflow."""
    import mlflow

    dataset = verified_dataset(DATA_PATH, DVC_DATA_PATH)
    model = verified_model(DEFAULT_MODEL_PATH, MODEL_CHECKSUM_PATH)
    evaluation = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    if evaluation["dataset"] != "OpenML 531 (historical Boston Housing)":
        raise ValueError("Unexpected training dataset in metrics")

    mlflow.set_tracking_uri("sqlite:///mlflow-ci.db")
    mlflow.set_experiment("Advanced Regression MLOps - CI releases")
    with mlflow.start_run(run_name=f"release-{os.getenv('GITHUB_RUN_ID', 'local')}") as run:
        mlflow.set_tags(
            {
                "source_git_sha": os.getenv("GITHUB_SHA", "local"),
                "dvc_dataset_md5": dataset["dvc_md5"],
                "model_sha256": model["sha256"],
                "release_run_id": os.getenv("GITHUB_RUN_ID", "local"),
            }
        )
        mlflow.log_params(evaluation["best_params"])
        mlflow.log_param("dataset", "openml-531")
        mlflow.log_param("model_version", evaluation["model_version"])
        mlflow.log_metrics({f"holdout_{k}": v for k, v in evaluation["holdout"].items()})
        mlflow.log_metric("best_cv_rmse", evaluation["best_cv_rmse"])

        record = {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "github": {
                "repository": os.getenv("GITHUB_REPOSITORY", "local"),
                "source_commit_sha": os.getenv("GITHUB_SHA", "local"),
                "release_run_id": os.getenv("GITHUB_RUN_ID", "local"),
            },
            "dataset": dataset,
            "model": {**model, "version": evaluation["model_version"]},
            "training": {
                "n_rows": evaluation["n_rows"],
                "n_train": evaluation["n_train"],
                "n_test": evaluation["n_test"],
                "hyperparameters": evaluation["best_params"],
                "holdout": evaluation["holdout"],
                "best_cv_rmse": evaluation["best_cv_rmse"],
            },
            "runtime_versions": {
                "python": sys.version.split()[0],
                "scikit-learn": version("scikit-learn"),
                "pandas": version("pandas"),
                "numpy": version("numpy"),
                "mlflow": version("mlflow"),
            },
            "mlflow": {"run_id": run.info.run_id, "store": "CI-local SQLite"},
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        mlflow.log_artifact(str(DEFAULT_MODEL_PATH), artifact_path="model")
        mlflow.log_artifact(str(METRICS_PATH), artifact_path="evaluation")
        mlflow.log_artifact(str(REPORT_PATH), artifact_path="provenance")
        print("Verified DVC dataset MD5:", dataset["dvc_md5"])
        print("Verified release model SHA256:", model["sha256"])
        print("MLflow release run ID:", run.info.run_id)
        print("Release provenance:", REPORT_PATH)


if __name__ == "__main__":
    main()
