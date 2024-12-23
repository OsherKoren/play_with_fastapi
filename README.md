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
charts repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```
3. Then update your local repositories
```shell
charts repo update
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
charts upgrade --install db ./charts/db -n msg-preds
```
5. Deploy kafka microservice
```shell
charts upgrade --install kafka ./charts/kafka -n msg-preds
```
6. Deploy app microservice
```shell
charts upgrade --install app ./charts/app -n msg-preds
```
7. Deploy worker microservice
```shell
charts upgrade --install worker ./charts/worker -n msg-preds
```
8. Deploy ingress microservice
```shell
charts upgrade --install ingress ./charts/ingress -n msg-preds
```
9. Deploy ingress-nginx controller
```shell
charts upgrade --install nginx ingress-nginx/ingress-nginx -n msg-preds
```
10. Verify the deployments
```shell
charts list -n msg-preds
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
