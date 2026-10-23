"""Fetch once from OpenML 531; normalize and validate the historical housing table."""

from pathlib import Path

import pandas as pd
from sklearn.datasets import fetch_openml

from advanced_regression_mlops.config import DATA_PATH, FEATURES, TARGET


def validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return numeric columns in canonical order, rejecting schema drift."""
    frame = frame.copy()
    frame.columns = [str(col).strip().upper() for col in frame.columns]
    required = [*FEATURES, TARGET]
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Boston data is missing expected columns: {missing}")
    clean = frame.loc[:, required].apply(pd.to_numeric, errors="coerce")
    if clean[TARGET].isna().any():
        raise ValueError("Target MEDV contains invalid or missing values")
    if clean.empty:
        raise ValueError("Boston dataset is empty")
    return clean


def download_dataset(destination: Path = DATA_PATH) -> pd.DataFrame:
    """First download requires Internet; subsequent training uses cached CSV."""
    print("Downloading OpenML dataset 531 (Boston Housing) for educational use...")
    try:
        bunch = fetch_openml(data_id=531, as_frame=True, parser="auto")
    except Exception as exc:
        raise RuntimeError(
            "OpenML download failed. Check Internet access, then retry; "
            "or put a compatible boston.csv in data/raw/."
        ) from exc
    frame = bunch.frame
    if frame is None:
        raise ValueError("OpenML returned no DataFrame")
    clean = validate_frame(frame)
    destination.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(destination, index=False, lineterminator="\r\n")
    print(f"Saved {len(clean)} observations to {destination}")
    return clean


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read locally if possible, otherwise perform the explicit OpenML fetch."""
    if not path.exists():
        return download_dataset(path)
    return validate_frame(pd.read_csv(path))


def main() -> None:
    download_dataset()


if __name__ == "__main__":
    main()
