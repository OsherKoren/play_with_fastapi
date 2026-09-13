#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_ENV="$REPO_ROOT/aws/.deploy.env"

export AWS_PROFILE="${AWS_PROFILE:-AwsDev}"
export AWS_REGION="${AWS_REGION:-us-east-2}"
export TF_VAR_aws_profile="${TF_VAR_aws_profile:-$AWS_PROFILE}"
export TF_VAR_region="${TF_VAR_region:-$AWS_REGION}"
export TF_VAR_admin_iam_users="${TF_VAR_admin_iam_users:-[\"AwsDev\"]}"

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

  # Contains only ECR repository URLs and the generated image tag.
  source "$DEPLOY_ENV"
  export APP_REPO WORKER_REPO IMAGE_TAG
}
