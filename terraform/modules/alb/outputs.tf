output "alb_arn" {
  description = "ARN of Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "Public DNS name of the Load Balancer"
  value       = aws_lb.main.dns_name
}

output "target_group_arn" {
  description = "ARN of the application target group"
  value       = aws_lb_target_group.app.arn
}
