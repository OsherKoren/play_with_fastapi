output "cluster_name" {
  value = module.compute.cluster_name
}
output "region" {
  value = var.region
}
output "vpc_id" {
  value = module.network.vpc_id
}

output "image_repositories" {
  description = "ECR repository URLs used to push the application images"
  value       = module.ecr.image_repositories
}
