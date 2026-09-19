## This project is for experimenting with FastAPI, Docker, and Kubernetes for microservice applications

## How to run via docker-compose
### Pre-Requisites  🛠️
1. Install `docker`
2. Install `docker-compose`

### Setup  ⚙️
1. Create a `.env.dev` and `.env` files in the root directory with the contents presented in the `.env.dev.example` and `.env.example` files.

### Run all services 🚀
1. For testing dev app locally run in the terminal:
```shell
docker-compose -f docker-compose-dev.yml --env-file .env.dev up -d --build
```

### Check the result  🎯
1. Go to `http://127.0.0.1:8000/docs` to see the swagger docs
2. Go to `http://127.0.0.1:8000/redoc` to see the redoc docs
3. Go to `http://1270.0.0.1:8000/api/v1/messages` to send requests

![API Docs](https://github.com/OsherKoren/play_with_fastapi/blob/dev/images/openapi.png)

### Stop all services  ❌
```shell
docker compose -f docker-compose-dev.yml --env-file ./.env.dev down
```

## How to deploy on kubernetes cluster - Using docker-desktop kubernetes engine
### Pre-Requisites  🛠️
1. Install `kubctl`
2. Install ingress-nginx:
```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```
3. Verify the installation
```shell
kubectl get all -n ingress-nginx
```

### Setup  ⚙️
1. Create kubectl postgres user and secret on `default` namespace
```shell
kubectl create secret generic pguser --from-literal=POSTGRES_USER=<your_postgres_user>
```
```shell
kubectl create secret generic pgpassword --from-literal=POSTGRES_PASSWORD=<your_postgres_password>
```

### Apply services  🚀
1. Apply kubernetes files using `default` namespace
```shell
kubectl apply -f k8s
```

### Check the result  🎯
1. Go to `msg-preds.com/docs` and try some get & post requests.

### Delete all resources under `default` namespace  ❌
```shell
kubectl delete all --all
```


## How to deploy on kubernetes cluster using helm
### Pre-Requisites  🛠️
1. Install `helm`
2. Add ingress-nginx repo:
```shell
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```
3. Then update your local repositories
```shell
helm repo update
```

### Setup  ⚙️
1. Check if namespace exist
```shell
kubectl get ns
```
## Output
```
NAME              STATUS   AGE
argocd            Active   13d
default           Active   14d
ingress-nginx     Active   11d
kube-node-lease   Active   14d
kube-public       Active   14d
kube-system       Active   14d
msg-preds         Active   14d

```
2. If namespace doesn't exist (In my case it already exists ...)
```shell
kubectl create namespace msg-preds
```
3. Create kubectl postgres user and secret on the namespace
```shell
kubectl create secret generic pguser --from-literal=POSTGRES_USER=<your_postgres_user> -n msg-preds
```
```shell
kubectl create secret generic pgpassword --from-literal=POSTGRES_PASSWORD=<your_postgres_password> -n msg-preds
```

### Deploy services of `msg-preds` namespace.  🚀
4. Deploy db microservice
```shell
helm upgrade --install db ./charts/db -n msg-preds
```
5. Deploy kafka microservice
```shell
helm upgrade --install kafka ./charts/kafka -n msg-preds
```
6. Deploy app microservice
```shell
helm upgrade --install app ./charts/app -n msg-preds
```
7. Deploy worker microservice
```shell
helm upgrade --install worker ./charts/worker -n msg-preds
```
8. Deploy ingress microservice
```shell
helm upgrade --install ingress ./charts/ingress -n msg-preds
```
9. Deploy ingress-nginx controller
```shell
helm upgrade --install nginx ingress-nginx/ingress-nginx -n msg-preds
```
10. Verify the deployments
```shell
helm list -n msg-preds
```
11. Get all resources in the namespace
```shell
kubectl get all -n msg-preds -o wide
```

### Check the result  🎯
1. Go to `msg-preds.com/docs` and try some get & post requests.

### Delete all resources under `msg-preds` namespace  ❌
```shell
kubectl delete all --all -n msg-preds
```


## How to run on kubernetes using helmfile
### Pre-Requisites  🛠️
1. Install `helmfile`

### Deploy services of `msg-preds` namespace.  🚀
1. Deploy all micro-services:
```shell
helmfile -f ./charts/helmfile.yaml sync
```

### Check the result  🎯
1. Go to `msg-preds.com/docs` and try some get & post requests.

Also, you can run:
```shell
 helmfile -f ./charts/helmfile.yaml --output=json list
```

## Output
```
[
{"name":"app","namespace":"msg-preds","enabled":true,"installed":true,"labels":"","chart":"./charts/app","version":""},
{"name":"kafka","namespace":"msg-preds","enabled":true,"installed":true,"labels":"","chart":"./charts/kafka","version":""},
{"name":"db","namespace":"msg-preds","enabled":true,"installed":true,"labels":"","chart":"./charts/db","version":""},
{"name":"worker","namespace":"msg-preds","enabled":true,"installed":true,"labels":"","chart":"./charts/worker","version":""},
{"name":"nginx","namespace":"msg-preds","enabled":true,"installed":true,"labels":"","chart":"ingress-nginx/ingress-nginx","version":"4.11.2"},
{"name":"ingress","namespace":"msg-preds","enabled":true,"installed":true,"labels":"","chart":"./charts/ingress","version":""}
]
```


### Delete all resources under `msg-preds` namespace  ❌
```shell
helmfile -f ./charts/helmfile.yaml destroy
```


## How to deploy on kubernetes cluster using argocd
https://argo-cd.readthedocs.io/en/stable/

### Setup  ⚙️
1. Create `argocd` namespace
```shell
kubectl create namespace argocd
```
2. Deploy argocd
```shell
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```
3. Check the pods installed in `argocd` namespace
```shell
kubectl get pods -n argocd
```
4. Check the services installed in `argocd` namespace
```shell
kubectl get svc -n argocd
```

```shell
$ kubectl get svc -n argocd
````
### Output
```
NAME                                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
argocd-applicationset-controller          ClusterIP   10.98.12.88      <none>        7000/TCP,8080/TCP            2m24s
argocd-dex-server                         ClusterIP   10.105.202.50    <none>        5556/TCP,5557/TCP,5558/TCP   2m24s
argocd-metrics                            ClusterIP   10.110.98.102    <none>        8082/TCP                     2m24s
argocd-notifications-controller-metrics   ClusterIP   10.105.162.223   <none>        9001/TCP                     2m24s
argocd-redis                              ClusterIP   10.111.16.83     <none>        6379/TCP                     2m23s
argocd-repo-server                        ClusterIP   10.108.138.52    <none>        8081/TCP,8084/TCP            2m23s
argocd-server                             ClusterIP   10.99.157.152    <none>        80/TCP,443/TCP               2m23s
argocd-server-metrics                     ClusterIP   10.102.104.217   <none>        8083/TCP                     2m23s
```

5. Access argocd service - `port-forward`
```shell
kubectl port-forward -n argocd svc/argocd-server 8080:443
```

### Output
```
Forwarding from 127.0.0.1:8080 -> 8080
Forwarding from [::1]:8080 -> 8080
```

1. Go to `127.0.0.1:8080` in your browser, click on `Advanced` and then `proceed`.
2. The user for login is `admin`.
3. Gets the user secret
```shell
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```
4. Login using the decoded password
5. Configure `application.yaml`
6. Deploying with argocd for the first time
```shell
kubectl apply -f infra-apps.yaml
```

### Check the result  🎯
1. Go to argocd UI and see your new argocd app and its details.
2. Also, you can get all apps in all namespaces
```shell
kubectl get apps -A
```

## Output
```
NAMESPACE   NAME                    SYNC STATUS   HEALTH STATUS
argocd      msg-preds-infra-apps       Synced        Healthy
argocd      msg-preds-apps             Synced        Healthy
argocd      ingress-nginx              Synced        Healthy
```

Or get ArgoCD Application CRD (custom resource definition)

```shell
kubectl get crd
```

## Output
```
NAME                          CREATED AT
applications.argoproj.io      2024-10-04T09:26:31Z
applicationsets.argoproj.io   2024-10-04T09:26:31Z
appprojects.argoproj.io       2024-10-04T09:26:32Z
```

## After deploying argocd for the first time to the cluster it will be synced to the git repo


## Deploy and destroy the application on AWS EKS (Git Bash)

The complete AWS-only runbook is also available in [`aws/README.md`](aws/README.md).
The reusable GitHub Actions start/destroy lifecycle, one-time setup, and long-term
return checklist are documented separately in
[`aws/AUTOMATED-LAB.md`](aws/AUTOMATED-LAB.md).
Run these commands from the repository root. The supported Terraform root is
`aws/modules`; do not run Terraform from `aws` and do not use the Docker Desktop
`charts/helmfile.yaml` for EKS.

Prerequisites: AWS CLI v2, Terraform 1.16.x, Helm 3, kubectl, curl, Python, and
Docker Desktop when building images. The existing S3 backend is already configured.

The complete workflow is available as Git Bash scripts. Run them from the repository
root in numeric order:

```bash
bash aws/scripts/01-infrastructure.sh
bash aws/scripts/02-build-and-push.sh  # Docker Desktop must be running
bash aws/scripts/03-deploy-app.sh
bash aws/scripts/04-test.sh
bash aws/scripts/05-status.sh          # Optional
bash aws/scripts/06-destroy.sh         # Run after testing to stop AWS charges
bash aws/scripts/07-verify-destroyed.sh
```

The scripts and [`aws/README.md`](aws/README.md) are the supported procedure. The
older direct-Helm command transcript below is retained only as historical learning
material; it does not describe the current Argo CD deployment path.

<details>
<summary>Legacy direct-Helm AWS command transcript</summary>

### 1. Select the AWS account and initialize Terraform

```bash
export AWS_PROFILE="AwsDev"
export AWS_REGION="us-east-2"
export TF_VAR_region="$AWS_REGION"

ADMIN_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '\r\n')"
export TF_VAR_admin_cidrs="[\"${ADMIN_IP}/32\"]"
# Optional for a pre-existing IAM user:
export TF_VAR_admin_iam_users='["AwsDev"]'

