"""Shared project configuration."""

import os
from pathlib import Path

PROJECT_ROOT = Path(
    os.environ.get("MLOPS_PROJECT_ROOT", str(Path(__file__).resolve().parents[2]))
).resolve()
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "boston.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "artifacts" / "model.joblib"
METRICS_PATH = PROJECT_ROOT / "reports" / "metrics.json"

# Exclude racially derived 'B' by design. See docs/data_ethics.md.
FEATURES = (
    "CRIM",
    "ZN",
    "INDUS",
    "CHAS",
    "NOX",
    "RM",
    "AGE",
    "DIS",
    "RAD",
    "TAX",
    "PTRATIO",
    "LSTAT",
)
TARGET = "MEDV"
SEED = 42


def model_path() -> Path:
    """Resolve a runtime override for deployment while retaining a local default."""
    return Path(os.environ.get("MODEL_PATH", str(DEFAULT_MODEL_PATH))).resolve()
