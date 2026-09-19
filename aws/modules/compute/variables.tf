# ###############################################################################
# VARIABLES
# ###############################################################################


variable "kubernetes_version" {
  description = "The version of Kubernetes for the EKS cluster"
  type        = string
  default     = "1.36"
}

variable "app_name" {
  description = "Name of the web application"
  type        = string
  default     = "msg-preds"
}

variable "env" {
  description = "Environment"
  type        = string
  default     = "dev"
}

variable "vpc_id" {
  description = "VPC ID where EKS will be deployed"
  type        = string
}

variable "private_subnets" {
  description = "Private subnets for EKS worker nodes"
  type        = list(string)
}

variable "admin_cidrs" {
  type = list(string)
}
