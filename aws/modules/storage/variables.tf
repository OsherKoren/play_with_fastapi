# ###############################################################################
# Input variables
# ###############################################################################

variable "cluster_name" {
  description = "Name of the EKS cluster that receives the EBS CSI add-on"
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider used by the CSI service account"
  type        = string
}
