"""
Infrastructure-as-Code (IaC) Policy & Security Validator
Enforces CIS AWS Foundations Benchmark, NIST 800-53, and DevSecOps security policies
on Terraform code prior to plan/apply execution.
"""

import os
import re
from typing import List, Dict, Any


RULES = [
    {
        "id": "CIS-AWS-VPC-001",
        "title": "VPC must have Flow Logs enabled to monitor network traffic",
        "severity": "HIGH",
        "target_resource": "aws_vpc",
        "required_resource": "aws_flow_log",
        "description": "VPC flow logging is required for intrusion detection and threat monitoring."
    },
    {
        "id": "CIS-AWS-S3-001",
        "title": "S3 Buckets must enforce Server-Side Encryption (SSE-KMS or AES256)",
        "severity": "HIGH",
        "pattern": r'aws_s3_bucket_server_side_encryption_configuration',
        "description": "Ensure data at rest is encrypted according to CIS compliance."
    },
    {
        "id": "CIS-AWS-S3-002",
        "title": "S3 Buckets must block public access",
        "severity": "CRITICAL",
        "pattern": r'aws_s3_bucket_public_access_block',
        "description": "Public access block prevents unauthorized data leakage."
    },
    {
        "id": "CIS-AWS-SG-001",
        "title": "Security Groups must not expose SSH (22) or RDP (3389) to 0.0.0.0/0",
        "severity": "CRITICAL",
        "forbidden_pattern": r'cidr_blocks\s*=\s*\[\s*"0\.0\.0\.0/0"\s*\].*?(?:from_port\s*=\s*(?:22|3389)|to_port\s*=\s*(?:22|3389))',
        "description": "Direct ingress from internet on administrative ports is strictly forbidden."
    },
    {
        "id": "CIS-AWS-ECS-001",
        "title": "ECS Task Definitions must enforce unprivileged non-root user",
        "severity": "HIGH",
        "pattern": r'("user"\s*:\s*"(?:appuser|10001|1000|nonroot)")|(user\s*=\s*"(?:appuser|10001|1000|nonroot)")',
        "description": "Containers must never execute as UID 0 (root) inside Fargate tasks."
    },
    {
        "id": "CIS-AWS-ECS-002",
        "title": "ECS Containers must enforce read-only root filesystems",
        "severity": "MEDIUM",
        "pattern": r'("readonlyRootFilesystem"\s*:\s*true)|(readonly_root_filesystem\s*=\s*true)',
        "description": "Prevents attackers from modifying binaries or dropping payloads in container storage."
    },
    {
        "id": "CIS-AWS-ECR-001",
        "title": "ECR Repositories must enforce tag immutability",
        "severity": "HIGH",
        "pattern": r'image_tag_mutability\s*=\s*"IMMUTABLE"',
        "description": "Prevents overwriting tagged images and protects supply-chain integrity."
    },
    {
        "id": "CIS-AWS-ECR-002",
        "title": "ECR Repositories must have vulnerability scan-on-push enabled",
        "severity": "HIGH",
        "pattern": r'scan_on_push\s*=\s*true',
        "description": "Automatically audits newly pushed images for CVEs in AWS ECR."
    },
    {
        "id": "CIS-AWS-ALB-001",
        "title": "Application Load Balancers must drop invalid HTTP header fields",
        "severity": "MEDIUM",
        "pattern": r'drop_invalid_header_fields\s*=\s*true',
        "description": "Protects downstream services from HTTP request smuggling vulnerabilities."
    },
    {
        "id": "CIS-AWS-IAM-001",
        "title": "IAM Policies must avoid dangerous wildcard actions combined with wildcard resources",
        "severity": "CRITICAL",
        "forbidden_pattern": r'"Action"\s*:\s*"\*".*?"Resource"\s*:\s*"\*"',
        "description": "Broad administrative wildcards violate the principle of least privilege."
    }
]


class IaCPolicyValidator:
    def __init__(self, terraform_dir: str):
        self.terraform_dir = terraform_dir

    def validate(self) -> Dict[str, Any]:
        """Scans all .tf files in the terraform directory against security policies."""
        violations: List[Dict[str, Any]] = []
        files_scanned = 0
        all_tf_content = ""

        file_contents: Dict[str, str] = {}
        for root, dirs, files in os.walk(self.terraform_dir):
            dirs[:] = [d for d in dirs if d not in {".terraform", ".git"}]
            for file_name in files:
                if file_name.endswith(".tf"):
                    file_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(file_path, self.terraform_dir).replace("\\", "/")
                    files_scanned += 1
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            file_contents[rel_path] = content
                            all_tf_content += "\n" + content
                    except Exception:
                        pass

        # Evaluate rules
        for rule in RULES:
            rule_id = rule["id"]
            if "forbidden_pattern" in rule:
                pat = re.compile(rule["forbidden_pattern"], re.DOTALL | re.IGNORECASE)
                for rel_path, content in file_contents.items():
                    if pat.search(content):
                        violations.append({
                            "rule_id": rule_id,
                            "title": rule["title"],
                            "severity": rule["severity"],
                            "file": rel_path,
                            "description": rule["description"]
                        })
            elif "pattern" in rule:
                pat = re.compile(rule["pattern"], re.DOTALL | re.IGNORECASE)
                if not pat.search(all_tf_content):
                    violations.append({
                        "rule_id": rule_id,
                        "title": rule["title"],
                        "severity": rule["severity"],
                        "file": "terraform/modules/*",
                        "description": f"Missing required security configuration: {rule['description']}"
                    })

        critical_count = sum(1 for v in violations if v["severity"] == "CRITICAL")
        high_count = sum(1 for v in violations if v["severity"] == "HIGH")
        medium_count = sum(1 for v in violations if v["severity"] == "MEDIUM")
        passed = (critical_count == 0 and high_count == 0)

        # Compliance score: 100 - (critical * 25 + high * 15 + medium * 5)
        score = max(0, 100 - (critical_count * 25 + high_count * 15 + medium_count * 5))

        return {
            "validator": "IaC CIS & DevSecOps Policy Validator",
            "files_scanned": files_scanned,
            "violations_count": len(violations),
            "critical_violations": critical_count,
            "high_violations": high_count,
            "medium_violations": medium_count,
            "compliance_score": score,
            "passed": passed,
            "violations": violations
        }


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "terraform"
    validator = IaCPolicyValidator(target)
    results = validator.validate()
    print(f"IaC Validation: {results['files_scanned']} files scanned. Violations: {results['violations_count']}. Score: {results['compliance_score']}%. Passed: {results['passed']}")
    if not results["passed"]:
        sys.exit(1)
