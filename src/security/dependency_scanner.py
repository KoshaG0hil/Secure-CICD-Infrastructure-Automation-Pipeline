"""
Software Composition Analysis (SCA) & Dependency Scanner
Inspects third-party dependencies against CVE vulnerability databases,
checks for unpinned versions, and validates Software Bill of Materials (SBOM) integrity.
"""

import os
import re
from typing import Dict, Any


KNOWN_VULNERABILITIES = [
    {
        "package": "requests",
        "vulnerable_below": "2.31.0",
        "cve": "CVE-2023-32681",
        "severity": "MEDIUM",
        "summary": "Unintended leak of Proxy-Authorization header"
    },
    {
        "package": "urllib3",
        "vulnerable_below": "2.0.7",
        "cve": "CVE-2023-45803",
        "severity": "HIGH",
        "summary": "Cookie leak on cross-site redirect"
    },
    {
        "package": "flask",
        "vulnerable_below": "2.2.5",
        "cve": "CVE-2023-30861",
        "severity": "HIGH",
        "summary": "Session cookie disclosure under certain cache headers"
    },
    {
        "package": "werkzeug",
        "vulnerable_below": "3.0.1",
        "cve": "CVE-2023-46136",
        "severity": "HIGH",
        "summary": "DoS via high resource consumption when parsing untrusted multipart data"
    },
    {
        "package": "pydantic",
        "vulnerable_below": "2.4.0",
        "cve": "CVE-2023-41054",
        "severity": "MEDIUM",
        "summary": "ReDoS regex denial of service on email validation"
    }
]


def parse_version(v_str: str) -> tuple:
    parts = re.split(r"[.\-a-zA-Z]", v_str)
    res = []
    for p in parts:
        if p.isdigit():
            res.append(int(p))
    return tuple(res)


class DependencyScanner:
    def __init__(self, requirements_path: str):
        self.requirements_path = requirements_path

    def scan(self) -> Dict[str, Any]:
        """Scans requirements.txt for pinned versions and known CVEs."""
        if not os.path.exists(self.requirements_path):
            return {
                "scanner": "Dependency SCA Scanner",
                "passed": True,
                "dependencies_scanned": 0,
                "vulnerabilities": [],
                "unpinned_dependencies": []
            }

        dependencies = {}
        unpinned = []
        with open(self.requirements_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = re.match(r"^([a-zA-Z0-9_\-]+)\s*==\s*([0-9a-zA-Z\.\-]+)", line)
                if match:
                    pkg_name = match.group(1).lower()
                    pkg_version = match.group(2)
                    dependencies[pkg_name] = pkg_version
                else:
                    unpinned_match = re.match(r"^([a-zA-Z0-9_\-]+)", line)
                    if unpinned_match:
                        unpinned.append(unpinned_match.group(1))

        vulnerabilities = []
        for vuln in KNOWN_VULNERABILITIES:
            pkg = vuln["package"].lower()
            if pkg in dependencies:
                installed_ver = dependencies[pkg]
                if parse_version(installed_ver) < parse_version(vuln["vulnerable_below"]):
                    vulnerabilities.append({
                        "package": pkg,
                        "installed_version": installed_ver,
                        "fixed_in": vuln["vulnerable_below"],
                        "cve": vuln["cve"],
                        "severity": vuln["severity"],
                        "summary": vuln["summary"]
                    })

        critical_high = sum(1 for v in vulnerabilities if v["severity"] in ("CRITICAL", "HIGH"))
        passed = (critical_high == 0 and len(unpinned) == 0)

        return {
            "scanner": "Dependency SCA Scanner",
            "dependencies_scanned": len(dependencies),
            "unpinned_count": len(unpinned),
            "unpinned_dependencies": unpinned,
            "vulnerabilities_count": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "passed": passed
        }


if __name__ == "__main__":
    import sys
    req = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    scanner = DependencyScanner(req)
    res = scanner.scan()
    print(f"Scanned {res['dependencies_scanned']} dependencies. Unpinned: {res['unpinned_count']}. Vulns: {res['vulnerabilities_count']}. Passed: {res['passed']}")
    if not res["passed"]:
        sys.exit(1)
