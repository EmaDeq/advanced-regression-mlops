import joblib
from fastapi.testclient import TestClient
from sklearn.dummy import DummyRegressor

from advanced_regression_mlops.api import app, load_bundle
from advanced_regression_mlops.config import FEATURES

SAMPLE = {
    "CRIM": 0.00632,
    "ZN": 18.0,
    "INDUS": 2.31,
    "CHAS": 0,
    "NOX": 0.538,
    "RM": 6.575,
    "AGE": 65.2,
    "DIS": 4.09,
    "RAD": 1.0,
    "TAX": 296.0,
    "PTRATIO": 15.3,
    "LSTAT": 4.98,
}


def test_api_predict_and_health(tmp_path, monkeypatch) -> None:
    model = DummyRegressor(strategy="constant", constant=22.0)
    model.fit([[1.0] * len(FEATURES)], [22.0])
    model_file = tmp_path / "dummy.joblib"
    joblib.dump({"pipeline": model, "features": list(FEATURES), "version": "test"}, model_file)
    monkeypatch.setenv("MODEL_PATH", str(model_file))
    load_bundle.cache_clear()
    try:
        client = TestClient(app)
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/model-info").json()["model_version"] == "test"
        response = client.post("/predict", json=SAMPLE)
        assert response.status_code == 200
        assert response.json()["predicted_value_thousands_usd"] == 22.0
        assert client.post("/predict", json={**SAMPLE, "B": 100.0}).status_code == 422
    finally:
        load_bundle.cache_clear()


def test_health_reports_unready(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "absent.joblib"))
    load_bundle.cache_clear()
    try:
        assert TestClient(app).get("/health").status_code == 503
    finally:
        load_bundle.cache_clear()
