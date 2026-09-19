# ###############################################################################
# OUTPUTS
# ###############################################################################

output "cluster_name" {
  value       = module.eks.cluster_name
  description = "EKS cluster name"
}

output "cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "EKS cluster endpoint"
}

output "oidc_provider_arn" {
  value       = module.eks.oidc_provider_arn
  description = "EKS OIDC provider ARN"
}

output "cluster_ca_cert" {
  value       = module.eks.cluster_certificate_authority_data
  description = "EKS cluster CA certificate"
}
