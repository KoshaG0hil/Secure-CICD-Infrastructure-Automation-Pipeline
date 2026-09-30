# ==============================================================================
# SECURE APPLICATION LOAD BALANCER MODULE
# Features: WAF Protection, Strict Header Dropping, Access Logging, Health Checks
# Compliance: CIS AWS Benchmark ALB Standards
# ==============================================================================

resource "aws_lb" "main" {
  name                       = "${var.project_name}-${var.environment}-alb"
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [var.security_group_id]
  subnets                    = var.public_subnet_ids
  enable_deletion_protection = false # Set true for strict production

  # Drop invalid HTTP headers to prevent request smuggling (CIS-AWS-ALB-001)
  drop_invalid_header_fields = true

  access_logs {
    bucket  = var.log_bucket_name
    prefix  = "alb-logs"
    enabled = true
  }

  tags = {
    Name       = "${var.project_name}-${var.environment}-alb"
    Compliance = "CIS-AWS-ALB"
  }
}

resource "aws_lb_target_group" "app" {
  name        = "${var.project_name}-${var.environment}-tg"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/healthz"
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    protocol            = "HTTP"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-tg"
  }
}

# HTTP Listener - routes to target group (or redirects to 443 with TLS cert)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Attach WAFv2 Web ACL to ALB
resource "aws_wafv2_web_acl_association" "alb_waf" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = var.waf_web_acl_arn
}
