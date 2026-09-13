#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"

for command in terraform aws docker python; do
  require_command "$command"
done

docker info >/dev/null

APP_REPO="$(terraform -chdir=aws/modules output -json image_repositories | python -c 'import json,sys; print(json.load(sys.stdin)["app"])')"
WORKER_REPO="$(terraform -chdir=aws/modules output -json image_repositories | python -c 'import json,sys; print(json.load(sys.stdin)["worker"])')"
REGISTRY="${APP_REPO%%/*}"
IMAGE_TAG="${IMAGE_TAG:-$(date -u +%Y%m%d%H%M%S)}"

aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" | \
  docker login --username AWS --password-stdin "$REGISTRY"
docker build --platform linux/amd64 -t "${APP_REPO}:${IMAGE_TAG}" ./app
docker build --platform linux/amd64 -t "${WORKER_REPO}:${IMAGE_TAG}" ./worker
docker push "${APP_REPO}:${IMAGE_TAG}"
docker push "${WORKER_REPO}:${IMAGE_TAG}"

cat >"$DEPLOY_ENV" <<EOF
APP_REPO='$APP_REPO'
WORKER_REPO='$WORKER_REPO'
IMAGE_TAG='$IMAGE_TAG'
EOF

echo "Images pushed with tag $IMAGE_TAG. Deployment settings saved to aws/.deploy.env."
