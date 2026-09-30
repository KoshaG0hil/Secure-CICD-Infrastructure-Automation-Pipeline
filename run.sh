#!/usr/bin/env bash
# ==============================================================================
# SECURE CI/CD & INFRASTRUCTURE AUTOMATION - BASH RUNNER
# ==============================================================================

set -e

echo "=================================================================="
echo "   🔒 SECURE CI/CD & INFRASTRUCTURE AUTOMATION PIPELINE RUNNER"
echo "=================================================================="
echo ""
echo "Select an action to execute:"
echo "  [1] Run Full End-to-End Pipeline (Happy Path)"
echo "  [2] Simulate Canary Failure & Test Automated Rollback Engine"
echo "  [3] Run Shift-Left Security & CIS IaC Policy Audit"
echo "  [4] Launch Interactive Web Dashboard (Streamlit)"
echo "  [5] Run Full Pytest Test Suite"
echo "  [6] Validate Terraform Modules"
echo "  [Q] Quit"
echo ""

read -p "Enter option [1-6, Q]: " choice

case "$choice" in
    1)
        echo -e "\n--> Executing Full Secure Pipeline..."
        python -m src.pipeline.cli run-all
        ;;
    2)
        echo -e "\n--> Simulating Fault Injection & Automated Rollback..."
        python -m src.pipeline.cli simulate-rollback
        ;;
    3)
        echo -e "\n--> Running Shift-Left Security Audit..."
        python -m src.pipeline.cli security-audit
        ;;
    4)
        echo -e "\n--> Launching Streamlit Web Dashboard..."
        streamlit run src/dashboard/app.py
        ;;
    5)
        echo -e "\n--> Running Unit & Integration Tests..."
        python -m pytest -v
        ;;
    6)
        echo -e "\n--> Validating Terraform IaC..."
        terraform -chdir=terraform fmt -check
        terraform -chdir=terraform validate
        ;;
    *)
        echo "Exiting."
        ;;
esac
