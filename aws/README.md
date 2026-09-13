# AWS EKS deployment runbook

This runbook deploys the `msg-preds` learning application to Amazon EKS and removes
it afterward. Run every command from the repository root in Git Bash. Terraform's
supported root is `aws/modules`; `aws/main.tf` only guards against using the wrong
directory. The S3 backend already exists, so do not run `aws/backend-setup`.

Docker Desktop may stay closed while Terraform creates AWS infrastructure. Start it
only when building the `app` and `worker` images.

## Git Bash scripts

The commands below are collected into scripts in `aws/scripts`. Run them from the
repository root in this order:

```bash
# Fresh infrastructure deployment (already completed for the current cluster)
bash aws/scripts/01-infrastructure.sh

# Next step for the current cluster; Docker Desktop must be running
bash aws/scripts/02-build-and-push.sh

# Deploy PostgreSQL, Kafka, worker, API and ingress
bash aws/scripts/03-deploy-app.sh

# Wait for the ALB and run the end-to-end test
bash aws/scripts/04-test.sh

# Optional status report
bash aws/scripts/05-status.sh

# Remove the application and all Terraform-managed AWS resources
bash aws/scripts/06-destroy.sh
```

The image script writes the ECR URLs and generated image tag to the ignored
`aws/.deploy.env` file. It contains no database password. The deployment script
prompts for PostgreSQL credentials without displaying the password.

## 1. Configure the terminal

```bash
export AWS_PROFILE="AwsDev"
export AWS_REGION="us-east-2"
export TF_VAR_aws_profile="$AWS_PROFILE"
export TF_VAR_region="$AWS_REGION"

ADMIN_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '\r\n')"
export TF_VAR_admin_cidrs="[\"${ADMIN_IP}/32\"]"
export TF_VAR_admin_iam_users='["AwsDev"]'

terraform version
aws sts get-caller-identity
```

Terraform must be 1.16.x. Confirm that the AWS account is the intended account.

## 2. Initialize and inspect state

```bash
terraform -chdir=aws/modules init -reconfigure
terraform -chdir=aws/modules validate
terraform -chdir=aws/modules state list
```

For a fresh deployment, `state list` should be empty. Do not apply if it unexpectedly
lists older resources.

## 3. Create the network and bootstrap EKS

The one-time targeted applies create the complete network first and then the cluster
before Terraform configures Helm. Inspect each plan before applying it.

```bash
terraform -chdir=aws/modules plan -target=module.network -out=network.tfplan
terraform -chdir=aws/modules apply network.tfplan

terraform -chdir=aws/modules plan -target=module.compute -out=cluster.tfplan
terraform -chdir=aws/modules apply cluster.tfplan

CLUSTER_NAME="$(terraform -chdir=aws/modules output -raw cluster_name)"
aws eks update-kubeconfig \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --profile "$AWS_PROFILE" \
  --alias msg-preds-eks
kubectl --context msg-preds-eks get nodes
```

## 4. Complete the AWS infrastructure

This creates IAM integrations, the EBS CSI add-on, ECR repositories, and the AWS
Load Balancer Controller.

```bash
terraform -chdir=aws/modules plan -out=eks.tfplan
terraform -chdir=aws/modules apply eks.tfplan

kubectl --context msg-preds-eks -n kube-system rollout status \
  deployment/alb-controller-aws-load-balancer-controller --timeout=5m
kubectl --context msg-preds-eks -n kube-system rollout status \
  deployment/ebs-csi-controller --timeout=5m
kubectl --context msg-preds-eks apply -f aws/k8s/storage-class.yaml
kubectl --context msg-preds-eks create namespace msg-preds \
  --dry-run=client -o yaml | kubectl --context msg-preds-eks apply -f -
```

## 5. Build and push images

Start Docker Desktop in Linux-container mode.

```bash
APP_REPO="$(terraform -chdir=aws/modules output -json image_repositories | python -c 'import json,sys; print(json.load(sys.stdin)["app"])')"
WORKER_REPO="$(terraform -chdir=aws/modules output -json image_repositories | python -c 'import json,sys; print(json.load(sys.stdin)["worker"])')"
REGISTRY="${APP_REPO%%/*}"
IMAGE_TAG="$(date -u +%Y%m%d%H%M%S)"

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$REGISTRY"
docker build --platform linux/amd64 -t "${APP_REPO}:${IMAGE_TAG}" ./app
docker build --platform linux/amd64 -t "${WORKER_REPO}:${IMAGE_TAG}" ./worker
docker push "${APP_REPO}:${IMAGE_TAG}"
docker push "${WORKER_REPO}:${IMAGE_TAG}"
```

Keep this terminal open so the repository and tag variables remain available.

## 6. Deploy `msg-preds`

