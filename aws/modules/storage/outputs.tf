# ###############################################################################
# Outputs
# ###############################################################################

output "ebs_csi_role_arn" {
  description = "IAM role used by the EBS CSI controller"
  value       = aws_iam_role.ebs_csi.arn
}
