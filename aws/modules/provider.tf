# ###############################################################################
# Terraform Backend and Required Providers
# ###############################################################################

terraform {
  required_version = "~> 1.16"
  backend "s3" {
    bucket       = "msg-preds-dev-directive-tf-state"
    key          = "tf-infra/terraform.tfstate"
    region       = "us-east-2"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.64"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.3"
    }
  }
}

# ###############################################################################
# AWS provider
# ###############################################################################

provider "aws" {
  region = var.region
}

# ###############################################################################
# Helm provider connected to EKS (Elastic Kubernetes Service)
# ###############################################################################

provider "helm" {
  kubernetes = {
    host                   = module.compute.cluster_endpoint
    cluster_ca_certificate = base64decode(module.compute.cluster_ca_cert)

    exec = {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks", "get-token",
        "--cluster-name", module.compute.cluster_name,
        "--region", var.region
      ]
    }
  }
}
