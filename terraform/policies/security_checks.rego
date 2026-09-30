# ==============================================================================
# Open Policy Agent (OPA) / Conftest Rego Policies for Terraform Plan
# Enforces CIS AWS Foundations Benchmark & Zero-Trust Cloud Guardrails
# ==============================================================================

package terraform.security

default allow = false

# Allow deployment only if there are zero critical policy violations
allow {
    count(deny) == 0
}

# Deny any Security Group rule allowing 0.0.0.0/0 on SSH (22)
deny[msg] {
    some resource in input.resource_changes
    resource.type == "aws_security_group_rule"
    resource.change.after.cidr_blocks[_] == "0.0.0.0/0"
    resource.change.after.from_port <= 22
    resource.change.after.to_port >= 22
    msg := sprintf("CIS-VIOLATION: Security group rule '%v' exposes SSH port 22 directly to 0.0.0.0/0", [resource.name])
}

# Deny S3 bucket creation without public access block
deny[msg] {
    some resource in input.resource_changes
    resource.type == "aws_s3_bucket"
    not has_public_access_block(resource.address)
    msg := sprintf("CIS-VIOLATION: S3 bucket '%v' lacks an attached aws_s3_bucket_public_access_block", [resource.address])
}

# Deny ECS Task Definition running as root
deny[msg] {
    some resource in input.resource_changes
    resource.type == "aws_ecs_task_definition"
    container := resource.change.after.container_definitions[_]
    container.user == "root"
    msg := sprintf("CIS-VIOLATION: ECS task definition '%v' runs container with root UID", [resource.name])
}

# Helper check
has_public_access_block(bucket_address) {
    some block in input.resource_changes
    block.type == "aws_s3_bucket_public_access_block"
}
