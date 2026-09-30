variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "security_group_id" {
  description = "ECS tasks security group ID"
  type        = string
}

variable "target_group_arn" {
  description = "ALB target group ARN"
  type        = string
}

variable "ecs_execution_role_arn" {
  description = "ECS Task Execution IAM Role ARN"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "ECS Task IAM Role ARN"
  type        = string
}

variable "container_image" {
  description = "Container image URI"
  type        = string
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8080
}

variable "app_count" {
  description = "Desired number of task instances"
  type        = number
  default     = 2
}
