#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"

for command in terraform aws docker python sha256sum; do
  require_command "$command"
done

docker info >/dev/null

APP_REPO="$(terraform -chdir=aws/modules output -json image_repositories | python -c 'import json,sys; print(json.load(sys.stdin)["app"])')"
WORKER_REPO="$(terraform -chdir=aws/modules output -json image_repositories | python -c 'import json,sys; print(json.load(sys.stdin)["worker"])')"
REGISTRY="${APP_REPO%%/*}"
APP_IMAGE_TAG="${APP_IMAGE_TAG:-$(git ls-files app/.dockerignore app/Dockerfile app/pyproject.toml app/src | sort | xargs sha256sum | sha256sum | awk '{print $1}')}"
WORKER_IMAGE_TAG="${WORKER_IMAGE_TAG:-$(git ls-files worker/.dockerignore worker/Dockerfile worker/pyproject.toml worker/src | sort | xargs sha256sum | sha256sum | awk '{print $1}')}"

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$REGISTRY"
if ! aws ecr describe-images --repository-name "${APP_REPO#*/}" \
  --image-ids "imageTag=$APP_IMAGE_TAG" --region "$AWS_REGION" >/dev/null 2>&1; then
  docker build --platform linux/amd64 --target production -t "${APP_REPO}:${APP_IMAGE_TAG}" ./app
  docker push "${APP_REPO}:${APP_IMAGE_TAG}"
fi
if ! aws ecr describe-images --repository-name "${WORKER_REPO#*/}" \
  --image-ids "imageTag=$WORKER_IMAGE_TAG" --region "$AWS_REGION" >/dev/null 2>&1; then
  docker build --platform linux/amd64 --target production -t "${WORKER_REPO}:${WORKER_IMAGE_TAG}" ./worker
  docker push "${WORKER_REPO}:${WORKER_IMAGE_TAG}"
fi

cat >"$DEPLOY_ENV" <<EOF
APP_REPO='$APP_REPO'
WORKER_REPO='$WORKER_REPO'
APP_IMAGE_TAG='$APP_IMAGE_TAG'
WORKER_IMAGE_TAG='$WORKER_IMAGE_TAG'
EOF

echo "Application tag: $APP_IMAGE_TAG"
echo "Worker tag: $WORKER_IMAGE_TAG"
echo "Deployment settings saved to aws/.deploy.env."
