"""
Tests for Security Modules: Secret Scanner, SAST Analyzer, Dependency Scanner, and IaC Validator
"""

import os
import tempfile
import pytest
from src.security.secret_scanner import SecretScanner
from src.security.sast_analyzer import SASTAnalyzer
from src.security.dependency_scanner import DependencyScanner
from src.security.iac_validator import IaCPolicyValidator


def test_secret_scanner_clean_repo():
    scanner = SecretScanner(".")
    results = scanner.scan()
    assert results["passed"] is True
    assert results["violations_found"] == 0


def test_secret_scanner_detects_leak():
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_file = os.path.join(tmpdir, "config.py")
        with open(fake_file, "w") as f:
            f.write('aws_key = "AKIAIOSFODNN7EXAMPLE"\n')

        scanner = SecretScanner(tmpdir)
        results = scanner.scan()
        assert results["passed"] is False
        assert results["violations_found"] >= 1
        assert results["findings"][0]["rule_id"] == "AWS-ACCESS-KEY"


def test_sast_analyzer_clean_src():
    analyzer = SASTAnalyzer("src")
    results = analyzer.analyze()
    assert results["passed"] is True
    assert results["critical"] == 0
    assert results["high"] == 0


def test_sast_analyzer_detects_eval():
    with tempfile.TemporaryDirectory() as tmpdir:
        insecure_file = os.path.join(tmpdir, "vuln.py")
        with open(insecure_file, "w") as f:
            f.write('def run_code(user_input):\n    return eval(user_input)\n')

        analyzer = SASTAnalyzer(tmpdir)
        results = analyzer.analyze()
        assert results["passed"] is False
        assert results["critical"] >= 1
        assert any(i["id"] == "SEC-SAST-001" for i in results["issues"])


def test_dependency_scanner():
    scanner = DependencyScanner("requirements.txt")
    results = scanner.scan()
    assert results["passed"] is True
    assert results["unpinned_count"] == 0
    assert len(results["vulnerabilities"]) == 0


def test_iac_policy_validator_on_terraform():
    validator = IaCPolicyValidator("terraform")
    results = validator.validate()
    assert results["passed"] is True
    assert results["compliance_score"] >= 90
    assert results["critical_violations"] == 0
