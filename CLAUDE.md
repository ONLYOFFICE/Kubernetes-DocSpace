## Project Overview

Kubernetes-DocSpace — Helm chart (`docspace`) deploying ONLYOFFICE DocSpace (room-based DMS) to Kubernetes or OpenShift. Runs ~25+ microservices (files, people-server, studio, router, doceditor, login, identity, notify, socket, backup, AI services, …) as separate applications, with ONLYOFFICE Docs pulled in as a subchart dependency (`onlyoffice/docs`, condition `docs.enabled`).

## Tech Stack

Helm 3, Kubernetes (>=1.19), OpenShift, Go templates, GitHub Actions, external MySQL + Redis + RabbitMQ (bitnami charts), OpenSearch, NFS/RWX storage

## Project Structure

```
Chart.yaml          — chart metadata (name: docspace; dependency: docs subchart from https://download.onlyoffice.com/charts/stable)
values.yaml         — all chart parameters (very large, ~6k lines; one top-level block per service)
templates/          — manifests: applications/ (one YAML per service: files.yaml, router.yaml, studio.yaml, identity.yaml, ai.yaml, …), configmaps/, jobs/, ingresses/, hpa/, pvc/, secrets/, serviceaccounts/, services/, tests/, RBAC/, _helpers.tpl, NOTES.txt
sources/            — auxiliary manifests: mysql_values.yaml (for bitnami mysql install), elasticsearch-clear-indexes.yaml, scc/ (OpenShift), scripts/
.github/workflows/  — lint.yaml (shared ONLYOFFICE/ga-common helm-lint + deprecated-resources), 4testing_repo.yaml / stable_repo.yaml (chart publishing)
CHANGELOG.md
```

## Build & Run

```bash
# Lint / render locally (fetch the docs subchart first)
helm dependency update
helm lint .
helm template docspace .

# Install from the published repo
helm repo add onlyoffice https://download.onlyoffice.com/charts/stable
helm install [RELEASE_NAME] -f values.yaml onlyoffice/docspace

# Enterprise edition
helm install [RELEASE_NAME] -f values.yaml onlyoffice/docspace --set global.installationType=ENTERPRISE

# Upgrade (version upgrades run hooks; parameter-only changes use --no-hooks)
helm upgrade [RELEASE_NAME] -f values.yaml onlyoffice/docspace --timeout 15m
helm upgrade [RELEASE_NAME] onlyoffice/docspace --set jwt.enabled=false --no-hooks

# Uninstall
helm uninstall [RELEASE_NAME]
```

## Key Patterns

- One top-level `values.yaml` block per service (`files`, `router`, `studio`, `identity`, `ai`, `backup`, …) with a matching manifest in `templates/applications/` — adding a service touches both plus the README table
- ONLYOFFICE Docs is a versioned subchart dependency in `Chart.yaml` — bump its pinned version deliberately
- External dependencies (MySQL, Redis, RabbitMQ) installed separately via bitnami charts; MySQL uses `sources/mysql_values.yaml`
- Helm hooks handle upgrade migrations (library cleanup/refill) — `--no-hooks` for config-only changes
- Exposure options: router LoadBalancer service, ingress (`ingress.enabled`), or Gateway API
- Editions switched via `global.installationType` (COMMUNITY/ENTERPRISE); JWT and connection strings under `connections.*` / `jwt.*`
- OpenShift support via `sources/scc/` and podSecurityContext toggles

## Review Focus

**Templates**: label/selector consistency across ~28 application manifests, helper reuse in `_helpers.tpl`
**Values**: new keys documented in the README parameter table; per-service blocks follow the established shape (replicas, image, resources, probes)
**Secrets**: passwords/JWT via Secrets or existingSecret patterns, never plain defaults
**Hooks**: upgrade job correctness and timeouts; `--no-hooks` path unaffected
**Subchart**: docs dependency version pin matches the intended Docs release

## Git Workflow

- **Main branch**: `main`
- **Integration branch**: `develop`
- **Branch naming**: `feature/*`, `bugfix/*`, `fix/*`
- Update `CHANGELOG.md` and bump `version` in `Chart.yaml` for release changes
