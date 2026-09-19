# ###############################################################################
# IAM role for the AWS Load Balancer Controller
# with IRSA (IAM Roles for Service Accounts)
# ###############################################################################

# Creating IAM Role and attaching AWS-managed ALB policy (permissions) only the ALB Controller Pod.
module "alb_controller_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts"
  version = "~> 6.8"

  name = "${var.cluster_name}-ALBControllerRole"

  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = var.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}
