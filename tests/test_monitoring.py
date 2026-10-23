"""Structured API log events must be usable without exposing inference inputs."""

import json

from fastapi.testclient import TestClient

from advanced_regression_mlops import api


def test_structured_health_event(monkeypatch):
    events = []
    monkeypatch.setattr(
        api.request_logger, "info", lambda message: events.append(json.loads(message))
    )
    monkeypatch.setattr(api, "load_bundle", lambda: {})
    monkeypatch.setenv("MLOPS_ENV", "test")

    response = TestClient(api.app).get("/health?secret=not-for-logs")

    assert response.status_code == 200
    assert len(events) == 1
    event = events[0]
    assert event["event"] == "http_request"
    assert event["route"] == "/health"
    assert event["method"] == "GET"
    assert event["environment"] == "test"
    assert event["status_code"] == 200
    assert event["latency_ms"] >= 0
    assert response.headers["X-Request-ID"] == event["request_id"]
    assert len(event["request_id"]) == 32
    assert "not-for-logs" not in json.dumps(event)


def test_structured_errors_do_not_log_prediction_payload(monkeypatch):
    events = []
    monkeypatch.setattr(
        api.request_logger, "info", lambda message: events.append(json.loads(message))
    )

    response = TestClient(api.app).post("/predict", json={"private_value": "DO_NOT_LOG_THIS"})
    assert response.status_code == 422
    assert len(events) == 1
    assert events[0]["route"] == "/predict"
    assert events[0]["status_code"] == 422
    assert response.headers["X-Request-ID"] == events[0]["request_id"]
    assert "DO_NOT_LOG_THIS" not in json.dumps(events[0])
    assert "CRIM" not in json.dumps(events[0])


def test_unmatched_paths_are_redacted(monkeypatch):
    events = []
    monkeypatch.setattr(
        api.request_logger, "info", lambda message: events.append(json.loads(message))
    )

    response = TestClient(api.app).get("/unknown/sensitive-fragment?token=secret")
    assert response.status_code == 404
    assert events[0]["route"] == "other"
    assert "secret" not in json.dumps(events)
    assert "sensitive-fragment" not in json.dumps(events)
