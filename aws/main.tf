# The deployable configuration is in aws/modules. This guard prevents Terraform
# from being run accidentally from the aws directory.
resource "terraform_data" "use_modules" {
  lifecycle {
    precondition {
      condition = path.module == "__never_deploy_this_directory__"
      error_message = "Run Terraform with -chdir=aws/modules. See the root README for deployment instructions."
    }
  }
}
