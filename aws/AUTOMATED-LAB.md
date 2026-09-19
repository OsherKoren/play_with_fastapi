# Reusable AWS lab lifecycle

This guide describes the intended GitHub Actions lifecycle for starting and stopping
the `msg-preds` AWS learning environment. The goal is to make the lab easy to use
again after a long break without leaving chargeable application infrastructure
running between study sessions.

> [!IMPORTANT]
> The automated `aws-start.yml` and `aws-destroy.yml` workflows described here are
> not implemented yet. Until they are added, use the tested manual procedure in
> [`README.md`](README.md). Do not assume that a GitHub Actions button currently
> deploys or removes the AWS environment.

## Lifecycle at a glance

The design separates a small, persistent bootstrap layer from the disposable lab.

```text
Persistent bootstrap
  Terraform state bucket + GitHub OIDC provider + deployment role
                              |
                              v
Start AWS Lab
  Terraform apply -> ECR build/push -> Helm deploy -> smoke test
                              |
                              v
Destroy AWS Lab
  Remove ingress/apps -> Terraform destroy -> cleanup verification
```

The bootstrap layer is deliberately not part of the normal destroy operation. IAM
and the GitHub OIDC provider have no hourly charge, and the nearly empty state bucket
should have only a very small storage cost. Keeping these resources makes a later
restart possible without recreating CI authentication or losing Terraform state.

## Planned controls

The deployment workflows should use all of the following controls:

- Manual `workflow_dispatch` triggers only for apply and destroy.
- A protected GitHub environment named `aws-lab`.
- A required reviewer and a deployment-branch rule restricted to `main`.
- Short-lived AWS credentials obtained through GitHub OIDC; no AWS access keys in
  GitHub secrets.
- An AWS role trust policy restricted to the exact repository and `aws-lab`
  environment.
- A concurrency group so only one lab-changing workflow can run at a time.
- A literal `DESTROY` confirmation input on the destroy workflow.
- Saved Terraform plans, with the reviewed plan supplied to `terraform apply`.
- Commit-SHA image tags rather than `latest` for immutable ECR repositories.

The important OIDC trust condition is expected to have this shape:

```json
{
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub":
      "repo:OsherKoren/play_with_fastapi:environment:aws-lab"
  }
}
```

A fork receives a different OIDC subject and therefore cannot assume this role.
Pull-request workflows must never apply Terraform or receive the AWS deployment
role. Do not use `pull_request_target` to check out and execute contributor code.

## One-time bootstrap

The planned `aws/bootstrap` Terraform root will own:

- The versioned and encrypted S3 Terraform state bucket.
- The GitHub Actions OIDC provider.
- The narrowly trusted GitHub deployment role and policies.
- An optional AWS Budget and billing notification.

Bootstrap is an administrator operation performed locally with an authenticated AWS
profile. It should be applied once and retained between lab sessions. Its outputs
will include the role ARN to configure as a GitHub environment variable.

Until that root is implemented, the existing backend remains managed through
`aws/backend-setup`, and the deployment itself must follow the manual AWS runbook.

## Planned Start AWS Lab workflow

The future `.github/workflows/aws-start.yml` workflow will:

1. Wait for approval on the protected `aws-lab` environment.
2. Exchange its GitHub OIDC token for temporary AWS credentials.
3. Validate Terraform and create a saved infrastructure plan.
4. Apply the network and EKS bootstrap stages required by the provider dependency.
5. Apply the complete Terraform configuration.
6. Build the `app` and `worker` images for Linux AMD64.
7. Tag and push both images to ECR using the Git commit SHA.
8. Update the EKS kubeconfig and deploy the Helm releases.
9. Wait for the ALB and run the end-to-end smoke test.
10. Write the application URL and deployed image tag to the workflow summary.

## Planned Destroy AWS Lab workflow

The future `.github/workflows/aws-destroy.yml` workflow will:

1. Require the operator to type `DESTROY` and approve the `aws-lab` environment.
2. Capture the persistent-volume and EBS-volume identifiers for verification.
3. Uninstall ingress first and wait for the AWS load balancer to disappear.
4. Uninstall the application, worker, Kafka, and database releases.
5. Delete the namespace, claims, and storage class.
6. Create and apply a saved Terraform destroy plan.
7. Check for leftover EKS clusters, load balancers, NAT gateways, EBS volumes, and
   ECR repositories associated with the lab.
8. Preserve the bootstrap role, OIDC provider, state bucket, and state history.

Always run destroy after a study session. Closing the browser or stopping a workflow
does not stop AWS charges.

## Returning after a long break

Use this checklist when reopening the project months or years later:

1. Read this guide and the current [`README.md`](README.md).
2. Check the AWS Budgets dashboard before creating resources.
3. Confirm that the `aws-lab` GitHub environment still exists and allows only
   `main`.
4. Confirm that the OIDC role still trusts only this repository and environment.
5. Review dependency update notes for Terraform, AWS, EKS, Helm, and GitHub Actions.
6. Run CI and Terraform validation before applying anything.
7. Review the infrastructure plan, then run **Start AWS Lab**.
8. Complete the exercises and smoke test.
9. Run **Destroy AWS Lab** and wait for its cleanup verification to pass.
10. Review AWS billing and Resource Explorer for unexpected remaining resources.

If the automated workflows have not yet been implemented, run the numbered scripts
in the manual runbook instead. They follow the same create, deploy, test, and destroy
sequence.

## Emergency lockout

If deployment access may have been exposed, or the repository is no longer being
used, disable or delete the GitHub deployment IAM role in AWS. That immediately
prevents the public workflow definition from creating resources in this account.
The role can later be recreated from the bootstrap configuration using an
administrator's local AWS credentials.

## Cost-safety checklist

After every destroy, verify that the lab no longer has:

- An EKS cluster or managed node group.
- EC2 instances created for EKS.
- NAT gateways or application load balancers.
- Unattached EBS volumes or snapshots that are not intentionally retained.
- ECR images or repositories from the disposable stack.
- Public IPv4 addresses allocated to lab resources.

Keep the AWS Budget active even while the lab is destroyed. A budget is a warning
mechanism, not a spending limit, so cleanup verification is still required.
