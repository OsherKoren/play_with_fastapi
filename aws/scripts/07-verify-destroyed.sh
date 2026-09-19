#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"

for command in terraform aws; do
  require_command "$command"
done

failures=0

if terraform -chdir=aws/modules state list | grep -q .; then
  echo "ERROR: disposable Terraform state is not empty." >&2
  terraform -chdir=aws/modules state list >&2
  failures=1
fi

if aws eks describe-cluster --name msg-preds-dev --region "$AWS_REGION" >/dev/null 2>&1; then
  echo "ERROR: EKS cluster msg-preds-dev still exists." >&2
  failures=1
fi

for repository in msg-preds-dev/app msg-preds-dev/worker; do
  if aws ecr describe-repositories --repository-names "$repository" \
    --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "ERROR: ECR repository $repository still exists." >&2
    failures=1
  fi
done

NAT_COUNT="$(aws ec2 describe-nat-gateways --region "$AWS_REGION" \
  --filter "Name=tag:Name,Values=msg-preds*" "Name=state,Values=pending,available" \
  --query 'length(NatGateways)' --output text)"
if [[ "$NAT_COUNT" != "0" ]]; then
  echo "ERROR: $NAT_COUNT msg-preds NAT gateway(s) still exist." >&2
  failures=1
fi

INSTANCE_COUNT="$(aws ec2 describe-instances --region "$AWS_REGION" \
  --filters "Name=tag:eks:cluster-name,Values=msg-preds-dev" \
  "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'length(Reservations[].Instances[])' --output text)"
if [[ "$INSTANCE_COUNT" != "0" ]]; then
  echo "ERROR: $INSTANCE_COUNT EKS EC2 instance(s) still exist." >&2
  failures=1
fi

VOLUME_COUNT="$(aws ec2 describe-volumes --region "$AWS_REGION" \
  --filters "Name=tag:kubernetes.io/cluster/msg-preds-dev,Values=owned" \
  --query 'length(Volumes)' --output text)"
if [[ "$VOLUME_COUNT" != "0" ]]; then
  echo "ERROR: $VOLUME_COUNT Kubernetes EBS volume(s) still exist." >&2
  failures=1
fi

LOAD_BALANCER_COUNT="$(aws resourcegroupstaggingapi get-resources --region "$AWS_REGION" \
  --resource-type-filters elasticloadbalancing:loadbalancer \
  --tag-filters Key=elbv2.k8s.aws/cluster,Values=msg-preds-dev \
  --query 'length(ResourceTagMappingList)' --output text)"
if [[ "$LOAD_BALANCER_COUNT" != "0" ]]; then
  echo "ERROR: $LOAD_BALANCER_COUNT Kubernetes load balancer(s) still exist." >&2
  failures=1
fi

if [[ "$failures" -ne 0 ]]; then
  echo "Cleanup verification failed. Inspect AWS before assuming charges have stopped." >&2
  exit 1
fi

echo "PASS: Terraform state and the checked EKS, EC2, NAT, EBS, load balancer, and ECR resources are gone."
echo "The persistent state bucket and GitHub OIDC bootstrap remain intentionally."
