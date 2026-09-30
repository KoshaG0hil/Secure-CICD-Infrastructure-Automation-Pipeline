output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "alb_dns_name" {
  description = "Public URL/DNS name for the deployed application load balancer"
  value       = module.alb.alb_dns_name
}

output "ecr_repository_url" {
  description = "ECR image repository URL"
  value       = module.ecr.repository_url
}

output "ecs_cluster_name" {
  description = "ECS Cluster Name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS Service Name"
  value       = module.ecs.service_name
}

output "log_bucket_name" {
  description = "Encrypted Audit Log Bucket Name"
  value       = module.security.log_bucket_name
}