```bash
read -rp "PostgreSQL username: " PG_USER
read -rsp "PostgreSQL password: " PG_PASSWORD
echo
kubectl --context msg-preds-eks -n msg-preds create secret generic pguser \
  --from-literal=POSTGRES_USER="$PG_USER" --dry-run=client -o yaml | \
  kubectl --context msg-preds-eks apply -f -
kubectl --context msg-preds-eks -n msg-preds create secret generic pgpassword \
  --from-literal=POSTGRES_PASSWORD="$PG_PASSWORD" --dry-run=client -o yaml | \
  kubectl --context msg-preds-eks apply -f -
unset PG_PASSWORD

helm upgrade --install db ./charts/db --kube-context msg-preds-eks \
  -n msg-preds -f charts/db/values-eks.yaml --wait --timeout 10m
helm upgrade --install kafka ./charts/kafka --kube-context msg-preds-eks \
  -n msg-preds --wait --timeout 10m
kubectl --context msg-preds-eks -n msg-preds exec deployment/kafka -- \
  kafka-topics --bootstrap-server kafka:9092 --list

helm upgrade --install worker ./charts/worker --kube-context msg-preds-eks \
  -n msg-preds --set-string "image.repository=$WORKER_REPO" \
  --set-string "image.tag=$IMAGE_TAG" --wait --timeout 10m
kubectl --context msg-preds-eks -n msg-preds exec deployment/kafka -- \
  kafka-consumer-groups --bootstrap-server kafka:9092 \
  --describe --group MlEngineersGroup --state

helm upgrade --install app ./charts/app --kube-context msg-preds-eks \
  -n msg-preds --set-string "image.repository=$APP_REPO" \
  --set-string "image.tag=$IMAGE_TAG" --wait --timeout 10m
helm upgrade --install ingress ./charts/ingress --kube-context msg-preds-eks \
  -n msg-preds -f charts/ingress/values-eks.yaml --wait --timeout 10m
kubectl --context msg-preds-eks -n msg-preds get pods,svc,ingress,pvc
```

Repeat either Kafka inspection command if the broker or consumer is still starting.

## 7. Test the complete application

```bash
kubectl --context msg-preds-eks -n msg-preds get ingress ingress -w
# Press Ctrl+C after ADDRESS appears.
ALB_HOST="$(kubectl --context msg-preds-eks -n msg-preds get ingress ingress \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"
test -n "$ALB_HOST" || { echo "ALB is not ready"; exit 1; }
BASE_URL="http://$ALB_HOST"
powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File "$(cygpath -w "$PWD/aws/test-eks.ps1")" -BaseUrl "$BASE_URL"
```

Successful output begins with `PASS: Swagger, API, PostgreSQL, Kafka and worker`.

Useful diagnostics:

```bash
kubectl --context msg-preds-eks -n msg-preds get events --sort-by=.lastTimestamp
kubectl --context msg-preds-eks -n msg-preds logs deployment/app --tail=100
kubectl --context msg-preds-eks -n msg-preds logs deployment/worker --tail=100
kubectl --context msg-preds-eks -n kube-system logs \
  deployment/alb-controller-aws-load-balancer-controller --tail=100
kubectl --context msg-preds-eks -n msg-preds describe pvc db-data
```

## 8. Destroy everything created for the application

Delete Kubernetes ingress before Terraform removes the controller. This lets its
finalizer remove the ALB. Record the EBS volume so its deletion can be verified.

```bash
PV_NAME="$(kubectl --context msg-preds-eks -n msg-preds get pvc db-data \
  -o jsonpath='{.spec.volumeName}' 2>/dev/null || true)"
DB_VOLUME_ID=""
if [ -n "$PV_NAME" ]; then
  DB_VOLUME_ID="$(kubectl --context msg-preds-eks get pv "$PV_NAME" \
    -o jsonpath='{.spec.csi.volumeHandle}' 2>/dev/null || true)"
fi

helm uninstall ingress --kube-context msg-preds-eks -n msg-preds || true
kubectl --context msg-preds-eks -n msg-preds wait \
  --for=delete ingress/ingress --timeout=10m || true
helm uninstall app worker kafka db --kube-context msg-preds-eks -n msg-preds || true
kubectl --context msg-preds-eks delete namespace msg-preds --wait=true || true
kubectl --context msg-preds-eks delete storageclass gp3 --ignore-not-found

terraform -chdir=aws/modules plan -destroy -out=destroy.tfplan
terraform -chdir=aws/modules apply destroy.tfplan

if [ -n "$DB_VOLUME_ID" ]; then
  aws ec2 describe-volumes --volume-ids "$DB_VOLUME_ID" \
    --region "$AWS_REGION" --profile "$AWS_PROFILE" >/dev/null 2>&1 && \
    echo "WARNING: EBS volume $DB_VOLUME_ID still exists; inspect and delete it." || \
    echo "Database EBS volume was deleted."
fi
```

The ECR repositories and their images are deleted by Terraform. Verify in AWS that
the EKS cluster, EC2 workers, NAT gateway, ALB, and database EBS volume are gone.
The older S3 state bucket and DynamoDB table are not part of this application destroy.
Delete that backend separately only after confirming no Terraform project uses it.
