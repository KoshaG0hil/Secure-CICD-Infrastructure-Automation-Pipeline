# ==============================================================================
# SECURE AWS ECS FARGATE MODULE
# Features: Non-root user, Read-Only Filesystem, Container Insights, Zero-Downtime Rollout
# Compliance: CIS AWS Benchmark ECS & Docker Standards
# ==============================================================================

# ECS Cluster with Container Insights (CIS requirement)
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name       = "${var.project_name}-${var.environment}-cluster"
    Compliance = "CIS-AWS-ECS"
  }
}

# CloudWatch Log Group for Application Logs
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = 30

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-logs"
  }
}

# ECS Task Definition (Hardened Security Profile)
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-${var.environment}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name         = "app"
      image        = var.container_image
      essential    = true
      user         = "10001" # CIS-AWS-ECS-001: Enforce unprivileged user
      privileged   = false
      readonlyRootFilesystem = true # CIS-AWS-ECS-002: Read-only container root

      linuxParameters = {
        capabilities = {
          drop = ["ALL"]
        }
      }

      portMappings = [
        {
          containerPort = var.app_port
          hostPort      = var.app_port
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "PORT", value = tostring(var.app_port) },
        { name = "APP_NAME", value = var.project_name }
      ]

      mountPoints = [
        {
          sourceVolume  = "tmp-volume"
          containerPath = "/tmp"
          readOnly      = false
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://127.0.0.1:${var.app_port}/healthz || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 10
      }
    }
  ])

  # Ephemeral volume for safe read-only filesystem runtime operations
  volume {
    name = "tmp-volume"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-task-def"
  }
}

# ECS Service with Zero-Downtime Rolling Update & Rollback support
resource "aws_ecs_service" "app" {
  name                              = "${var.project_name}-${var.environment}-svc"
  cluster                           = aws_ecs_cluster.main.id
  task_definition                   = aws_ecs_task_definition.app.arn
  desired_count                     = var.app_count
  launch_type                       = "FARGATE"
  platform_version                  = "LATEST"
  health_check_grace_period_seconds = 30

  # Rolling deployment strategy
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    security_groups  = [var.security_group_id]
    subnets          = var.private_subnet_ids
    assign_public_ip = false # Strictly private network isolation
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "app"
    container_port   = var.app_port
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-service"
  }

  depends_on = [var.target_group_arn]
}
