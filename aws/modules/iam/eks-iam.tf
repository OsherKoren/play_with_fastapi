# ###############################################################################
# IAM IDENTITIES AND POLICY FOR THE
# EKS (ELASTIC KUBERNETES SERVICE) CLUSTER
# ###############################################################################

# https://navyadevops.hashnode.dev/step-by-step-guide-creating-an-eks-cluster-with-alb-controller-using-terraform-modules
# Creates IAM Entities for allowing access to the EKS cluster
# Creates an IAM Role and Policy for accessing the EKS cluster
# This role is assumed by the root user of the AWS account that owns the VPC
# where the EKS cluster is deployed. This is required for the AWS Load Balancer
# Controller.


module "allow_eks_access_iam_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "~> 6.8"

  name   = "allow-eks-access"
  create = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters"
        ]
        Resource = "*"
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

module "eks_admin_iam_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.8"

  name            = "EKSAdminRole"
  use_name_prefix = false

  trust_policy_permissions = {
    accountRoot = {
      actions = ["sts:AssumeRole"]
      principals = [{
        type        = "AWS"
        identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      }]
    }
  }

  policies = {
    allow_eks_access = module.allow_eks_access_iam_policy.arn
  }
}

module "allow_assume_eks_admin_iam_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "~> 6.8"

  name   = "allow-assume-eks-admin"
  create = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sts:AssumeRole"
        ]
        Resource = module.eks_admin_iam_role.arn
      }
    ]
  })
}


module "eks_admins_iam_group" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-group"
  version = "~> 6.8"

  name                               = "EKSAdminsGroup"
  users                              = var.admin_iam_users
  enable_self_management_permissions = false
  enable_mfa_enforcement             = false

  policies = {
    allow_assume_eks_admin = module.allow_assume_eks_admin_iam_policy.arn
  }
}
resource "aws_eks_access_entry" "admin" {
  cluster_name  = var.cluster_name
  principal_arn = module.eks_admin_iam_role.arn
  type          = "STANDARD"
}
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = var.cluster_name
  principal_arn = aws_eks_access_entry.admin.principal_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  access_scope { type = "cluster" }
}
