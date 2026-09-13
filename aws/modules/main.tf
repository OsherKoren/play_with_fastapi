# ###############################################################################
# MAIN
# ###############################################################################

# ###############################################################################
# NETWORK MODULE
# ###############################################################################
module "network" {
  source  = "./network"
  vpc_azs = ["${var.region}a", "${var.region}b"]
}

# ###############################################################################
# COMPUTE / EKS (ELASTIC KUBERNETES SERVICE) MODULE
# ###############################################################################
module "compute" {
  source             = "./compute"
  kubernetes_version = var.kubernetes_version
  admin_cidrs        = var.admin_cidrs
  vpc_id             = module.network.vpc_id
  private_subnets    = module.network.private_subnets
}

# ###############################################################################
# IAM MODULE
# ###############################################################################
module "iam" {
  source          = "./iam"
  admin_iam_users = var.admin_iam_users

  cluster_name      = module.compute.cluster_name
  oidc_provider_arn = module.compute.oidc_provider_arn
}

# ###############################################################################
# ALB (APPLICATION LOAD BALANCER) MODULE
# ###############################################################################
module "alb" {
  source = "./alb"

  providers = {
    helm = helm
  }

  region           = var.region
  cluster_name     = module.compute.cluster_name
  alb_iam_role_arn = module.iam.alb_iam_role_arn
  vpc_id           = module.network.vpc_id
}

# ###############################################################################
# STORAGE MODULE
# ###############################################################################
module "storage" {
  source = "./storage"

  cluster_name      = module.compute.cluster_name
  oidc_provider_arn = module.compute.oidc_provider_arn
}

# ###############################################################################
# ECR (ELASTIC CONTAINER REGISTRY) MODULE
# ###############################################################################
module "ecr" {
  source = "./ecr"

  cluster_name = module.compute.cluster_name
}
