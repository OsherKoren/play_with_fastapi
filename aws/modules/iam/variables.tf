###############################################################################
# VARIABLES
###############################################################################

variable "cluster_name" {
  type        = string
  description = "EKS cluster name"
}

variable "oidc_provider_arn" {
  type        = string
  description = "EKS OIDC provider ARN"
}
variable "admin_iam_users" {
  type    = list(string)
  default = ["AwsDev"]
}
