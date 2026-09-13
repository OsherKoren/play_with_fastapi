#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"

for command in kubectl curl powershell.exe cygpath; do
  require_command "$command"
done

echo "Waiting up to 10 minutes for the Application Load Balancer address..."
ALB_HOST=""
for _ in {1..60}; do
  ALB_HOST="$(kubectl --context msg-preds-eks -n msg-preds get ingress ingress \
    -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)"
  [[ -n "$ALB_HOST" ]] && break
  sleep 10
done

if [[ -z "$ALB_HOST" ]]; then
  echo "The ALB address was not ready after 10 minutes." >&2
  exit 1
fi

BASE_URL="http://$ALB_HOST"
echo "Waiting up to 15 minutes for ALB DNS and the health endpoint..."
for _ in {1..90}; do
  if curl -fsS --max-time 10 "$BASE_URL/api/v1/health/" >/dev/null 2>&1; then
    break
  fi
  sleep 10
done

if ! curl -fsS --max-time 10 "$BASE_URL/api/v1/health/" >/dev/null 2>&1; then
  echo "The ALB health endpoint was not ready after 15 minutes: $BASE_URL" >&2
  exit 1
fi

echo "Testing $BASE_URL"
powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File "$(cygpath -w "$REPO_ROOT/aws/test-eks.ps1")" \
  -BaseUrl "$BASE_URL"
