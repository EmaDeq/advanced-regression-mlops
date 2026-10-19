"""Offline integration test: full training, metrics and usable serialized pipeline."""

import joblib

from advanced_regression_mlops import train as trainer
from advanced_regression_mlops.config import FEATURES, TARGET


def test_train_end_to_end_offline(tmp_path, monkeypatch, synthetic_training_set) -> None:
    X, y = synthetic_training_set
    frame = X.copy()
    frame[TARGET] = y
    artifact_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"
    monkeypatch.setattr(trainer, "load_data", lambda: frame)
    monkeypatch.setattr(trainer, "DEFAULT_MODEL_PATH", artifact_path)
    monkeypatch.setattr(trainer, "METRICS_PATH", metrics_path)

    metrics = trainer.train(n_iter=1, cv_splits=2)
    assert artifact_path.is_file()
    assert metrics_path.is_file()
    assert metrics["n_train"] + metrics["n_test"] == len(frame)
    assert metrics["features"] == list(FEATURES)
    bundle = joblib.load(artifact_path)
    assert len(bundle["pipeline"].predict(X.iloc[:2])) == 2
