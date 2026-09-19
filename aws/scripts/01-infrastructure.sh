#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"

for command in terraform aws kubectl curl; do
  require_command "$command"
done

ADMIN_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '\r\n')"
export TF_VAR_admin_cidrs="[\"${ADMIN_IP}/32\"]"

terraform version
aws sts get-caller-identity
terraform -chdir=aws/modules init -reconfigure
terraform -chdir=aws/modules validate

# The complete network must exist before private EKS nodes can bootstrap.
terraform -chdir=aws/modules plan -target=module.network -out=network.tfplan
terraform -chdir=aws/modules apply network.tfplan
terraform -chdir=aws/modules plan -target=module.compute -out=cluster.tfplan
terraform -chdir=aws/modules apply cluster.tfplan

CLUSTER_NAME="$(terraform -chdir=aws/modules output -raw cluster_name)"
aws eks update-kubeconfig \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --alias msg-preds-eks

terraform -chdir=aws/modules plan -out=eks.tfplan
terraform -chdir=aws/modules apply eks.tfplan

kubectl --context msg-preds-eks get nodes
kubectl --context msg-preds-eks -n kube-system rollout status \
  deployment/alb-controller-aws-load-balancer-controller --timeout=5m
kubectl --context msg-preds-eks -n kube-system rollout status \
  deployment/ebs-csi-controller --timeout=5m
kubectl --context msg-preds-eks apply -f aws/k8s/storage-class.yaml
kubectl --context msg-preds-eks create namespace msg-preds \
  --dry-run=client -o yaml | kubectl --context msg-preds-eks apply -f -
