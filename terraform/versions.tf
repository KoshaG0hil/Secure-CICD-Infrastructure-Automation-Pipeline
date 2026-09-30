terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Production state backend configuration with locking
  # backend "s3" {
  #   bucket         = "prod-terraform-state-secure-pipeline"
  #   key            = "infrastructure/prod/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Secure-CICD-Pipeline"
      ManagedBy   = "Terraform"
      Environment = var.environment
      Compliance  = "CIS-AWS-Benchmark"
    }
  }
}
