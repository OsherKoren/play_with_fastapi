# AWS EKS and Argo CD runbook

This runbook creates the disposable `msg-preds-dev` EKS lab, builds immutable
application images in ECR, bootstraps Argo CD, tests the deployment, and removes the
chargeable resources afterward. Run local commands from the repository root in Git
Bash. The Terraform root is `aws/modules`.

For the one-time GitHub OIDC setup and protected workflow buttons, see
[`AUTOMATED-LAB.md`](AUTOMATED-LAB.md).

## Architecture and ownership

```text
Terraform
  VPC, EKS, ECR, IAM, AWS controllers, Argo CD

Argo CD (inside EKS, namespace argocd)
  db, Kafka, worker, API, ALB ingress

GitHub Actions or local scripts
  Terraform orchestration, image build/push, Argo bootstrap, smoke test
```

Argo CD is a `ClusterIP` service. It does not create a public administrative load
balancer. The application ingress still creates the public ALB.

## Prerequisites

- AWS CLI v2 with profile `AwsDev`
- Terraform 1.16.x
- Docker Desktop in Linux-container mode
- kubectl, Helm 3, Git Bash, curl, and Python
- The persistent S3 backend and GitHub OIDC bootstrap described in
  [`AUTOMATED-LAB.md`](AUTOMATED-LAB.md)

## Complete local lifecycle

```bash
export AWS_PROFILE="AwsDev"
export AWS_REGION="us-east-2"

bash aws/scripts/01-infrastructure.sh
bash aws/scripts/02-build-and-push.sh
bash aws/scripts/03-deploy-app.sh
bash aws/scripts/04-test.sh
bash aws/scripts/05-status.sh       # optional
bash aws/scripts/06-destroy.sh      # always run when finished
bash aws/scripts/07-verify-destroyed.sh
```

The infrastructure script admits the current public IP to the EKS API. The image
script calculates independent content hashes from each production Dockerfile,
dependency file, and `src` tree. If that immutable tag already exists in ECR, the
build and push are skipped.

The deployment script prompts for PostgreSQL credentials, creates Kubernetes
Secrets, and applies the Argo CD Applications from
`aws/argocd/applications.yaml.tpl`. Argo CD continuously reconciles the Helm charts
on `main`; later chart commits are applied without another `helm upgrade` command.

## Inspect Argo CD

Confirm the applications:

```bash
kubectl --context msg-preds-eks -n argocd get applications
```

Start a private local tunnel to the Argo CD UI:

```bash
kubectl --context msg-preds-eks -n argocd \
  port-forward service/argocd-server 8080:443
```

Open `https://localhost:8080`. A browser warning for the internal certificate is
expected. The username is `admin`. Read the initial password in another terminal:

```bash
kubectl --context msg-preds-eks -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d
```

## CI image strategy

Each service now has one multi-stage Dockerfile:

- `development` contains development/test behavior and is selected by
  `docker-compose-dev.yml`.
- `production` contains only runtime dependencies and is the default final stage.

CI runs pytest once in the development app container. It separately build-validates
only a changed service's `production` stage and does not start a duplicate
production Compose stack. Buildx stores reusable layers in the GitHub Actions cache.

AWS deployment uses content-based tags rather than the repository commit SHA. An
infrastructure-only commit therefore reuses existing images. After a full destroy,
ECR is empty and images must be rebuilt, but BuildKit caching can still accelerate
that operation.

## Safe destruction

The destroy script deletes the Argo CD Applications first. Their finalizers let
Argo CD remove Kubernetes resources and give the AWS Load Balancer Controller time
to delete the ALB. Terraform then destroys Argo CD, EKS, networking, ECR, and other
disposable resources.

The final verification checks Terraform state, EKS, EC2 nodes, NAT gateways, EBS
volumes, Kubernetes load balancers, and ECR repositories. The S3 state bucket,
GitHub OIDC provider, deployment role, and optional AWS Budget remain intentionally
so the lab can be recreated later.
