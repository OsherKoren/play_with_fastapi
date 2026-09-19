apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: msg-preds-db
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/OsherKoren/play_with_fastapi.git
    targetRevision: main
    path: charts/db
    helm:
      releaseName: db
      valueFiles:
        - values.yaml
        - values-eks.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: msg-preds
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: msg-preds-kafka
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/OsherKoren/play_with_fastapi.git
    targetRevision: main
    path: charts/kafka
    helm:
      releaseName: kafka
  destination:
    server: https://kubernetes.default.svc
    namespace: msg-preds
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: msg-preds-worker
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/OsherKoren/play_with_fastapi.git
    targetRevision: main
    path: charts/worker
    helm:
      releaseName: worker
      parameters:
        - name: image.repository
          value: __WORKER_REPO__
        - name: image.tag
          value: __WORKER_IMAGE_TAG__
  destination:
    server: https://kubernetes.default.svc
    namespace: msg-preds
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: msg-preds-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/OsherKoren/play_with_fastapi.git
    targetRevision: main
    path: charts/app
    helm:
      releaseName: app
      parameters:
        - name: image.repository
          value: __APP_REPO__
        - name: image.tag
          value: __APP_IMAGE_TAG__
  destination:
    server: https://kubernetes.default.svc
    namespace: msg-preds
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: msg-preds-ingress
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/OsherKoren/play_with_fastapi.git
    targetRevision: main
    path: charts/ingress
    helm:
      releaseName: ingress
      valueFiles:
        - values.yaml
        - values-eks.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: msg-preds
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
