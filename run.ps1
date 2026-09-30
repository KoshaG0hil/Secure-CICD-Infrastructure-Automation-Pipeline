# ==============================================================================
# SECURE CI/CD & INFRASTRUCTURE AUTOMATION - POWERSHELL RUNNER
# ==============================================================================

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "   🔒 SECURE CI/CD & INFRASTRUCTURE AUTOMATION PIPELINE RUNNER" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Select an action to execute:" -ForegroundColor Yellow
Write-Host "  [1] Run Full End-to-End Pipeline (Happy Path)" -ForegroundColor White
Write-Host "  [2] Simulate Canary Failure & Test Automated Rollback Engine" -ForegroundColor White
Write-Host "  [3] Run Shift-Left Security & CIS IaC Policy Audit" -ForegroundColor White
Write-Host "  [4] Launch Interactive Web Dashboard (Streamlit)" -ForegroundColor White
Write-Host "  [5] Run Full Pytest Test Suite" -ForegroundColor White
Write-Host "  [6] Validate Terraform Modules" -ForegroundColor White
Write-Host "  [Q] Quit" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter option [1-6, Q]"

switch ($choice) {
    "1" {
        Write-Host "`n--> Executing Full Secure Pipeline..." -ForegroundColor Green
        python -m src.pipeline.cli run-all
    }
    "2" {
        Write-Host "`n--> Simulating Fault Injection & Automated Rollback..." -ForegroundColor Yellow
        python -m src.pipeline.cli simulate-rollback
    }
    "3" {
        Write-Host "`n--> Running Shift-Left Security Audit..." -ForegroundColor Magenta
        python -m src.pipeline.cli security-audit
    }
    "4" {
        Write-Host "`n--> Launching Streamlit Web Dashboard..." -ForegroundColor Cyan
        streamlit run src/dashboard/app.py
    }
    "5" {
        Write-Host "`n--> Running Unit & Integration Tests..." -ForegroundColor Blue
        python -m pytest -v
    }
    "6" {
        Write-Host "`n--> Validating Terraform IaC..." -ForegroundColor Green
        terraform -chdir=terraform fmt -check
        terraform -chdir=terraform validate
    }
    default {
        Write-Host "Exiting." -ForegroundColor Gray
    }
}
