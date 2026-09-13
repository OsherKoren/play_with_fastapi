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


## Deploy the same application on AWS EKS (PowerShell)

Run all commands from the repository root. This deploys FastAPI, PostgreSQL,
Kafka/ZooKeeper and the scoring worker in `msg-preds`, exposed through an AWS ALB.
Terraform's supported entry point is **`aws/modules`**.
The guard in `aws/main.tf` intentionally refuses deployment from the wrong directory.
Do not run the Docker Desktop `charts/helmfile.yaml` on EKS: it installs ingress-nginx.

Prerequisites: AWS CLI v2, Terraform 1.16.x, Helm 3, kubectl, and Docker Desktop
running Linux containers. Your AWS profile must have permission to provision VPC,
EKS, EC2, IAM, KMS, ECR, CloudWatch and the Terraform S3/DynamoDB backend.
The profile performing cluster creation gets Kubernetes administrator access.
AWS provider/module versions are constrained; commit `.terraform.lock.hcl` files.
Documentation was checked against the current official
[HashiCorp AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs),
[AWS EKS storage](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html), and
[AWS Load Balancer Controller](https://docs.aws.amazon.com/eks/latest/userguide/lbc-helm.html) documentation.
The reusable `terraform-aws-modules` packages are community modules, distinct from
HashiCorp's official AWS provider.

### 1. Select the account and backend

```powershell
$ErrorActionPreference = 'Stop'
$env:AWS_PROFILE = 'AwsDev'       # Your configured AWS CLI profile
$env:AWS_REGION = 'us-east-2'
$env:TF_VAR_aws_profile = $env:AWS_PROFILE
$env:TF_VAR_region = $env:AWS_REGION
aws sts get-caller-identity
if ($LASTEXITCODE -ne 0) { throw 'Log in to your AWS profile first' }
# For an SSO profile, use: aws sso login --profile $env:AWS_PROFILE
$AccountId = aws sts get-caller-identity --query Account --output text
$StateBucket = "msg-preds-$AccountId-tf-state"
$LockTable = 'msg-preds-dev-state-locking'
$AdminIp = (Invoke-RestMethod 'https://checkip.amazonaws.com').Trim()
$env:TF_VAR_admin_cidrs = '["' + $AdminIp + '/32"]'
```

Check that the printed account is yours. If your public IP changes, update
`TF_VAR_admin_cidrs` and apply Terraform before using kubectl again.

**Existing deployment:** use your existing backend bucket instead of the new default
above (the previous configuration used `msg-preds-dev-directive-tf-state`).
Both historical roots used `tf-infra/terraform.tfstate`. Before applying, run
`terraform -chdir=aws/modules state list` after initialization and inspect the plan.
Existing modular addresses start with `module.network.module.vpc` and
`module.compute.module.eks`; these addresses are retained. If the state instead
contains top-level `module.vpc` / `module.eks`, migrate/import those resources into
modular addresses before proceeding. Do not apply a plan that replaces the VPC or
cluster as a side effect of changing directories. An existing Kubernetes cluster
must be upgraded one minor version at a time; set `TF_VAR_kubernetes_version` to
the next supported upgrade step rather than jumping directly to 1.36.
To add the existing IAM user `AwsDev` to the administrator group, set
`$env:TF_VAR_admin_iam_users = '["AwsDev"]'`. SSO-only accounts can leave this empty.

For a **new backend only**, provision the bucket and lock table once:

```powershell
terraform -chdir=aws/backend-setup init
terraform -chdir=aws/backend-setup plan -var="s3_bucket=$StateBucket" -var="dynamodb_table=$LockTable" -out=backend.tfplan
terraform -chdir=aws/backend-setup apply backend.tfplan
```

Do not recreate an existing backend whose bootstrap state lives elsewhere.
Initialize the application infrastructure using that bucket:

```powershell
terraform -chdir=aws/modules init -reconfigure -backend-config="bucket=$StateBucket" -backend-config="dynamodb_table=$LockTable"
terraform -chdir=aws/modules validate
terraform -chdir=aws/modules state list
```

### 2. Create EKS, then install cluster integrations

For a **fresh cluster only**, bootstrap compute first so Helm has a reachable API.
This targeted apply is a one-time bootstrap; always follow it with the full plan/apply.

```powershell
terraform -chdir=aws/modules plan -target=module.compute -out=cluster.tfplan
terraform -chdir=aws/modules apply cluster.tfplan
```

Then run the normal full deployment (also the normal path for subsequent updates):

```powershell
terraform -chdir=aws/modules plan -out=eks.tfplan
# Inspect for unexpected deletion/replacement before applying.
terraform -chdir=aws/modules apply eks.tfplan
$ClusterName = terraform -chdir=aws/modules output -raw cluster_name
aws eks update-kubeconfig --name $ClusterName --region $env:AWS_REGION --profile $env:AWS_PROFILE --alias msg-preds-eks
kubectl --context msg-preds-eks get nodes
kubectl --context msg-preds-eks -n kube-system rollout status deployment/alb-controller-aws-load-balancer-controller --timeout=5m
kubectl --context msg-preds-eks -n kube-system rollout status deployment/ebs-csi-controller --timeout=5m
kubectl --context msg-preds-eks apply -f aws/k8s/storage-class.yaml
kubectl --context msg-preds-eks create namespace msg-preds --dry-run=client -o yaml | kubectl --context msg-preds-eks apply -f -
```

Terraform provisions two private worker nodes, NAT egress, correctly tagged public
ALB subnets, managed networking/DNS add-ons, controller IRSA, EBS CSI IAM/add-on,
and private ECR repositories. The public API is restricted to your admin CIDR.
No purchased domain is needed to test: use the ALB hostname.

### 3. Publish this checkout's images to your ECR repositories

Build fresh images rather than relying on the age of Docker Hub's `latest` tags.
Run Docker Desktop in Linux-container mode. Keep this tag for repeatable redeploys;
use a new tag for each rebuild because ECR tags are immutable.

```powershell
$Repos = terraform -chdir=aws/modules output -json image_repositories | ConvertFrom-Json
$Registry = ($Repos.app -split '/')[0]
$ImageTag = Get-Date -Format 'yyyyMMddHHmmss'
aws ecr get-login-password --region $env:AWS_REGION | docker login --username AWS --password-stdin $Registry
docker build --platform linux/amd64 -t "$($Repos.app):$ImageTag" ./app
if ($LASTEXITCODE -ne 0) { throw 'App image build failed' }
docker build --platform linux/amd64 -t "$($Repos.worker):$ImageTag" ./worker
if ($LASTEXITCODE -ne 0) { throw 'Worker image build failed' }
docker push "$($Repos.app):$ImageTag"
docker push "$($Repos.worker):$ImageTag"
```

### 4. Create secrets and deploy the application

For a fresh database, enter a database username and password. Reuse the same values
on redeployment: changing a Kubernetes Secret does not change an existing Postgres
password. Secrets are sent through stdin, not stored in Terraform state or files.

```powershell
$PgUser = Read-Host 'PostgreSQL username'
$PgSecure = Read-Host 'PostgreSQL password' -AsSecureString
$PgPassword = [System.Net.NetworkCredential]::new('', $PgSecure).Password
@{apiVersion='v1'; kind='Secret'; metadata=@{name='pguser';namespace='msg-preds'}; stringData=@{POSTGRES_USER=$PgUser}} | ConvertTo-Json -Depth 5 -Compress | kubectl --context msg-preds-eks apply -f -
@{apiVersion='v1'; kind='Secret'; metadata=@{name='pgpassword';namespace='msg-preds'}; stringData=@{POSTGRES_PASSWORD=$PgPassword}} | ConvertTo-Json -Depth 5 -Compress | kubectl --context msg-preds-eks apply -f -
Remove-Variable PgPassword, PgSecure

helm upgrade --install db ./charts/db --kube-context msg-preds-eks -n msg-preds -f charts/db/values-eks.yaml --wait --timeout 10m
helm upgrade --install kafka ./charts/kafka --kube-context msg-preds-eks -n msg-preds --wait --timeout 10m
# Wait for the broker itself, not only its Pod, before starting consumers.
kubectl --context msg-preds-eks -n msg-preds exec deployment/kafka -- kafka-topics --bootstrap-server kafka:9092 --list
# If the broker is still starting, repeat the command until it succeeds.
if ($LASTEXITCODE -ne 0) { throw "Kafka is not ready yet" }
helm upgrade --install worker ./charts/worker --kube-context msg-preds-eks -n msg-preds --set-string "image.repository=$($Repos.worker)" --set-string "image.tag=$ImageTag" --wait --timeout 10m
# Confirm the consumer has joined before submitting test messages (it starts at latest).
kubectl --context msg-preds-eks -n msg-preds exec deployment/kafka -- kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group MlEngineersGroup --state
# Repeat until STATE is Stable and the group has members, then continue.
helm upgrade --install app ./charts/app --kube-context msg-preds-eks -n msg-preds --set-string "image.repository=$($Repos.app)" --set-string "image.tag=$ImageTag" --wait --timeout 10m
helm upgrade --install ingress ./charts/ingress --kube-context msg-preds-eks -n msg-preds -f charts/ingress/values-eks.yaml --wait --timeout 10m
kubectl --context msg-preds-eks -n msg-preds get pods,svc,ingress,pvc
```

The EKS storage override uses a 10Gi encrypted gp3 volume and a `pgdata` subdirectory
so Postgres can initialize on an EBS filesystem. For an existing database, migrate
its data before changing its storage class or PGDATA path; these commands target
a fresh EKS database, not a transfer of Docker Desktop data.

### 5. End-to-end test

Allow several minutes for ALB provisioning and healthy targets. Retrieve its hostname:

```powershell
kubectl --context msg-preds-eks -n msg-preds get ingress ingress -w
# Ctrl+C after ADDRESS appears, then:
$AlbHost = kubectl --context msg-preds-eks -n msg-preds get ingress ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
if (-not $AlbHost) { throw 'The ALB has not been provisioned yet' }
$BaseUrl = "http://$AlbHost"
./aws/test-eks.ps1 -BaseUrl $BaseUrl
```

Expected output: `PASS: Swagger, API, PostgreSQL, Kafka and worker`, followed by the
message ID and score. The script checks `/docs` and health, posts a uniquely named
message to `/api/v1/messages/jobs`, then polls its score for up to 120 seconds and
checks the original message and score range. Open `$BaseUrl/docs` in a browser.
The score is random because this project uses a mock prediction model.

If the ALB is still starting, retry the test. For application failures:

```powershell
kubectl --context msg-preds-eks -n msg-preds get events --sort-by=.lastTimestamp
kubectl --context msg-preds-eks -n msg-preds logs deployment/app --tail=100
kubectl --context msg-preds-eks -n msg-preds logs deployment/worker --tail=100
kubectl --context msg-preds-eks -n kube-system logs deployment/alb-controller-aws-load-balancer-controller --tail=100
kubectl --context msg-preds-eks -n msg-preds describe pvc db-data
```

For `msg-preds.com`, use a domain you actually control: create a DNS alias to the
controller-created ALB in your authoritative hosted zone, then add that host to
the ingress rules. For HTTPS, obtain an ACM certificate in this region and set
`alb.ingress.kubernetes.io/certificate-arn`, HTTPS listen ports and SSL redirect
annotations. The baseline is an HTTP learning environment with mock authentication;
do not submit real personal data. PostgreSQL and Kafka remain internal Services.
Kafka is single-broker and ephemeral, matching the local experiment.

### Cleanup

Remove ingress first and let the controller delete its ALB before destroying EKS:

```powershell
helm uninstall ingress --kube-context msg-preds-eks -n msg-preds
kubectl --context msg-preds-eks -n msg-preds wait --for=delete ingress/ingress --timeout=10m
helm uninstall app worker kafka db --kube-context msg-preds-eks -n msg-preds
terraform -chdir=aws/modules plan -destroy -out=destroy.tfplan
terraform -chdir=aws/modules apply destroy.tfplan
```

ECR repositories refuse deletion while they contain images: explicitly remove the
images you no longer need before completing destroy. EBS volumes use `Retain`;
back up and explicitly delete unused retained volumes when you no longer need the
data. Backend storage is intentionally protected. EKS, EC2, NAT, ALB and retained
storage incur charges until removed. This is a small learning deployment, not a
high-availability database or Kafka installation.