aws sts get-caller-identity
terraform -chdir=aws/modules init -reconfigure
terraform -chdir=aws/modules validate
terraform -chdir=aws/modules state list
```

Confirm that `aws sts get-caller-identity` shows the intended account. For this
fresh learning deployment, `state list` should be empty. If your public IP changes,
set `TF_VAR_admin_cidrs` again and apply a new Terraform plan.

### 2. Create the network, EKS, and remaining AWS integrations

The two targeted applies are required only once for a fresh cluster. The complete
network must exist before EKS nodes bootstrap, and the EKS API must exist before
Terraform configures Helm. Always follow them with the complete plan.

```bash
terraform -chdir=aws/modules plan -target=module.network -out=network.tfplan
terraform -chdir=aws/modules apply network.tfplan

terraform -chdir=aws/modules plan -target=module.compute -out=cluster.tfplan
terraform -chdir=aws/modules apply cluster.tfplan

CLUSTER_NAME="$(terraform -chdir=aws/modules output -raw cluster_name)"
aws eks update-kubeconfig \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --alias msg-preds-eks
kubectl --context msg-preds-eks get nodes

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

### 3. Build and push the application images

Start Docker Desktop in Linux-container mode for this step.

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

Keep `APP_REPO`, `WORKER_REPO`, and `IMAGE_TAG` in this terminal for the Helm commands.

### 4. Deploy PostgreSQL, Kafka, the worker, the API, and ingress

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

If either Kafka command fails while the broker or consumer starts, wait briefly and
repeat it. The database uses a 10Gi encrypted gp3 EBS volume with deletion reclaim.

### 5. Run the end-to-end test

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

Expected output starts with `PASS: Swagger, API, PostgreSQL, Kafka and worker`.

### 6. Destroy the learning environment and stop charges

Run this section from the repository root. Removing ingress first gives the controller
time to delete the ALB. Capture the database volume ID before deleting its claim so it
can be checked afterward.

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
    --region "$AWS_REGION" >/dev/null 2>&1 && \
    echo "WARNING: EBS volume $DB_VOLUME_ID still exists; inspect and delete it." || \
    echo "Database EBS volume was deleted."
fi
```

The ECR repositories use `force_delete`, so their learning images are removed by
Terraform. Confirm that no load balancer, NAT gateway, EKS cluster, worker instance,
or database EBS volume remains. The pre-existing backend bucket and DynamoDB table
are deliberately excluded from the application destroy because they may hold state
history; remove them separately only when no Terraform configuration still uses them.

</details>
