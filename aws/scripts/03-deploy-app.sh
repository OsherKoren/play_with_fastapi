#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"
load_deploy_env

for command in kubectl helm; do
  require_command "$command"
done

read -rp "PostgreSQL username: " PG_USER
read -rsp "PostgreSQL password: " PG_PASSWORD
echo

kubectl --context msg-preds-eks -n msg-preds create secret generic pguser \
  --from-literal=POSTGRES_USER="$PG_USER" --dry-run=client -o yaml | \
  kubectl --context msg-preds-eks apply -f -
kubectl --context msg-preds-eks -n msg-preds create secret generic pgpassword \
  --from-literal=POSTGRES_PASSWORD="$PG_PASSWORD" --dry-run=client -o yaml | \
  kubectl --context msg-preds-eks apply -f -
unset PG_USER PG_PASSWORD

helm upgrade --install db ./charts/db --kube-context msg-preds-eks \
  -n msg-preds -f charts/db/values-eks.yaml --wait --timeout 10m
helm upgrade --install kafka ./charts/kafka --kube-context msg-preds-eks \
  -n msg-preds --wait --timeout 10m
helm upgrade --install worker ./charts/worker --kube-context msg-preds-eks \
  -n msg-preds --set-string "image.repository=$WORKER_REPO" \
  --set-string "image.tag=$IMAGE_TAG" --wait --timeout 10m
helm upgrade --install app ./charts/app --kube-context msg-preds-eks \
  -n msg-preds --set-string "image.repository=$APP_REPO" \
  --set-string "image.tag=$IMAGE_TAG" --wait --timeout 10m
helm upgrade --install ingress ./charts/ingress --kube-context msg-preds-eks \
  -n msg-preds -f charts/ingress/values-eks.yaml --wait --timeout 10m

kubectl --context msg-preds-eks -n msg-preds get pods,svc,ingress,pvc
