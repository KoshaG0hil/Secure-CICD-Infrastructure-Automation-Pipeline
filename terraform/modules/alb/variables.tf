variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs"
  type        = list(string)
}

variable "security_group_id" {
  description = "ALB security group ID"
  type        = string
}

variable "log_bucket_name" {
  description = "Name of encrypted S3 log bucket"
  type        = string
}

variable "app_port" {
  description = "Backend container application port"
  type        = number
  default     = 8080
}

variable "waf_web_acl_arn" {
  description = "ARN of WAFv2 Web ACL to associate"
  type        = string
}
