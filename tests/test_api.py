from fastapi.testclient import TestClient

from src.serve import app


def test_health_ok():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_predict_returns_valid_response():
    payload = {
        "tenure": 12,
        "monthly_charges": 70.5,
        "total_charges": 846.0,
        "contract": 0,
        "internet_service": 1,
        "payment_method": 2,
    }
    with TestClient(app) as client:
        r = client.post("/predict", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert 0.0 <= data["churn_probability"] <= 1.0
        assert data["action"] in {"urgent_retention_offer", "send_discount", "no_action"}


def test_predict_validates_input():
    bad_payload = {
        "tenure": -5,
        "monthly_charges": 70.5,
        "total_charges": 846.0,
        "contract": 0,
        "internet_service": 1,
        "payment_method": 2,
    }
    with TestClient(app) as client:
        r = client.post("/predict", json=bad_payload)
        assert r.status_code == 422


def test_metrics_endpoint():
    with TestClient(app) as client:
        r = client.get("/metrics")
        assert r.status_code == 200
        assert b"predictions_total" in r.content
