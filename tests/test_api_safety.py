import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from advanced_regression_mlops.api import HousingFeatures, app
from advanced_regression_mlops.config import FEATURES


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_prediction_input_rejects_nonfinite_numbers(invalid: float) -> None:
    payload = {feature: 1.0 for feature in FEATURES}
    payload["RM"] = invalid
    with pytest.raises(ValidationError):
        HousingFeatures(**payload)


def test_api_response_security_headers() -> None:
    response = TestClient(app).get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"
    assert len(response.headers["X-Request-ID"]) == 32
