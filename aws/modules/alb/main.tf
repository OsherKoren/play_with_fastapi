# ###############################################################################
# AWS Load Balancer Controller
# ###############################################################################

resource "helm_release" "alb-controller" {
  name       = "alb-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  # helm_release requires the configured chart version to match the resolved version.
  version = "3.5.0"
  timeout = 600

  # -----------------------------------------------------------------------------
  # EKS cluster settings and IRSA (IAM Roles for Service Accounts)
  # -----------------------------------------------------------------------------
  values = [yamlencode({
    clusterName = var.cluster_name
    region      = var.region
    vpcId       = var.vpc_id
    serviceAccount = {
      create      = true
      name        = "aws-load-balancer-controller"
      annotations = { "eks.amazonaws.com/role-arn" = var.alb_iam_role_arn }
    }
  })]
}
