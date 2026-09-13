# ###############################################################################
# BACKEND VARIABLES
# ###############################################################################


variable "region" {
  description = "Default region for provider"
  type        = string
  default     = "us-east-2"
}

variable "aws_profile" {
  default     = "eksAdmin"
  description = "AWS CLI profile to use for authentication"
}


variable "s3_bucket" {
  description = "Name of the terraform state bucket"
  type        = string
  default     = "msg-preds-dev-directive-tf-state"
}

variable "dynamodb_table" {
  description = "Name of the dynamodb table"
  type        = string
  default     = "msg-preds-dev-state-locking"
}
