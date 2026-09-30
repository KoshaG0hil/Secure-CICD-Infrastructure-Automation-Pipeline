# ==============================================================================
# SECURE CI/CD & INFRASTRUCTURE AUTOMATION - ROOT TERRAFORM CONFIGURATION
# Connects VPC, Security, ECR, ALB, and ECS modules into a coherent architecture
# ==============================================================================

module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

module "security" {
  source       = "./modules/security"
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  app_port     = var.app_port
}

module "ecr" {
  source       = "./modules/ecr"
  project_name = var.project_name
  environment  = var.environment
}

module "alb" {
  source            = "./modules/alb"
  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  security_group_id = module.security.alb_security_group_id
  log_bucket_name   = module.security.log_bucket_name
  app_port          = var.app_port
  waf_web_acl_arn   = module.security.waf_web_acl_arn
}

module "ecs" {
  source                 = "./modules/ecs"
  project_name           = var.project_name
  environment            = var.environment
  aws_region             = var.aws_region
  private_subnet_ids     = module.vpc.private_subnet_ids
  security_group_id      = module.security.ecs_security_group_id
  target_group_arn       = module.alb.target_group_arn
  ecs_execution_role_arn = module.security.ecs_execution_role_arn
  ecs_task_role_arn      = module.security.ecs_task_role_arn
  container_image        = var.container_image
  app_port               = var.app_port
  app_count              = var.app_count
}
