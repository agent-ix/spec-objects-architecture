# 🐍 spec-objects-architecture

> Filament Module: tier-2 architecture ObjectTypes (api_endpoint, ui_component, data_schema, action, queue, integration, dto, middleware)

---

## 📐 Project Structure and Development Philosophy

- **Library Name:** `spec_objects_architecture`
- **Layout:** Flat project layout (package at root, no `src/`)
- **Language:** Python 3.13+
- **Dependency Management:** [Poetry](https://python-poetry.org/)
- **Build and CI:** GitHub Actions
- **Publishing:** Google Artifact Registry (PyPI-compatible)

---

## 🛠 Prerequisites

- **Python 3.13+** installed on your system
- **Poetry 2.x** installed (`pip install poetry` or [official installer](https://python-poetry.org/docs/#installation))
- **devpi-client** (optional, for local publishing): `pip install devpi-client`

---

## 🚀 Quick Start

```bash
# Install dependencies and create venv
make install

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Build distribution
make build
```

---

## 📦 Build Process

- **Local Development**:
  - `make install` - Install dependencies in Poetry venv
  - `make test` - Run tests
  - `make format` - Auto-format code (Black + Ruff)
  - `make lint` - Run linting checks
- **Artifact Building**:
  - `make build` - Build wheel and sdist under `dist/`
- **Artifact Upload**:
  - Artifacts uploaded via `twine upload` in CI

---

## 🚀 Continuous Integration (CI)

- **GitHub Actions Workflow**:
  - Triggers: `push`, `pull_request`, `tag v*.*.*`
  - Runs tests and lint checks
  - Builds artifacts with `poetry build`
  - Publishes to Google Artifact Registry using `twine upload -r internal-pypi`

---

## 🔑 Required GitHub Secrets

| Secret Name | Purpose |
|:------------|:--------|
| `GCP_SERVICE_ACCOUNT_KEY` | Raw JSON of GCP Service Account Key |

| Variable Name | Purpose |
|:------------|:--------|
| `GCP_REGION` | GCP Region for Artifact Registry (e.g., `us-west1`) |
| `GCP_PROJECT_NAME` | GCP Project ID (e.g., `agent-ix`) |
| `GCP_PYPI` | Artifact Registry repository name (e.g., `internal-pypi`) |

---

## 🐳 Makefile Targets

| Target | Description |
|:-------|:------------|
| `install` | Install dependencies in Poetry venv |
| `build` | Build wheel and sdist artifacts |
| `test` | Run tests |
| `lint` | Run linting (Ruff + Black check) |
| `format` | Auto-format code (Black + Ruff --fix) |
| `shell` | Open Poetry shell |
| `clean` | Remove all build artifacts |
| `version` | Show project version |
| `info` | Show Git and version info |
| `update-lock` | Update poetry.lock |
| `update-packages` | Update all dependencies |
| `add-package p=<name>` | Add a production dependency |
| `add-dev-package p=<name>` | Add a dev dependency |
| `local-publish` | Build and publish to local PyPI |

---

## 🏠 Local Development with Local PyPI

For local development and testing, you can publish packages to the local PyPI proxy.

### Prerequisites

1. **Local Kubernetes cluster** running with PyPI proxy:
   ```bash
   # In the local repo
   make up
   make pypi-up
   ```

2. **devpi-client** installed locally:
   ```bash
   pip install devpi-client
   ```

### Publishing Locally

```bash
make local-publish
```

### Installing from Local PyPI

```bash
pip install --index-url http://pypi.ix/root/dev/+simple/ spec_objects_architecture
```

---

## 📜 Design Philosophy

- Native Poetry-based development (no Docker required for development)
- Isolated Poetry virtualenv (no global pip pollution)
- Direct uploads to Artifact Registry using correct PyPI-style authentication
- Always source-driven — no hand-editing built artifacts
- Dynamic, Git-tag-based versioning
- Clear Makefile and CI workflows matching production standards

---
