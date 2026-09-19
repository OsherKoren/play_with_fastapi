# ###############################################################################
# VARIABLES
# ###############################################################################

variable "region" {
  description = "Default region for provider"
  type        = string
  default     = "us-east-2"
}

variable "kubernetes_version" {
  type    = string
  default = "1.36"
}
variable "admin_cidrs" {
  description = "Public IPv4 CIDRs permitted to reach the Kubernetes API"
  type        = list(string)
  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for cidr in var.admin_cidrs : can(cidrnetmask(cidr)) && cidr != "0.0.0.0/0"])
    error_message = "Supply trusted IPv4 CIDRs, such as your public IP followed by /32."
  }
}

variable "admin_iam_users" {
  description = "Existing IAM users to add to EKSAdminsGroup; empty for SSO-only accounts"
  type        = list(string)
  default     = []
}
