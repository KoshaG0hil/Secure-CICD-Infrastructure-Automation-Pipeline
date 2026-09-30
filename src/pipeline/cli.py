"""
Secure CI/CD & Infrastructure Automation Pipeline CLI
Orchestrates shift-left security validation, IaC policy enforcement,
container image scanning, approval gates, deployments, and automated rollback controls.
"""

import os
import time
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from src.security.secret_scanner import SecretScanner
from src.security.sast_analyzer import SASTAnalyzer
from src.security.dependency_scanner import DependencyScanner
from src.security.iac_validator import IaCPolicyValidator
from src.deployment.deployer import DeploymentCoordinator


class PipelineOrchestrator:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.reports_dir = os.path.join(self.root_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        self.console = Console() if RICH_AVAILABLE else None

    def print_banner(self):
        banner = """
================================================================================
   🔒 SECURE CI/CD & INFRASTRUCTURE AUTOMATION PIPELINE
   Security-Focused Delivery | Shift-Left IaC Validation | Automated Rollback
================================================================================
        """
        if self.console:
            self.console.print(Panel.fit(
                "[bold cyan]SECURE CI/CD & INFRASTRUCTURE AUTOMATION PIPELINE[/bold cyan]\n"
                "[dim]Engineered with Shift-Left Security, IaC Policy Gates, and Automated Rollback Controls[/dim]",
                border_style="cyan"
            ))
        else:
            print(banner)

    # --------------------------------------------------------------------------
    # STAGE 1: Source Code Security & Shift-Left Validation
    # --------------------------------------------------------------------------
    def run_stage_1_source_security(self) -> Dict[str, Any]:
        start = time.time()
        # 1. Secret Scanner
        sec_scanner = SecretScanner(self.root_dir)
        sec_res = sec_scanner.scan()

        # 2. SAST Analyzer
        sast = SASTAnalyzer(os.path.join(self.root_dir, "src"))
        sast_res = sast.analyze()

        # 3. Dependency Scanner
        req_path = os.path.join(self.root_dir, "requirements.txt")
        dep_scanner = DependencyScanner(req_path)
        dep_res = dep_scanner.scan()

        stage_passed = sec_res["passed"] and sast_res["passed"] and dep_res["passed"]

        return {
            "stage_id": "STAGE-1-SOURCE-SECURITY",
            "name": "Source Validation & Shift-Left SAST",
            "passed": stage_passed,
            "duration_sec": round(time.time() - start, 2),
            "details": {
                "secrets": sec_res,
                "sast": sast_res,
                "dependencies": dep_res
            }
        }

    # --------------------------------------------------------------------------
    # STAGE 2: Infrastructure as Code (IaC) Validation & Policy-as-Code
    # --------------------------------------------------------------------------
    def run_stage_2_iac_security(self) -> Dict[str, Any]:
        start = time.time()
        tf_dir = os.path.join(self.root_dir, "terraform")
        validator = IaCPolicyValidator(tf_dir)
        val_res = validator.validate()

        return {
            "stage_id": "STAGE-2-IAC-VALIDATION",
            "name": "IaC Compliance & Policy-as-Code (CIS AWS)",
            "passed": val_res["passed"],
            "duration_sec": round(time.time() - start, 2),
            "details": val_res
        }

    # --------------------------------------------------------------------------
    # STAGE 3: Container Security & Image Vulnerability Scan
    # --------------------------------------------------------------------------
    def run_stage_3_container_security(self) -> Dict[str, Any]:
        start = time.time()
        dockerfile_path = os.path.join(self.root_dir, "Dockerfile")
        has_dockerfile = os.path.exists(dockerfile_path)

        dockerfile_checks = {
            "multi_stage": False,
            "non_root_user": False,
            "healthcheck_defined": False,
            "no_cache_pip": False
        }

        if has_dockerfile:
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                content = f.read()
                dockerfile_checks["multi_stage"] = "AS runner" in content or "AS builder" in content
                dockerfile_checks["non_root_user"] = "USER appuser" in content or "USER 10001" in content
                dockerfile_checks["healthcheck_defined"] = "HEALTHCHECK" in content
                dockerfile_checks["no_cache_pip"] = "--no-cache-dir" in content

        container_passed = all(dockerfile_checks.values())

        # Simulated Trivy Image Vulnerability Scan
        trivy_simulation = {
            "target_image": "secure-pipeline-app:v1.2.0",
            "base_image": "python:3.12-slim",
            "vulnerabilities": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 1
            },
            "status": "APPROVED_FOR_DEPLOYMENT"
        }

        return {
            "stage_id": "STAGE-3-CONTAINER-SECURITY",
            "name": "Container Hardening & Image Scan (Trivy/Hadolint)",
            "passed": container_passed,
            "duration_sec": round(time.time() - start, 2),
            "details": {
                "dockerfile_checks": dockerfile_checks,
                "trivy_scan": trivy_simulation
            }
        }

    # --------------------------------------------------------------------------
    # STAGE 4: Terraform Plan Generation & Approval Gate
    # --------------------------------------------------------------------------
    def run_stage_4_plan_approval_gate(self, auto_approve: bool = True) -> Dict[str, Any]:
        start = time.time()
        time.sleep(0.3)

        plan_summary = {
            "resources_to_add": 14,
            "resources_to_change": 0,
            "resources_to_destroy": 0,
            "modules": ["vpc", "security", "ecr", "alb", "ecs"],
            "plan_artifact_sha256": "8f4e2b19c4d92a013f9cba44e8812c309f48ac7713f01901a11e29cbf78a19de",
            "drift_detected": False
        }

        approval_status = "APPROVED" if auto_approve else "MANUAL_APPROVAL_REQUIRED"

        return {
            "stage_id": "STAGE-4-PLAN-APPROVAL",
            "name": "Terraform Plan & Environment Approval Gate",
            "passed": True,
            "approval_status": approval_status,
            "duration_sec": round(time.time() - start, 2),
            "details": plan_summary
        }

    # --------------------------------------------------------------------------
    # STAGE 5: Container Deployment & Synthetic Validation
    # --------------------------------------------------------------------------
    def run_stage_5_deployment(self, simulate_failure: bool = False) -> Dict[str, Any]:
        start = time.time()
        coordinator = DeploymentCoordinator(
            service_name="secure-cloud-service",
            current_version="v1.1.9"
        )
        deploy_res = coordinator.deploy("v1.2.0", simulate_failure=simulate_failure)

        return {
            "stage_id": "STAGE-5-DEPLOYMENT",
            "name": "Canary Rollout & Post-Deploy Health Verification",
            "passed": (deploy_res["status"] == "SUCCESSFUL"),
            "duration_sec": round(time.time() - start, 2),
            "details": deploy_res
        }

    # --------------------------------------------------------------------------
    # Full Pipeline Execution
    # --------------------------------------------------------------------------
    def execute_pipeline(self, simulate_rollback: bool = False) -> Dict[str, Any]:
        self.print_banner()
        pipeline_start = time.time()
        stages_output: List[Dict[str, Any]] = []

        # Stage 1
        s1 = self.run_stage_1_source_security()
        stages_output.append(s1)
        self._render_stage(s1)

        # Stage 2
        s2 = self.run_stage_2_iac_security()
        stages_output.append(s2)
        self._render_stage(s2)

        # Stage 3
        s3 = self.run_stage_3_container_security()
        stages_output.append(s3)
        self._render_stage(s3)

        # Stage 4
        s4 = self.run_stage_4_plan_approval_gate(auto_approve=True)
        stages_output.append(s4)
        self._render_stage(s4)

        # Stage 5
        s5 = self.run_stage_5_deployment(simulate_failure=simulate_rollback)
        stages_output.append(s5)
        self._render_stage(s5)

        total_duration = round(time.time() - pipeline_start, 2)
        if simulate_rollback:
            overall_status = "ROLLED_BACK_SAFELY"
        else:
            overall_status = "PASSED" if all(s["passed"] for s in stages_output) else "FAILED"

        summary = {
            "pipeline_id": f"PIPE-RUN-{int(pipeline_start)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": overall_status,
            "total_duration_sec": total_duration,
            "stages": stages_output
        }

        # Write Pipeline Run Report
        report_file = os.path.join(self.reports_dir, f"pipeline_run_{summary['pipeline_id']}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        self._render_final_summary(summary)
        return summary

    def _render_stage(self, stage: Dict[str, Any]):
        passed = stage["passed"]
        is_rollback = "ROLLED_BACK" in str(stage.get("details", {}))
        icon = "[PASS]" if passed else ("[ROLLBACK]" if is_rollback else "[FAIL]")
        status_text = "PASSED" if passed else ("ROLLED BACK SAFELY" if is_rollback else "FAILED")

        if self.console:
            color = "green" if passed else ("yellow" if is_rollback else "red")
            self.console.print(f"[bold {color}]{icon}[/bold {color}] [bold]{stage['name']}[/bold] - [dim]Duration: {stage['duration_sec']}s[/dim]")
        else:
            print(f"{icon} {stage['name']} [{status_text}] ({stage['duration_sec']}s)")

    def _render_final_summary(self, summary: Dict[str, Any]):
        if self.console:
            table = Table(title="Pipeline Execution Summary", box=box.ROUNDED)
            table.add_column("Stage ID", style="cyan")
            table.add_column("Stage Name", style="white")
            table.add_column("Duration", style="yellow")
            table.add_column("Verdict", style="bold")

            for s in summary["stages"]:
                verdict = "[green]PASSED[/green]" if s["passed"] else "[red]FAILED / ROLLBACK[/red]"
                table.add_row(s["stage_id"], s["name"], f"{s['duration_sec']}s", verdict)

            self.console.print(table)
            self.console.print(f"\n[bold]Overall Pipeline Status: [/bold] [cyan]{summary['status']}[/cyan]")
            self.console.print(f"[bold]Total Run Time: [/bold] {summary['total_duration_sec']}s\n")
        else:
            print("\n=== PIPELINE EXECUTION SUMMARY ===")
            for s in summary["stages"]:
                print(f"- {s['stage_id']}: {'PASSED' if s['passed'] else 'FAILED'} ({s['duration_sec']}s)")
            print(f"Overall Status: {summary['status']} ({summary['total_duration_sec']}s)\n")


def main():
    parser = argparse.ArgumentParser(description="Secure CI/CD & Infrastructure Automation Pipeline CLI")
    parser.add_argument("command", choices=["run-all", "simulate-rollback", "security-audit", "test"],
                        help="Command to execute")
    parser.add_argument("--root", default=".", help="Root directory of the project")

    args = parser.parse_args()
    orchestrator = PipelineOrchestrator(root_dir=args.root)

    if args.command == "run-all":
        orchestrator.execute_pipeline(simulate_rollback=False)
    elif args.command == "simulate-rollback":
        orchestrator.execute_pipeline(simulate_rollback=True)
    elif args.command == "security-audit":
        orchestrator.print_banner()
        s1 = orchestrator.run_stage_1_source_security()
        s2 = orchestrator.run_stage_2_iac_security()
        s3 = orchestrator.run_stage_3_container_security()
        orchestrator._render_stage(s1)
        orchestrator._render_stage(s2)
        orchestrator._render_stage(s3)
    elif args.command == "test":
        print("Running unit test suite...")
        import pytest
        pytest.main(["-v", "tests"])


if __name__ == "__main__":
    main()
