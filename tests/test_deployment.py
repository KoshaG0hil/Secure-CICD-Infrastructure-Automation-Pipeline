"""
Tests for Deployment Coordinator, Health Prober, and Rollback Controller
"""

import os
import shutil
import tempfile
import pytest
from src.deployment.deployer import DeploymentCoordinator
from src.deployment.rollback_controller import RollbackController
from src.deployment.health_probe import DeploymentHealthProbe


def test_rollback_controller_incident_generation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        controller = RollbackController(service_name="test-service", reports_dir=tmp_dir)

        fake_probe_metrics = {
            "target": "http://localhost:8080",
            "passed": False,
            "consecutive_failures": 3
        }

        res = controller.trigger_rollback(
            current_version="v2.0.0-broken",
            target_stable_version="v1.0.0",
            failure_reason="Continuous 503 errors during health probing",
            probe_metrics=fake_probe_metrics
        )

        assert res["success"] is True
        assert res["restored_version"] == "v1.0.0"
        assert os.path.exists(res["json_report"])
        assert os.path.exists(res["markdown_report"])


def test_deployment_coordinator_simulate_failure_and_rollback():
    coordinator = DeploymentCoordinator(
        service_name="secure-cloud-service",
        current_version="v1.1.0"
    )

    result = coordinator.deploy("v1.2.0-bad", simulate_failure=True)

    assert result["status"] == "ROLLED_BACK"
    assert result["rollback_triggered"] is True
    assert result["active_version"] == "v1.1.0"
    assert "INC-ROLLBACK-" in result["rollback_details"]["incident_id"]


def test_deployment_health_probe_invalid_host():
    probe = DeploymentHealthProbe(base_url="http://127.0.0.1:59999", timeout_sec=0.2)
    res = probe.probe_single("/healthz")
    assert res["healthy"] is False
    assert res["error"] is not None
