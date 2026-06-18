# spec-objects-architecture

> Filament Module: tier-2 architecture ObjectTypes (api_endpoint, data_schema, queue, action, ui_component, rate_limit, interface, external_contract, extension_point, binary_format)

This is an Agent-IX Filament module loaded by [`quire-cli`](https://github.com/agent-ix/quire-cli) and [`ix-spec`](https://github.com/agent-ix/ix-spec). It provides tier-2 embedded `object_types` — a `manifest.yaml` plus per-kind authoring `skeletons/` used to author and validate Markdown spec artifacts.

## Installing quire-cli

This module is consumed by the `quire` binary from [`quire-cli`](https://github.com/agent-ix/quire-cli), published on the public npm registry, so no auth or registry config is needed:

```bash
npm install -g @agent-ix/quire-cli
```

See [quire-cli#install](https://github.com/agent-ix/quire-cli#install) for full installation instructions.

## Object types provided

| Object | `type:` | Description |
|:-------|:--------|:------------|
| API endpoint | `api_endpoint` | An HTTP endpoint surface: a required `Endpoint` section describing what it does plus its method/path routes, and an optional `2. API Contract` section for request/response/auth detail. |
| Data schema | `data_schema` | A JSON-shaped record defined by a required `Schema` section holding a JSON Schema (draft 2020-12) code block. |
| Queue | `queue` | A message queue defined by a required `Message Format` section holding an example JSON message payload (or its schema). |
| Action | `action` | A discrete action/task defined by a required `Inputs` section listing every input it consumes, with type and source. |
| UI component | `ui_component` | A frontend component defined by a required `Props` section enumerating every prop with name, type, and behavior. |
| Rate limit | `rate_limit` | A throttling policy defined by a required `Thresholds` section listing the concrete limits, windows, and the response when a limit is exceeded. |
| Interface | `interface` | A language-neutral operations contract *within* the system, defined by a required `Contract` section holding a YAML code block (name, types, operations, invariants). |
| External contract | `external_contract` | A contract with a system *outside* this one, with a required `Contract` section plus optional `Endpoints` and `Behavior` sections for the consumed/exposed surface and interaction semantics. |
| Extension point | `extension_point` | First-class pluggability: a required `Contract` section naming the interface it exposes, plus optional `Registration` and `Stability` sections for discovery and compatibility guarantees. |
| Binary format | `binary_format` | A persisted binary layout defined by a required `Layout` section holding a YAML code block of record types with per-field name/offset/size/type/endianness. |

## How this module is used

### With ix-spec (recommended)

Install this module as a plugin, then author and review spec artifacts:

```bash
ix-spec plugin install path:../spec-objects-architecture
ix-spec catalog list
ix-spec write . --types api_endpoint,data_schema
ix-spec review
```

See [ix-spec](https://github.com/agent-ix/ix-spec) for details.

### With quire-cli directly

Point `quire` at this module's package directory to fetch a skeleton, validate documents, or extract a document's structured body:

```bash
quire schema api_endpoint --module ./spec_objects_architecture
quire validate spec/**/*.md --module ./spec_objects_architecture
quire extract spec/upload-artifact.md --module ./spec_objects_architecture
```

See [quire-cli#usage-instructions](https://github.com/agent-ix/quire-cli#usage-instructions) for details.

## Development

- **Library name:** `spec_objects_architecture` (flat layout, package at repo root)
- **Language / tooling:** Python 3.13+, [Poetry](https://python-poetry.org/), GitHub Actions CI
- **Versioning:** dynamic, Git-tag-based
- **Publishing:** Google Artifact Registry (PyPI-compatible) via `twine upload -r internal-pypi` in CI on `tag v*.*.*`

Common Makefile targets:

| Target | Description |
|:-------|:------------|
| `install` | Install dependencies in Poetry venv |
| `test` | Run tests (pytest) |
| `lint` | Run linting (Ruff + Black check) |
| `format` | Auto-format code (Ruff + Black) |
| `build` | Build wheel and sdist under `dist/` |
| `update-lock` | Update `poetry.lock` |
| `update-packages` | Update all dependencies |
| `add-package p=<name>` | Add a runtime dependency |
| `add-dev-package p=<name>` | Add a dev dependency |
| `use-local p=<name>` | Switch a dep to local `pypi.ix` |
| `use-upstream p=<name>` | Switch a dep back to upstream |
| `local-publish` | Build and publish to local PyPI (`pypi.ix`) |

CI requires the `GCP_SERVICE_ACCOUNT_KEY` secret plus the `GCP_REGION`, `GCP_PROJECT_NAME`, and `GCP_PYPI` variables for Artifact Registry publishing.

Licensed under MIT — see [LICENSE](./LICENSE).
