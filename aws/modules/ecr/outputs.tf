# ###############################################################################
# Outputs
# ###############################################################################

output "image_repositories" {
  description = "ECR repository URLs keyed by application component"
  value       = { for name, repository in aws_ecr_repository.application : name => repository.repository_url }
}
