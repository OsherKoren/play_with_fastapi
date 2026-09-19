variable "region" {
  description = "AWS region used by the lab"
  type        = string
  default     = "us-east-2"
}

variable "github_repository" {
  description = "GitHub owner and repository allowed to assume the deployment role"
  type        = string
  default     = "OsherKoren/play_with_fastapi"
}

variable "github_environment" {
  description = "Protected GitHub environment used by AWS lifecycle workflows"
  type        = string
  default     = "aws-lab"
}

variable "github_branch" {
  description = "Only this branch may obtain AWS deployment credentials"
  type        = string
  default     = "main"
}

variable "create_github_oidc_provider" {
  description = "Create the account-level GitHub OIDC provider; leave false when the account already has one"
  type        = bool
  default     = false
}

variable "state_bucket" {
  description = "Existing S3 bucket containing the disposable stack state"
  type        = string
  default     = "msg-preds-dev-directive-tf-state"
}

variable "postgres_user_parameter" {
  description = "SSM Parameter Store path containing the AWS lab PostgreSQL username"
  type        = string
  default     = "/msg-preds/aws-lab/postgres/user"
}

variable "postgres_password_parameter" {
  description = "SSM Parameter Store path containing the AWS lab PostgreSQL password"
  type        = string
  default     = "/msg-preds/aws-lab/postgres/password"
}

variable "budget_email" {
  description = "Optional email address for a monthly AWS budget notification"
  type        = string
  default     = ""
}

variable "monthly_budget_usd" {
  description = "Monthly budget threshold in USD"
  type        = number
  default     = 25
}
