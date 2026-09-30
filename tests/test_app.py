"""
Tests for Core Web Application Endpoints, Probes, Metrics, and Security Headers
"""

import pytest
from src.app.main import create_app
from src.app.metrics import metrics


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    metrics.set_chaos(False)
    with app.test_client() as client:
        yield client
    metrics.set_chaos(False)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "operational"
    assert "version" in data
    assert "endpoints" in data


def test_healthz_healthy(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ready"
    assert "checks" in data


def test_metrics_prometheus_format(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "http_requests_total" in text
    assert "uptime_seconds" in text


def test_security_headers_present(client):
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")


def test_chaos_fault_injection_and_recovery(client):
    # 1. Verify healthy initial state
    res = client.get("/healthz")
    assert res.status_code == 200

    # 2. Inject chaos fault
    chaos_res = client.post("/api/v1/chaos/simulate-failure")
    assert chaos_res.status_code == 200
    assert chaos_res.get_json()["chaos_active"] is True

    # 3. Liveness probe must now return 503 Service Unavailable
    res_faulty = client.get("/healthz")
    assert res_faulty.status_code == 503
    assert res_faulty.get_json()["status"] == "UNHEALTHY"

    # 4. Readiness probe must also fail
    ready_faulty = client.get("/ready")
    assert ready_faulty.status_code == 503

    # 5. Recover from chaos
    rec_res = client.post("/api/v1/chaos/recover")
    assert rec_res.status_code == 200

    # 6. Verify health restored to 200 OK
    res_restored = client.get("/healthz")
    assert res_restored.status_code == 200
