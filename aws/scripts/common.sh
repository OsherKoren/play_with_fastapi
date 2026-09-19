#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_ENV="$REPO_ROOT/aws/.deploy.env"

export AWS_REGION="${AWS_REGION:-us-east-2}"
export TF_VAR_region="${TF_VAR_region:-$AWS_REGION}"
export TF_VAR_admin_iam_users="${TF_VAR_admin_iam_users:-[\"AwsDev\"]}"

# A named profile is convenient locally, but GitHub OIDC supplies temporary
# environment credentials and must not be forced to resolve a local profile.
if [[ -z "${AWS_ACCESS_KEY_ID:-}" && -z "${AWS_WEB_IDENTITY_TOKEN_FILE:-}" ]]; then
  export AWS_PROFILE="${AWS_PROFILE:-AwsDev}"
fi

cd "$REPO_ROOT"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required command is missing: $1" >&2
    exit 1
  }
}

load_deploy_env() {
  if [[ ! -f "$DEPLOY_ENV" ]]; then
    echo "Missing $DEPLOY_ENV. Run aws/scripts/02-build-and-push.sh first." >&2
    exit 1
  fi

  # Contains only ECR repository URLs and image content tags.
  source "$DEPLOY_ENV"
  APP_IMAGE_TAG="${APP_IMAGE_TAG:-${IMAGE_TAG:-}}"
  WORKER_IMAGE_TAG="${WORKER_IMAGE_TAG:-${IMAGE_TAG:-}}"
  export APP_REPO WORKER_REPO APP_IMAGE_TAG WORKER_IMAGE_TAG
}
