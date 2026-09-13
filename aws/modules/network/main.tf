# ###############################################################################
# VPC (Virtual Private Cloud), subnets, routing and NAT (Network Address Translation) gateway
# ###############################################################################

module "vpc" {
  source               = "terraform-aws-modules/vpc/aws"
  version              = "~> 6.7"
  name                 = "${var.app_name}-vpc-${var.env}"
  cidr                 = var.vpc_cidr
  azs                  = var.vpc_azs
  private_subnets      = var.vpc_private_subnets
  public_subnets       = var.vpc_public_subnets
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  # -----------------------------------------------------------------------------
  # AWS Load Balancer Controller subnet discovery
  # -----------------------------------------------------------------------------
  public_subnet_tags  = { "kubernetes.io/role/elb" = "1" }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = "1" }

  tags = {
    Name                                               = "${var.app_name}-vpc-${var.env}"
    Terraform                                          = "true"
    Environment                                        = var.env
    "kubernetes.io/cluster/${var.app_name}-${var.env}" = "shared"
  }
}
