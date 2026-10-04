from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    assert client.get("/healthz").status_code == 200


def test_readyz_ok():
    assert client.get("/readyz").status_code == 200


def test_readyz_dependency_down(monkeypatch):
    monkeypatch.setenv("DEPENDENCY_DOWN", "true")
    assert client.get("/readyz").status_code == 503


def test_checkout_success():
    r = client.post("/checkout")
    assert r.status_code == 200
    assert r.json()["status"] == "confirmed"


def test_metrics_exposed():
    client.post("/checkout")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "checkout_requests_total" in r.text