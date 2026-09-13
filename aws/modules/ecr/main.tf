# ###############################################################################
# ECR (Elastic Container Registry) private container image repositories
# ###############################################################################

resource "aws_ecr_repository" "application" {
  for_each             = toset(["app", "worker"])
  name                 = "${var.cluster_name}/${each.key}"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}
