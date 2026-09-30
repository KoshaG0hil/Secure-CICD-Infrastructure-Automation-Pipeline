# 🚀 Quickstart: How to Run the Secure CI/CD Pipeline Project

This document provides step-by-step instructions to run, test, and demo the **Secure CI/CD & Infrastructure Automation Pipeline** on Windows, Linux, and macOS.

---

## ⚡ Option 1: 1-Click Interactive Menu (Recommended)

Run the script matching your operating system:

### Windows (PowerShell):
```powershell
.\run.ps1
```

### Windows (Command Prompt):
```cmd
run.bat
```

### Linux / macOS (Bash):
```bash
chmod +x run.sh
./run.sh
```

You will see an interactive terminal menu:
```
Select an action to execute:
  [1] Run Full End-to-End Pipeline (Happy Path)
  [2] Simulate Canary Failure & Test Automated Rollback Engine
  [3] Run Shift-Left Security & CIS IaC Policy Audit
  [4] Launch Interactive Web Dashboard (Streamlit)
  [5] Run Full Pytest Test Suite
  [6] Validate Terraform Modules
  [Q] Quit
```

---

## 💻 Option 2: Command Line Interface (CLI)

You can run individual CLI commands directly:

### 1. Execute Full End-to-End Secure Pipeline
Runs all 5 stages (Source Validation, IaC Compliance, Container Scanning, Plan & Approval Gate, Canary Rollout):
```bash
python -m src.pipeline.cli run-all
```

### 2. Simulate Fault Injection & Test Automated Rollback
Simulates deploying an unhealthy release and demonstrates the **Automated Rollback Engine** detecting the failure, reverting to the stable revision, and generating an incident post-mortem:
```bash
python -m src.pipeline.cli simulate-rollback
```

### 3. Run Shift-Left Security & IaC Policy Audit Only
Runs Secret Scanner, AST SAST analysis, Dependency CVE scanner, and CIS AWS Terraform validator:
```bash
python -m src.pipeline.cli security-audit
```

### 4. Run the Pytest Unit & Integration Test Suite
```bash
python -m pytest -v
```

---

## 🌐 Option 3: Launch Interactive Web Dashboard

Launch the visual Streamlit dashboard:

```bash
streamlit run src/dashboard/app.py
```

Then open your browser to `http://localhost:8501`.

### What You Can Do in the Dashboard:
- **Pipeline Overview**: Visualize the DevSecOps flow diagram and trigger full pipeline runs.
- **Security & IaC Audit**: Inspect discovered secrets, AST SAST analysis, SBOM dependencies, and Terraform compliance score.
- **Interactive Rollback Simulator**: Click the fault-injection button and watch the automated rollback engine catch the failure and restore service stability live!
- **Reports**: Read generated incident post-mortems and pipeline telemetry files.

---

## 🏗️ Option 4: Terraform Infrastructure Verification

To inspect and validate the AWS Terraform infrastructure modules:

```bash
# Verify formatting
terraform -chdir=terraform fmt -check

# Initialize modules
terraform -chdir=terraform init -backend=false

# Validate module syntax and references
terraform -chdir=terraform validate

# Run Policy-as-Code CIS compliance scanner
python -m src.security.iac_validator terraform/
```

---

## 📂 Generated Incident Reports

All incident post-mortems and pipeline run logs are saved in the `reports/` folder:
- `reports/SAMPLE_ROLLBACK_POSTMORTEM.md`: Sample rollback post-mortem report.
- `reports/incident_INC-ROLLBACK-*.json`: Machine-readable incident telemetry.
- `reports/incident_INC-ROLLBACK-*.md`: Formatted post-mortem for operations teams.
