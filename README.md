## This project is for experimenting with FastAPI, Docker, and Kubernetes for microservice applications

## How to run via docker-compose
### Pre-Requisites
1. Install `docker`
2. Install `docker-compose`

### Setup
1. Create a `.env.dev` and `.env` files in the root directory with the contents presented in the `.env.dev.example` and `.env.example` files.

### Command
1. In the terminal run `docker-compose -f docker-compose-dev.yml --env-file .env.dev up -d --build` for testing dev app locally.

### Check the result
1. Go to `http://127.0.0.1:8000/docs` to see the swagger docs
2. Go to `http://127.0.0.1:8000/redoc` to see the redoc docs
3. Go to `http://1270.0.0.1:8000/api/v1/messages` to send requests


## How to run via kubernetes
### Pre-Requisites
1. Install `kubctl`
2. Install ingress-nginx: `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml`
3. Verify the installation: `kubectl get all -n ingress-nginx`

### Setup
1. `kubectl create secret generic pguser --from-literal=POSTGRES_USER=<your_postgres_user>`
2. `kubectl create secret generic pgpassword --from-literal=POSTGRES_PASSWORD=<your_postgres_password>`

### Command
1. Apply kubernetes files using `default` namespace: `kubectl apply -f k8s`

### Check the result
1. Go to `msg-preds.com/docs` and try some get & post requests.

### Delete all resources under `default` namespace
1. Run `kubectl delete all --all`


## How to run via helm
### Pre-Requisites
1. Install `helm`
2. Add ingress-nginx repo: `helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx`
3. Then update your local repositories: `helm repo update`

### Setup
1. `kubectl create namespace msg-preds`
2. `kubectl create secret generic pguser --from-literal=POSTGRES_USER=<your_postgres_user> -n msg-preds`
3. `kubectl create secret generic pgpassword --from-literal=POSTGRES_PASSWORD=<your_postgres_password> -n msg-preds`

### Commands - Deploy services releases using `msg-preds` namespace.
1. Install/upgrade db micro-service `helm upgrade --install db ./helm/charts/db -n msg-preds`
2. Install/upgrade kafka micro-service `helm upgrade --install kafka ./helm/charts/kafka -n msg-preds`
3. Install/upgrade app micro-service `helm upgrade --install app ./helm/charts/app -n msg-preds`
4. Install/upgrade worker micro-service `helm upgrade --install worker ./helm/charts/worker -n msg-preds`
5. Install/upgrade ingress micro-service `helm upgrade --install ingress ./helm/charts/ingress -n msg-preds`
6. Install/upgrade ingress-nginx controller `helm upgrade --install nginx ingress-nginx/ingress-nginx -n msg-preds`
7. Verify the deployments: `helm list -n msg-preds`
8. Get all resources in the namespace: `kubectl get all -n msg-preds -o wide`

### Check the result
1. Go to `msg-preds.com/docs` and try some get & post requests.

### Delete all resources under `msg-preds` namespace
1. Run `kubectl delete all --all -n msg-preds`
