## This project is for experimenting with FastAPI, Docker, and Kubernetes for microservice applications

## How to run via docker-compose
1. Install docker
2. Install docker-compose
3. Create a `.env.dev` and `.env` files in the root directory with the contents presented in the `.env.dev.example` and `.env.example` files.
4. In the terminal run `docker-compose -f docker-compose-dev.yml --env-file .env.dev up -d --build` for testing dev app locally.
5. Go to `http://127.0.0.1:8000/docs` to see the swagger docs
6. Go to `http://127.0.0.1:8000/redoc` to see the redoc docs
7. Go to `http://1270.0.0.1:8000/api/v1/messages` to send requests


## How to run via kubernetes
1. Install ingress-nginx: `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml`
2. Verify the installation: `kubectl get pods -n ingress-nginx`
3. Apply kubernetes files: `kubectl apply -f k8s`
4. Go to `msg-preds.com/docs` and try some get & post requests.
