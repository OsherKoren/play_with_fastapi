#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"

if [[ -z "${APP_REPO:-}" || -z "${WORKER_REPO:-}" || \
      -z "${APP_IMAGE_TAG:-}" || -z "${WORKER_IMAGE_TAG:-}" ]]; then
  load_deploy_env
fi

for command in kubectl python; do
  require_command "$command"
done

if [[ "${CI:-false}" == "true" && ( -z "${PG_USER:-}" || -z "${PG_PASSWORD:-}" ) ]]; then
  echo "PG_USER and PG_PASSWORD must be loaded from SSM Parameter Store before deployment." >&2
  exit 1
fi

if [[ -z "${PG_USER:-}" ]]; then
  read -rp "PostgreSQL username: " PG_USER
fi
if [[ -z "${PG_PASSWORD:-}" ]]; then
  read -rsp "PostgreSQL password: " PG_PASSWORD
  echo
fi

kubectl --context msg-preds-eks create namespace msg-preds \
  --dry-run=client -o yaml | kubectl --context msg-preds-eks apply -f -
kubectl --context msg-preds-eks -n msg-preds create secret generic pguser \
  --from-literal=POSTGRES_USER="$PG_USER" --dry-run=client -o yaml | \
  kubectl --context msg-preds-eks apply -f -
kubectl --context msg-preds-eks -n msg-preds create secret generic pgpassword \
  --from-literal=POSTGRES_PASSWORD="$PG_PASSWORD" --dry-run=client -o yaml | \
  kubectl --context msg-preds-eks apply -f -
unset PG_USER PG_PASSWORD

ARGO_APPLICATIONS="$(mktemp)"
trap 'rm -f "$ARGO_APPLICATIONS"' EXIT
python - "$REPO_ROOT/aws/argocd/applications.yaml.tpl" "$ARGO_APPLICATIONS" <<'PY'
import os
import pathlib
import sys

content = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
replacements = {
    "__APP_REPO__": os.environ["APP_REPO"],
    "__WORKER_REPO__": os.environ["WORKER_REPO"],
    "__APP_IMAGE_TAG__": os.environ["APP_IMAGE_TAG"],
    "__WORKER_IMAGE_TAG__": os.environ["WORKER_IMAGE_TAG"],
}
for old, new in replacements.items():
    content = content.replace(old, new)
pathlib.Path(sys.argv[2]).write_text(content, encoding="utf-8")
PY

kubectl --context msg-preds-eks apply -f "$ARGO_APPLICATIONS"

echo "Waiting up to 20 minutes for all Argo CD applications to become Synced and Healthy..."
for _ in {1..120}; do
  if kubectl --context msg-preds-eks -n argocd get applications >/dev/null 2>&1; then
    READY="$(kubectl --context msg-preds-eks -n argocd get applications \
      -o jsonpath='{range .items[*]}{.metadata.name}:{.status.sync.status}:{.status.health.status}{"\n"}{end}' | \
      awk '$1 ~ /^msg-preds-/ && $1 !~ /:Synced:Healthy$/ {bad=1} END {print bad ? "false" : "true"}')"
    COUNT="$(kubectl --context msg-preds-eks -n argocd get applications \
      -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep -c '^msg-preds-' || true)"
    [[ "$COUNT" == "5" && "$READY" == "true" ]] && break
  fi
  sleep 10
done

STATUS="$(kubectl --context msg-preds-eks -n argocd get applications \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status --no-headers)"
echo "$STATUS"
FINAL_COUNT="$(echo "$STATUS" | awk '$1 ~ /^msg-preds-/ {count++} END {print count+0}')"
FINAL_READY="$(echo "$STATUS" | awk '$1 ~ /^msg-preds-/ && ($2 != "Synced" || $3 != "Healthy") {bad=1} END {print bad ? "false" : "true"}')"
if [[ "$FINAL_COUNT" != "5" || "$FINAL_READY" != "true" ]]; then
  echo "One or more Argo CD applications did not become healthy." >&2
  exit 1
fi

kubectl --context msg-preds-eks -n msg-preds get pods,svc,ingress,pvc
