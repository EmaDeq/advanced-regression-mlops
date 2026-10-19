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
