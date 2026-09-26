# Reusable AWS lab lifecycle

This guide describes the intended GitHub Actions lifecycle for starting and stopping
the `msg-preds` AWS learning environment. The goal is to make the lab easy to use
again after a long break without leaving chargeable application infrastructure
running between study sessions.

The repository provides manual lifecycle scripts as well as protected GitHub
Actions workflows. Complete the one-time bootstrap and GitHub configuration below
before using the workflow buttons. The tested local fallback remains in
[`README.md`](README.md).

## Lifecycle at a glance

The design separates a small, persistent bootstrap layer from the disposable lab.

```text
Persistent bootstrap
  Terraform state bucket + GitHub OIDC provider + deployment role
                              |
                              v
Start AWS Lab
  Terraform apply -> ECR build/push -> Argo CD sync -> smoke test
                              |
                              v
Destroy AWS Lab
  Remove ingress/apps -> Terraform destroy -> cleanup verification
```

The bootstrap layer is deliberately not part of the normal destroy operation. IAM
and the GitHub OIDC provider have no hourly charge, and the nearly empty state bucket
should have only a very small storage cost. Keeping these resources makes a later
restart possible without recreating CI authentication or losing Terraform state.

## Security controls

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
      "repo:OsherKoren/play_with_fastapi:environment:aws-lab",
    "token.actions.githubusercontent.com:ref": "refs/heads/main"
  }
}
```

A fork receives a different OIDC subject and therefore cannot assume this role.
Pull-request workflows must never apply Terraform or receive the AWS deployment
role. Do not use `pull_request_target` to check out and execute contributor code.

## One-time bootstrap

The `aws/bootstrap` Terraform root owns:

- The narrowly trusted GitHub deployment role and policy.
- Read access to AWS's public EKS optimized-AMI parameters and the two private
  application parameter paths.
- An optional AWS Budget and billing notification.

The GitHub OIDC provider is account-wide. By default, the bootstrap reuses an
existing provider instead of taking ownership of one that another project may
need. In a brand-new account with no GitHub provider, create it during the first
plan with `-var='create_github_oidc_provider=true'`; Terraform will then own it.

The existing state bucket is intentionally managed separately by
`aws/backend-setup`, because Terraform cannot create the bucket in which it is
already storing its own state. The bootstrap root uses a separate state key in that
same persistent bucket.

Bootstrap is an administrator operation performed once from a local terminal. From
the repository root in Git Bash:

```bash
export AWS_PROFILE="AwsDev"
export AWS_REGION="us-east-2"

aws sts get-caller-identity
terraform -chdir=aws/bootstrap init -reconfigure
terraform -chdir=aws/bootstrap plan -out=bootstrap.tfplan
terraform -chdir=aws/bootstrap apply bootstrap.tfplan
terraform -chdir=aws/bootstrap output -raw github_actions_role_arn
```

To create email budget notifications, add a real address when creating the saved
plan by using a local variable file or
`-var='budget_email=you@example.com'`, then apply that saved plan normally. Never
commit a personal address in this public repository.

Check whether the AWS account already contains the GitHub OIDC provider:

```bash
aws iam list-open-id-connect-providers
```

When it exists, use the default bootstrap plan, which reads but does not own it.
When it does not exist, add `-var='create_github_oidc_provider=true'` to the saved
plan command. Continue using the same value for future bootstrap plans so the
state and configuration remain consistent.

## One-time GitHub configuration

In the original GitHub repository—not a fork—open **Settings → Environments** and
create an environment named `aws-lab`.

Configure it as follows:

1. Allow deployments only from the `main` branch.
2. Add yourself as a required reviewer if that control is available for the
   repository's GitHub plan.
3. Add environment variable `AWS_ROLE_ARN` with the bootstrap output.
4. Add environment variable `AWS_REGION` with value `us-east-2`.
5. Add environment secret `ADMINISTRATOR_CIDR` with your current public IPv4
   address followed by `/32`, for example `203.0.113.10/32`. This grants your
   computer access to the EKS API without exposing the address as a workflow
   input. If your ISP changes your public address, update this secret before the
   next start or destroy run. You can obtain the current value with
   `curl -fsS https://checkip.amazonaws.com` and append `/32`.
6. In AWS Systems Manager Parameter Store in `us-east-2`, create
   `/msg-preds/aws-lab/postgres/user` as a Standard `String` and
   `/msg-preds/aws-lab/postgres/password` as a Standard `SecureString`. The
   workflow reads them after assuming the deployment role; do not duplicate
   their values in GitHub secrets.

Protect the `main` branch and require the `CI` and `Terraform check` status checks.
Do not permit outside collaborators to merge without review.

Before creating infrastructure, run **Actions → Check AWS Authentication → Run
workflow** from `main`. It verifies OIDC role assumption and access to the two SSM
parameters without creating EKS, networking, or other application resources.

## Start AWS Lab

Confirm that the `ADMINISTRATOR_CIDR` environment secret still matches your
current public IPv4 address, then open **Actions → Start AWS Lab → Run workflow**.
The workflow automatically combines that private CIDR with the temporary GitHub
runner CIDR. The former enables local `kubectl` access after the workflow finishes;
the latter lets the workflow configure the cluster. The workflow:

1. Wait for approval on the protected `aws-lab` environment.
2. Exchange its GitHub OIDC token for temporary AWS credentials.
3. Validate Terraform and create a saved infrastructure plan.
4. Apply the network and EKS bootstrap stages required by the provider dependency.
5. Apply the complete Terraform configuration, including Argo CD.
6. Build the `app` and `worker` images for Linux AMD64.
7. Tag each image with a hash of its production build inputs and push it only when
   that immutable tag is missing from ECR.
8. Update the EKS kubeconfig and bootstrap the Argo CD Applications.
9. Wait for Argo CD health and the ALB, then run the end-to-end smoke test.
10. Write the application URL and deployed image tag to the workflow summary.

## Container build cache

The path-aware production build jobs and AWS deployment use Docker Buildx with
GitHub Actions cache storage. The application uses cache scope `ecr-app`, and the
worker uses `ecr-worker`. Repeated commits on the same branch can reuse dependency
and filesystem layers. Builds on `main` also warm the cache used by **Start AWS
Lab**. Infrastructure-only changes skip application CI jobs.

The optional Docker Hub workflow has separate `docker-hub-app` and
`docker-hub-worker` scopes so publishing public images cannot replace the AWS build
cache. A cache miss is safe: Docker simply performs a complete build and stores new
layers for later runs.

## Destroy AWS Lab

If your public IP changed during the study session, update the
`ADMINISTRATOR_CIDR` environment secret first. Then open **Actions → Destroy AWS
Lab → Run workflow**, type `DESTROY`, and approve the protected environment. The
workflow:

1. Require the operator to type `DESTROY` and approve the `aws-lab` environment.
2. Capture the persistent-volume and EBS-volume identifiers for verification.
3. Delete the Argo CD Applications and let their finalizers remove ingress first.
4. Wait for the application, worker, Kafka, database, and load balancer to disappear.
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

If GitHub Actions is unavailable, run the numbered scripts in the manual runbook.
They follow the same create, deploy, test, and destroy sequence.

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
