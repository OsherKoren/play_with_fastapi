#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"

for command in terraform aws kubectl curl; do
  require_command "$command"
done

ADMIN_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '\r\n')"
export TF_VAR_admin_cidrs="[\"${ADMIN_IP}/32\"]"

PV_NAME="$(kubectl --context msg-preds-eks -n msg-preds get pvc db-data \
  -o jsonpath='{.spec.volumeName}' 2>/dev/null || true)"
DB_VOLUME_ID=""
if [[ -n "$PV_NAME" ]]; then
  DB_VOLUME_ID="$(kubectl --context msg-preds-eks get pv "$PV_NAME" \
    -o jsonpath='{.spec.csi.volumeHandle}' 2>/dev/null || true)"
fi

kubectl --context msg-preds-eks -n argocd delete applications.argoproj.io \
  msg-preds-ingress msg-preds-app msg-preds-worker msg-preds-kafka msg-preds-db \
  --ignore-not-found --wait=true --timeout=15m
kubectl --context msg-preds-eks -n msg-preds wait \
  --for=delete ingress/ingress --timeout=10m || true
kubectl --context msg-preds-eks delete namespace msg-preds --wait=true || true
kubectl --context msg-preds-eks delete storageclass gp3 --ignore-not-found

terraform -chdir=aws/modules plan -destroy -out=destroy.tfplan
terraform -chdir=aws/modules apply destroy.tfplan

if [[ -n "$DB_VOLUME_ID" ]]; then
  if aws ec2 describe-volumes --volume-ids "$DB_VOLUME_ID" \
    --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "WARNING: EBS volume $DB_VOLUME_ID still exists; inspect and delete it."
  else
    echo "Database EBS volume was deleted."
  fi
fi

rm -f "$DEPLOY_ENV"
