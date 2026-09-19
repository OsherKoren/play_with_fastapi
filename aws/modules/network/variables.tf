# ###############################################################################
# VARIABLES
# ###############################################################################


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

variable "vpc_cidr" {
  description = "Default CIDR range of the VPC"
  type        = string
  default     = "10.0.0.0/16"
  #   default = "192.168.0.0/16"
}

variable "vpc_azs" {
  description = "Availability zones for VPC"
  type        = list(string)
  default     = ["us-east-2a", "us-east-2b"]
}

variable "vpc_public_subnets" {
  description = "Public subnets for VPC"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
  #   default     = ["192.168.0.0/18", "192.168.64.0/18"]
}

variable "vpc_private_subnets" {
  description = "Private subnets for VPC"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
  #   default     = ["192.168.128.0/18", "192.168.192.0/18"]
}
