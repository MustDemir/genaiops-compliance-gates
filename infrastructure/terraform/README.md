# infrastructure/terraform/ — reserved (not part of the PoC)

This directory is a **reserved placeholder** for a future declarative
Infrastructure-as-Code (Terraform) provisioning path.

The PoC instantiation evaluated in the thesis (Azure AKS, Sweden Central,
2026-04-13) was provisioned **imperatively via the Azure CLI**, not Terraform:

- `../scripts/deploy-aks.sh` — Resource Group + ACR + AKS cluster, image
  build/push, Gatekeeper install, app + Evidence Store + monitoring deploy.
- `../scripts/setup-minikube.sh` — local equivalent for laptop reproduction.
- `../helm/` — Helm values for OPA Gatekeeper and the kube-prometheus-stack.

A Terraform module that reproduces the same topology declaratively is left as
future work and is intentionally out of the PoC scope (Demonstration/Evaluation
only, see thesis Kap. 1.7 / Tab. 1.2).
