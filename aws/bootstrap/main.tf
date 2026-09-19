resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = []

  tags = {
    Project   = "msg-preds"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role" "github_actions" {
  name        = "msg-preds-github-actions"
  description = "Starts and destroys the msg-preds learning lab from its protected GitHub environment"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:environment:${var.github_environment}"
          "token.actions.githubusercontent.com:ref" = "refs/heads/${var.github_branch}"
        }
      }
    }]
  })

  max_session_duration = 7200

  tags = {
    Project   = "msg-preds"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role_policy" "github_actions" {
  name = "msg-preds-lab-lifecycle"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "TerraformState"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [
          "arn:${data.aws_partition.current.partition}:s3:::${var.state_bucket}/tf-infra/*"
        ]
      },
      {
        Sid      = "TerraformStateBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetBucketVersioning"]
        Resource = "arn:${data.aws_partition.current.partition}:s3:::${var.state_bucket}"
      },
      {
        Sid    = "LabInfrastructure"
        Effect = "Allow"
        Action = [
          "autoscaling:*",
          "ec2:*",
          "ecr:*",
          "eks:*",
          "elasticloadbalancing:*",
          "logs:*",
          "sts:GetCallerIdentity",
          "tag:GetResources"
        ]
        Resource = "*"
      },
      {
        Sid    = "LabIamResources"
        Effect = "Allow"
        Action = [
          "iam:AddUserToGroup", "iam:AttachGroupPolicy", "iam:AttachRolePolicy",
          "iam:AddRoleToInstanceProfile", "iam:CreateGroup", "iam:CreateInstanceProfile",
          "iam:CreateOpenIDConnectProvider", "iam:CreatePolicy",
          "iam:CreatePolicyVersion", "iam:CreateRole", "iam:CreateServiceLinkedRole",
          "iam:DeleteGroup", "iam:DeleteInstanceProfile", "iam:DeleteOpenIDConnectProvider", "iam:DeletePolicy",
          "iam:DeletePolicyVersion", "iam:DeleteRole", "iam:DeleteRolePolicy",
          "iam:DetachGroupPolicy", "iam:DetachRolePolicy", "iam:GetGroup",
          "iam:GetInstanceProfile", "iam:GetOpenIDConnectProvider", "iam:GetPolicy", "iam:GetPolicyVersion",
          "iam:GetRole", "iam:GetRolePolicy", "iam:ListAttachedGroupPolicies",
          "iam:ListAttachedRolePolicies", "iam:ListGroupsForUser", "iam:ListInstanceProfilesForRole",
          "iam:ListPolicyVersions", "iam:ListRolePolicies", "iam:ListRoles",
          "iam:ListUsers", "iam:PassRole", "iam:PutRolePolicy", "iam:RemoveRoleFromInstanceProfile",
          "iam:RemoveUserFromGroup", "iam:SetDefaultPolicyVersion", "iam:TagInstanceProfile",
          "iam:TagOpenIDConnectProvider", "iam:TagPolicy", "iam:TagRole",
          "iam:UntagInstanceProfile",
          "iam:UntagOpenIDConnectProvider", "iam:UntagPolicy", "iam:UntagRole",
          "iam:UpdateAssumeRolePolicy", "iam:UpdateOpenIDConnectProviderThumbprint"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_budgets_budget" "lab" {
  count = var.budget_email == "" ? 0 : 1

  name         = "msg-preds-monthly-cost"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.budget_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_email]
  }
}
