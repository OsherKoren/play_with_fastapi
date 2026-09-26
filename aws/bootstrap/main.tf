resource "aws_iam_openid_connect_provider" "github" {
  count = var.create_github_oidc_provider ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = []

  tags = {
    Project   = "msg-preds"
    ManagedBy = "Terraform"
  }
}

data "aws_iam_openid_connect_provider" "github" {
  count = var.create_github_oidc_provider ? 0 : 1
  url   = "https://token.actions.githubusercontent.com"
}

locals {
  github_oidc_provider_arn = var.create_github_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : data.aws_iam_openid_connect_provider.github[0].arn
}

resource "aws_iam_role" "github_actions" {
  name        = "msg-preds-github-actions"
  description = "Starts and destroys the msg-preds learning lab from its protected GitHub environment"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = local.github_oidc_provider_arn
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
        Sid    = "PostgresParameters"
        Effect = "Allow"
        Action = ["ssm:GetParameter", "ssm:GetParameters"]
        Resource = [
          "arn:${data.aws_partition.current.partition}:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${var.postgres_user_parameter}",
          "arn:${data.aws_partition.current.partition}:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${var.postgres_password_parameter}"
        ]
      },
      {
        Sid      = "EksOptimizedAmiParameters"
        Effect   = "Allow"
        Action   = "ssm:GetParameter"
        Resource = "arn:${data.aws_partition.current.partition}:ssm:${var.region}::parameter/aws/service/eks/optimized-ami/*"
      },
      {
        Sid      = "CreateTaggedLabKmsKey"
        Effect   = "Allow"
        Action   = ["kms:CreateKey", "kms:TagResource"]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestTag/Environment" = "dev"
            "aws:RequestTag/Project"     = "msg-preds"
            "aws:RequestTag/Terraform"   = "true"
            "kms:KeySpec"                = "SYMMETRIC_DEFAULT"
            "kms:KeyUsage"               = "ENCRYPT_DECRYPT"
          }
          Bool = {
            "kms:MultiRegion" = "false"
          }
        }
      },
      {
        Sid    = "ManageTaggedLabKmsKey"
        Effect = "Allow"
        Action = [
          "kms:CancelKeyDeletion",
          "kms:CreateAlias",
          "kms:DeleteAlias",
          "kms:DescribeKey",
          "kms:DisableKey",
          "kms:DisableKeyRotation",
          "kms:EnableKey",
          "kms:EnableKeyRotation",
          "kms:GetKeyPolicy",
          "kms:GetKeyRotationStatus",
          "kms:ListResourceTags",
          "kms:PutKeyPolicy",
          "kms:ScheduleKeyDeletion",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:UpdateAlias",
          "kms:UpdateKeyDescription"
        ]
        Resource = "arn:${data.aws_partition.current.partition}:kms:${var.region}:${data.aws_caller_identity.current.account_id}:key/*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Environment" = "dev"
            "aws:ResourceTag/Project"     = "msg-preds"
            "aws:ResourceTag/Terraform"   = "true"
          }
        }
      },
      {
        Sid      = "ManageLabKmsAlias"
        Effect   = "Allow"
        Action   = ["kms:CreateAlias", "kms:DeleteAlias", "kms:UpdateAlias"]
        Resource = "arn:${data.aws_partition.current.partition}:kms:${var.region}:${data.aws_caller_identity.current.account_id}:alias/eks/msg-preds-dev"
      },
      {
        Sid      = "ListKmsAliases"
        Effect   = "Allow"
        Action   = "kms:ListAliases"
        Resource = "*"
      },
      {
        Sid      = "CreateEksOidcProvider"
        Effect   = "Allow"
        Action   = ["iam:CreateOpenIDConnectProvider", "iam:TagOpenIDConnectProvider"]
        Resource = "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/oidc.eks.${var.region}.amazonaws.com/id/*"
      },
      {
        Sid    = "ManageEksOidcProvider"
        Effect = "Allow"
        Action = [
          "iam:AddClientIDToOpenIDConnectProvider",
          "iam:DeleteOpenIDConnectProvider",
          "iam:GetOpenIDConnectProvider",
          "iam:ListOpenIDConnectProviderTags",
          "iam:RemoveClientIDFromOpenIDConnectProvider",
          "iam:TagOpenIDConnectProvider",
          "iam:UntagOpenIDConnectProvider",
          "iam:UpdateOpenIDConnectProviderThumbprint"
        ]
        Resource = "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/oidc.eks.${var.region}.amazonaws.com/id/*"
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
          "iam:CreatePolicy",
          "iam:CreatePolicyVersion", "iam:CreateRole", "iam:CreateServiceLinkedRole",
          "iam:DeleteGroup", "iam:DeleteInstanceProfile", "iam:DeletePolicy",
          "iam:DeletePolicyVersion", "iam:DeleteRole", "iam:DeleteRolePolicy",
          "iam:DetachGroupPolicy", "iam:DetachRolePolicy", "iam:GetGroup",
          "iam:GetInstanceProfile", "iam:GetPolicy", "iam:GetPolicyVersion",
          "iam:GetRole", "iam:GetRolePolicy", "iam:ListAttachedGroupPolicies",
          "iam:ListAttachedRolePolicies", "iam:ListGroupsForUser", "iam:ListInstanceProfilesForRole",
          "iam:ListPolicyVersions", "iam:ListRolePolicies", "iam:ListRoles",
          "iam:ListUsers", "iam:PassRole", "iam:PutRolePolicy", "iam:RemoveRoleFromInstanceProfile",
          "iam:RemoveUserFromGroup", "iam:SetDefaultPolicyVersion", "iam:TagInstanceProfile",
          "iam:TagPolicy", "iam:TagRole",
          "iam:UntagInstanceProfile",
          "iam:UntagPolicy", "iam:UntagRole", "iam:UpdateAssumeRolePolicy"
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
