#!/usr/bin/env bash

source "$(dirname -- "$0")/common.sh"
require_command kubectl

kubectl --context msg-preds-eks get nodes
kubectl --context msg-preds-eks -n argocd get applications
kubectl --context msg-preds-eks -n msg-preds get pods,svc,ingress,pvc
kubectl --context msg-preds-eks -n msg-preds get events --sort-by=.lastTimestamp
