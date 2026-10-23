import pandas as pd
import pytest

from advanced_regression_mlops.config import FEATURES, TARGET
from advanced_regression_mlops.data import validate_frame


def test_validate_frame_normalizes_names() -> None:
    row = {name.lower(): [1.0] for name in [*FEATURES, TARGET]}
    result = validate_frame(pd.DataFrame(row))
    assert list(result) == [*FEATURES, TARGET]


def test_validate_frame_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing expected columns"):
        validate_frame(pd.DataFrame({"MEDV": [23.0]}))


def test_download_dataset_uses_canonical_line_endings(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from advanced_regression_mlops import data

    frame = pd.DataFrame({name: [1.0, 2.0] for name in [*FEATURES, TARGET]})
    monkeypatch.setattr(
        data,
        "fetch_openml",
        lambda **kwargs: SimpleNamespace(frame=frame),
    )

    destination = tmp_path / "boston.csv"
    data.download_dataset(destination)

    raw = destination.read_bytes()
    assert raw.count(b"\r\n") == len(frame) + 1
    assert b"\n" not in raw.replace(b"\r\n", b"")
