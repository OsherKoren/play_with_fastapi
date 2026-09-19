output "github_actions_role_arn" {
  description = "Set this value as the AWS_ROLE_ARN variable on the aws-lab GitHub environment"
  value       = aws_iam_role.github_actions.arn
}

output "github_oidc_provider_arn" {
  value = local.github_oidc_provider_arn
}
