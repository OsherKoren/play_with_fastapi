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
1. Create namespace
```shell
kubectl create namespace msg-preds
```
1. Create kubectl postgres user and secret on the namespace
```shell
kubectl create secret generic pguser --from-literal=POSTGRES_USER=<your_postgres_user> -n msg-preds
```
```shell
kubectl create secret generic pgpassword --from-literal=POSTGRES_PASSWORD=<your_postgres_password> -n msg-preds
```

### Deploy services of `msg-preds` namespace.  🚀
1. Deploy db microservice
```shell
helm upgrade --install db ./helm/charts/db -n msg-preds
```
2. Deploy kafka microservice
```shell
helm upgrade --install kafka ./helm/charts/kafka -n msg-preds
```
3. Deploy app microservice
```shell
helm upgrade --install app ./helm/charts/app -n msg-preds
```
4. Deploy worker microservice
```shell
helm upgrade --install worker ./helm/charts/worker -n msg-preds
```
5. Deploy ingress microservice
```shell
helm upgrade --install ingress ./helm/charts/ingress -n msg-preds
```
6. Deploy ingress-nginx controller
```shell
helm upgrade --install nginx ingress-nginx/ingress-nginx -n msg-preds
```
7. Verify the deployments
```shell
helm list -n msg-preds
```
8. Get all resources in the namespace
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
helmfile -f .helm/helmfile.yaml sync
```

### Check the result  🎯
1. Go to `msg-preds.com/docs` and try some get & post requests.

### Delete all resources under `msg-preds` namespace  ❌
```shell
helmfile -f .helm/helmfile.yaml destroy
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

1. Go to ` 127.0.0.1:8080` in your browser, click on `Advanced` and then `proceed`.
2. The user for login is `admin`.
3. Gets the user secret
```shell
kubectl get secret argocd-initial-admin-secret -n argocd -o yaml
```
4. Decode the base64 encoded password
```shell
echo theBase64EncodedPassword== | base64 --decode
```
5. Login using the decoded password
6. Configure `application.yaml`
7. Deploying with argocd for the first time
```shell
kubectl apply -f argocd.yaml
```

## After deploying argocd for the first time to the cluster it will be synced to the git repo
