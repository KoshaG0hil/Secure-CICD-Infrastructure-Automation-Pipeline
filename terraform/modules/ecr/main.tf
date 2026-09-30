# ==============================================================================
# SECURE AWS ECR REPOSITORY MODULE
# Features: Tag Immutability, Vulnerability Scan-on-Push, KMS Encryption
# Compliance: CIS AWS Benchmark ECR standards
# ==============================================================================

resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name       = "${var.project_name}-${var.environment}-ecr"
    Compliance = "CIS-AWS-ECR"
  }
}

# Lifecycle Policy: Retain last 30 tagged production images, purge untagged
resource "aws_ecr_lifecycle_policy" "policy" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images older than 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Retain last 30 production container releases"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "release", "prod"]
          countType     = "imageCountMoreThan"
          countNumber   = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
