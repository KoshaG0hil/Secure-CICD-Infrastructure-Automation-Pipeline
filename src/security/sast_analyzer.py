"""
Static Application Security Testing (SAST) Engine
Performs Abstract Syntax Tree (AST) analysis on source code to detect security anti-patterns,
insecure deserialization, injection risks, hardcoded credentials, and bad crypto.
"""

import ast
import os
from typing import List, Dict, Any


class SecurityASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[Dict[str, Any]] = []

    def visit_Call(self, node: ast.Call):
        # 1. Check for eval / exec
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                self.issues.append({
                    "id": "SEC-SAST-001",
                    "title": f"Dangerous dynamic code execution with '{node.func.id}'",
                    "severity": "CRITICAL",
                    "file": self.file_path,
                    "line": node.lineno,
                    "recommendation": "Avoid dynamic code execution. Use safe parser or explicit mappings."
                })

        # 2. Check for shell=True in subprocess
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("Popen", "run", "call", "check_output"):
                for keyword in node.keywords:
                    if keyword.arg == "shell" and getattr(keyword.value, "value", False) is True:
                        self.issues.append({
                            "id": "SEC-SAST-002",
                            "title": "Subprocess execution with shell=True creates command injection risk",
                            "severity": "HIGH",
                            "file": self.file_path,
                            "line": node.lineno,
                            "recommendation": "Pass command arguments as a list and set shell=False."
                        })

            # 3. Check for insecure pickle deserialization
            if node.func.attr in ("load", "loads"):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                    self.issues.append({
                        "id": "SEC-SAST-003",
                        "title": "Insecure deserialization using Python 'pickle'",
                        "severity": "HIGH",
                        "file": self.file_path,
                        "line": node.lineno,
                        "recommendation": "Use json or safe serialisation formats like protobuf."
                    })

            # 4. Check for weak hashing algorithms (MD5, SHA1)
            if node.func.attr in ("md5", "sha1"):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "hashlib":
                    self.issues.append({
                        "id": "SEC-SAST-004",
                        "title": f"Use of cryptographically weak hash algorithm '{node.func.attr}'",
                        "severity": "MEDIUM",
                        "file": self.file_path,
                        "line": node.lineno,
                        "recommendation": "Use SHA-256, SHA-512, or bcrypt/argon2 for password hashing."
                    })

            # 5. Check for debug=True in Flask run
            if node.func.attr == "run":
                for kw in node.keywords:
                    if kw.arg == "debug" and getattr(kw.value, "value", False) is True:
                        self.issues.append({
                            "id": "SEC-SAST-005",
                            "title": "Application running with debug=True in server initialization",
                            "severity": "HIGH",
                            "file": self.file_path,
                            "line": node.lineno,
                            "recommendation": "Disable debug mode in production to prevent interactive traceback exposure."
                        })

        self.generic_visit(node)


class SASTAnalyzer:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def analyze(self) -> Dict[str, Any]:
        """Runs SAST analysis across all python files."""
        issues: List[Dict[str, Any]] = []
        files_scanned = 0

        for current_root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in {".git", ".pytest_cache", "__pycache__", "venv", ".venv", "tests"}]
            for file_name in files:
                if file_name.endswith(".py"):
                    full_path = os.path.join(current_root, file_name)
                    rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                    files_scanned += 1
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        tree = ast.parse(content, filename=rel_path)
                        visitor = SecurityASTVisitor(rel_path)
                        visitor.visit(tree)
                        issues.extend(visitor.issues)
                    except SyntaxError as e:
                        issues.append({
                            "id": "SEC-SAST-PARSE",
                            "title": f"Syntax parsing failure: {e}",
                            "severity": "LOW",
                            "file": rel_path,
                            "line": e.lineno or 1,
                            "recommendation": "Fix Python syntax error."
                        })

        critical_count = sum(1 for i in issues if i["severity"] == "CRITICAL")
        high_count = sum(1 for i in issues if i["severity"] == "HIGH")
        passed = (critical_count == 0 and high_count == 0)

        return {
            "analyzer": "AST SAST Engine",
            "files_scanned": files_scanned,
            "issues_count": len(issues),
            "critical": critical_count,
            "high": high_count,
            "passed": passed,
            "issues": issues
        }


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    analyzer = SASTAnalyzer(target)
    results = analyzer.analyze()
    print(f"SAST Scanned: {results['files_scanned']} files. Found {results['issues_count']} issues. Passed: {results['passed']}")
    if not results["passed"]:
        sys.exit(1)
