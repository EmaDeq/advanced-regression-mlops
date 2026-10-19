"""Offline test fixtures deliberately avoid the OpenML network dependency."""

import numpy as np
import pandas as pd
import pytest

from advanced_regression_mlops.config import FEATURES


@pytest.fixture
def synthetic_training_set() -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(42)
    X = pd.DataFrame(rng.uniform(1, 10, (80, len(FEATURES))), columns=FEATURES)
    X["CHAS"] = rng.integers(0, 2, size=80)
    y = pd.Series(8 + 3 * X["RM"] - 0.8 * X["LSTAT"])
    return X, y
