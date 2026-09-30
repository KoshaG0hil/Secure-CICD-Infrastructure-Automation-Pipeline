@echo off
setlocal
title Secure CI/CD & Infrastructure Automation Pipeline

echo ==================================================================
echo    SECURE CI/CD ^& INFRASTRUCTURE AUTOMATION PIPELINE RUNNER
echo ==================================================================
echo.
echo Select an action to execute:
echo   [1] Run Full End-to-End Pipeline (Happy Path)
echo   [2] Simulate Canary Failure ^& Test Automated Rollback Engine
echo   [3] Run Shift-Left Security ^& CIS IaC Policy Audit
echo   [4] Launch Interactive Web Dashboard (Streamlit)
echo   [5] Run Full Pytest Test Suite
echo   [6] Validate Terraform Modules
echo   [Q] Quit
echo.

set /p choice="Enter option [1-6, Q]: "

if "%choice%"=="1" (
    echo.
    echo --^> Executing Full Secure Pipeline...
    python -m src.pipeline.cli run-all
    goto end
)
if "%choice%"=="2" (
    echo.
    echo --^> Simulating Fault Injection ^& Automated Rollback...
    python -m src.pipeline.cli simulate-rollback
    goto end
)
if "%choice%"=="3" (
    echo.
    echo --^> Running Shift-Left Security Audit...
    python -m src.pipeline.cli security-audit
    goto end
)
if "%choice%"=="4" (
    echo.
    echo --^> Launching Streamlit Web Dashboard...
    streamlit run src\dashboard\app.py
    goto end
)
if "%choice%"=="5" (
    echo.
    echo --^> Running Unit ^& Integration Tests...
    python -m pytest -v
    goto end
)
if "%choice%"=="6" (
    echo.
    echo --^> Validating Terraform IaC...
    terraform -chdir=terraform fmt -check
    terraform -chdir=terraform validate
    goto end
)

:end
echo.
pause
