# ###############################################################################
# EKS (Elastic Kubernetes Service) cluster and managed worker nodes
# ###############################################################################

module "eks" {
  source                                   = "terraform-aws-modules/eks/aws"
  version                                  = "~> 21.25"
  name                                     = local.cluster_name
  vpc_id                                   = var.vpc_id
  subnet_ids                               = var.private_subnets
  kubernetes_version                       = var.kubernetes_version
  endpoint_private_access                  = true
  endpoint_public_access                   = true
  endpoint_public_access_cidrs             = var.admin_cidrs
  enable_cluster_creator_admin_permissions = true
  enable_irsa                              = true

  # -----------------------------------------------------------------------------
  # EKS (Elastic Kubernetes Service) managed add-ons
  # -----------------------------------------------------------------------------
  addons = {
    vpc-cni    = { before_compute = true }
    kube-proxy = {}
    coredns    = {}
  }

  # -----------------------------------------------------------------------------
  # EKS (Elastic Kubernetes Service) managed node groups
  # -----------------------------------------------------------------------------
  eks_managed_node_groups = {
    msg-preds = {
      instance_types = ["t3.medium"]
      ami_type       = "AL2023_x86_64_STANDARD"
      capacity_type  = "ON_DEMAND"
      min_size       = 2
      max_size       = 3
      desired_size   = 2
      subnet_ids     = var.private_subnets
    }
  }

  tags = {
    Environment = var.env
    Project     = var.app_name
    Terraform   = "true"
  }
}
