"""
Deployment Coordinator & Canary Rollout Engine
Manages zero-downtime rolling container updates, coordinates post-deployment health probes,
and triggers automatic rollback if health validation fails.
"""

import time
import logging
from typing import Dict, Any, Optional
from src.deployment.health_probe import DeploymentHealthProbe
from src.deployment.rollback_controller import RollbackController

logger = logging.getLogger("deployment-coordinator")


class DeploymentCoordinator:
    def __init__(
        self,
        service_name: str,
        current_version: str,
        probe_target_url: str = "http://127.0.0.1:8080"
    ):
        self.service_name = service_name
        self.current_version = current_version
        self.probe_target_url = probe_target_url
        self.probe = DeploymentHealthProbe(base_url=probe_target_url)
        self.rollback_ctrl = RollbackController(service_name=service_name)

    def deploy(self, new_version: str, simulate_failure: bool = False) -> Dict[str, Any]:
        """
        Executes deployment lifecycle:
        1. Register new revision
        2. Rollout container instances
        3. Run synthetic health verification
        4. Trigger automated rollback if unhealthy
        """
        logger.info(f"Initiating deployment: {self.service_name} [{self.current_version} -> {new_version}]")
        deployment_start = time.time()

        # Step 1: Simulate rolling task registration
        time.sleep(0.5)

        # Step 2: Health validation
        if simulate_failure:
            logger.warning("Simulated failure injected during deployment validation phase!")
            fake_probe_results = {
                "target": self.probe_target_url,
                "cycles_run": 3,
                "successful_cycles": 0,
                "success_rate_pct": 0.0,
                "consecutive_failures": 3,
                "passed": False,
                "cycle_details": [
                    {"cycle": 1, "passed": False, "liveness": {"status_code": 503, "error": "HTTP 503 Service Unavailable"}},
                    {"cycle": 2, "passed": False, "liveness": {"status_code": 503, "error": "HTTP 503 Service Unavailable"}},
                    {"cycle": 3, "passed": False, "liveness": {"status_code": 503, "error": "HTTP 503 Service Unavailable"}}
                ]
            }

            # Trigger automated rollback!
            rollback_res = self.rollback_ctrl.trigger_rollback(
                current_version=new_version,
                target_stable_version=self.current_version,
                failure_reason="Deployment health probe failed: consecutive HTTP 503 errors during rollout",
                probe_metrics=fake_probe_results
            )

            return {
                "deployment_id": f"DEP-{int(deployment_start)}",
                "status": "ROLLED_BACK",
                "new_version_attempted": new_version,
                "active_version": self.current_version,
                "duration_sec": round(time.time() - deployment_start, 2),
                "rollback_triggered": True,
                "rollback_details": rollback_res
            }

        # Happy path probe execution (or simulated success)
        probe_results = self.probe.run_health_suite(cycles=3, interval_sec=0.2)
        if not probe_results["passed"]:
            rollback_res = self.rollback_ctrl.trigger_rollback(
                current_version=new_version,
                target_stable_version=self.current_version,
                failure_reason=f"Health check failed with {probe_results['consecutive_failures']} consecutive errors",
                probe_metrics=probe_results
            )
            return {
                "deployment_id": f"DEP-{int(deployment_start)}",
                "status": "ROLLED_BACK",
                "new_version_attempted": new_version,
                "active_version": self.current_version,
                "duration_sec": round(time.time() - deployment_start, 2),
                "rollback_triggered": True,
                "rollback_details": rollback_res
            }

        # Deployment Succeeded
        self.current_version = new_version
        return {
            "deployment_id": f"DEP-{int(deployment_start)}",
            "status": "SUCCESSFUL",
            "active_version": new_version,
            "duration_sec": round(time.time() - deployment_start, 2),
            "rollback_triggered": False,
            "probe_results": probe_results
        }
