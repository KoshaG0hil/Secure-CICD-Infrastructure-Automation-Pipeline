variable "aws_region" {
  description = "The AWS Region where resources will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (staging or production)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Name prefix for all project infrastructure resources"
  type        = string
  default     = "secure-pipeline-app"
}

variable "vpc_cidr" {
  description = "CIDR block for the main VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "app_port" {
  description = "Application listening port"
  type        = number
  default     = 8080
}

variable "app_count" {
  description = "Number of ECS task replicas to maintain"
  type        = number
  default     = 2
}

variable "container_image" {
  description = "Full URI or tag of container image to deploy"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/secure-pipeline-app:v1.2.0"
}
