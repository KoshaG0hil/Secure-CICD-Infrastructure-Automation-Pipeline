output "alb_security_group_id" {
  description = "ID of ALB security group"
  value       = aws_security_group.alb_sg.id
}

output "ecs_security_group_id" {
  description = "ID of ECS tasks security group"
  value       = aws_security_group.ecs_sg.id
}

output "ecs_execution_role_arn" {
  description = "ARN of ECS execution IAM role"
  value       = aws_iam_role.ecs_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of ECS task IAM role"
  value       = aws_iam_role.ecs_task_role.arn
}

output "log_bucket_name" {
  description = "Name of encrypted S3 log bucket"
  value       = aws_s3_bucket.logs.id
}

output "waf_web_acl_arn" {
  description = "ARN of WAFv2 Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}
