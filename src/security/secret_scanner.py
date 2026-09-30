"""
Enterprise Secret Scanning Engine
Scans repository code, configurations, and IaC files for exposed secrets,
credentials, API tokens, and cryptographic keys before git commits or deployments.
"""

import os
import re
from typing import List, Dict, Any


SECRET_PATTERNS = [
    {
        "id": "AWS-ACCESS-KEY",
        "name": "AWS Access Key ID",
        "pattern": r"(?i)\b((?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16})\b",
        "severity": "CRITICAL"
    },
    {
        "id": "AWS-SECRET-KEY",
        "name": "AWS Secret Access Key",
        "pattern": r"(?i)aws_secret_access_key\s*=\s*['\"]([0-9a-zA-Z/+]{40})['\"]",
        "severity": "CRITICAL"
    },
    {
        "id": "GITHUB-TOKEN",
        "name": "GitHub Personal Access Token",
        "pattern": r"\b(ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})\b",
        "severity": "CRITICAL"
    },
    {
        "id": "PRIVATE-KEY",
        "name": "Unencrypted Private Key Header",
        "pattern": r"-----BEGIN (?:RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----",
        "severity": "CRITICAL"
    },
    {
        "id": "SLACK-WEBHOOK",
        "name": "Slack Webhook URL",
        "pattern": r"https://hooks\.slack\.com/services/T[0-9A-Za-z]{8}/B[0-9A-Za-z]{8}/[0-9A-Za-z]{24}",
        "severity": "HIGH"
    },
    {
        "id": "DATABASE-CREDENTIALS",
        "name": "Hardcoded Database Connection String",
        "pattern": r"(?:postgres|mysql|mongodb)://(?:[a-zA-Z0-9_-]+):([a-zA-Z0-9_!@#$%^&*()-]+)@[a-zA-Z0-9.-]+:\d+/[a-zA-Z0-9_-]+",
        "severity": "HIGH"
    }
]

IGNORE_DIRS = {
    ".git", ".pytest_cache", "__pycache__", "venv", ".venv",
    "node_modules", ".terraform", "reports", "assets"
}

IGNORE_EXTENSIONS = {
    ".pyc", ".png", ".jpg", ".jpeg", ".svg", ".zip", ".tar", ".gz", ".tfstate"
}


class SecretScanner:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def scan(self) -> Dict[str, Any]:
        """Scans the repository directory for exposed secrets."""
        findings: List[Dict[str, Any]] = []
        files_scanned = 0

        for current_root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file_name in files:
                ext = os.path.splitext(file_name)[1].lower()
                if ext in IGNORE_EXTENSIONS:
                    continue

                file_path = os.path.join(current_root, file_name)
                rel_path = os.path.relpath(file_path, self.root_dir)

                # Skip tests containing test fixtures or scanner definition itself
                if "secret_scanner.py" in file_name or "test_security.py" in file_name:
                    continue

                files_scanned += 1
                file_findings = self._scan_file(file_path, rel_path)
                findings.extend(file_findings)

        passed = len(findings) == 0
        return {
            "scanner": "Enterprise Secret Scanner",
            "files_scanned": files_scanned,
            "violations_found": len(findings),
            "passed": passed,
            "findings": findings
        }

    def _scan_file(self, file_path: str, rel_path: str) -> List[Dict[str, Any]]:
        file_findings = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, start=1):
                    for rule in SECRET_PATTERNS:
                        match = re.search(rule["pattern"], line)
                        if match:
                            # Redact sensitive match
                            matched_text = match.group(0)
                            redacted = matched_text[:4] + "*" * (len(matched_text) - 8) + matched_text[-4:] if len(matched_text) > 8 else "***REDACTED***"
                            file_findings.append({
                                "rule_id": rule["id"],
                                "rule_name": rule["name"],
                                "severity": rule["severity"],
                                "file": rel_path.replace("\\", "/"),
                                "line": line_num,
                                "match_preview": redacted
                            })
        except Exception:
            pass
        return file_findings


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    scanner = SecretScanner(target)
    results = scanner.scan()
    print(f"Scanned {results['files_scanned']} files. Found {results['violations_found']} secrets. Status: {'PASSED' if results['passed'] else 'FAILED'}")
    if not results["passed"]:
        sys.exit(1)
