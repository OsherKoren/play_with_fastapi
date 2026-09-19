# ###############################################################################
# VARIABLES
# ###############################################################################

variable "alb_iam_role_arn" {
  type        = string
  description = "IAM role ARN for ALB controller"
}

variable "cluster_name" {
  type        = string
  description = "EKS Cluster name"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where EKS cluster is deployed"
}
variable "region" {
  type = string
}
