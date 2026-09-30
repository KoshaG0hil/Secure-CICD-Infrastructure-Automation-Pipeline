variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Target deployment environment"
  type        = string
}

variable "vpc_id" {
  description = "ID of VPC"
  type        = string
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8080
}
