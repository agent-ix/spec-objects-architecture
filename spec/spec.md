---
type: master-requirements
name: spec-objects-architecture
org: agent-ix
component_type: filament-module
implementation_language: python
tags:
  - filament
  - spec-objects
  - architecture
depends_on: []
standards_alignment:
  - iso-iec-ieee-29148
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/filament-core-data/FR-031"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/quoin/FR-070"
    type: "depends_on"
    cardinality: "1:1"
  - target: "ix://agent-ix/quire-rs/FR-069"
    type: "depends_on"
    cardinality: "1:1"
security_critical: false
---
# Master Requirements Specification

## Purpose

This document specifies the requirements for `spec-objects-architecture`, a
Filament Module that contributes tier-2 architecture ObjectTypes. Architecture
specs need extractable graph entities for API endpoints, data schemas, queues,
actions, UI components, interfaces, external contracts, extension points,
binary formats, and rate limits; this module ships those ObjectTypes (with
their skeletons and schemas) so that authors, reviewers, and agent generators
share one authoritative definition of what the module activates against
`filament-core`.

## Scope

### In Scope

- The Module manifest (`spec_objects_architecture/manifest.yaml`) and the ten
  tier-2 architecture ObjectTypes it contributes.
- The functional requirement that the manifest activates idempotently against
  `filament-core-service`, and the integration test that verifies it.
- The semantic-module contract (issue #8): a TypeSpec source importing
  `@agent-ix/semantic-core` 0.1.0, the emitted JSON Schema per declared type
  shipped under `spec_objects_architecture/schemas/`, the manifest `semantic`
  block with reference-form `data_schema`, and the skeletons rewritten as
  executable typed fixtures with negative counterparts.
- The architecture-specific lowerings this module owns: `interface`
  `contract_yaml` to `OperationDecl[]`, the `data_schema` `schema_json` fence
  registering its record as a `TypeRef` target, and `api_endpoint` operation
  inputs and outputs referencing those records by `TypeRef`.

### Out of Scope

- The behaviour of `filament-core-service` itself, referenced here only by the
  relationship to its manifest schema (FR-035).
- Deployment topology and cluster infrastructure, which live in the operating
  environment rather than this specification.
- Generated-language fixtures (Rust, TypeScript, Python) for the architecture
  types: produced by the compiler backends `agent-ix/filament-core-data#21`
  (Rust), `#22` (TypeScript) and `#23` (Python), and published only behind the
  promotion gate (`agent-ix/quoin#290`); the semantic-core language packages
  are `agent-ix/filament-core-data#11`. None is produced or faked here.
- Extraction of the declared-but-not-yet-extracted keys (`routes`, `carries`,
  `delivery`, `exposes`, `registration`, `stability`, `versioning`,
  `provider`, `records`, `thresholds`, `throttles`, `renders`, `requires`,
  `associated_types`) from Markdown: the mapping is owned by
  `agent-ix/quoin#335` (FR-071/FR-072 define `Properties`, `Invariants`, and
  `Operations` only) and the extractor by `agent-ix/quire-rs` once the mapping
  is published; the schemas declare the keys as optional so the engine can
  fill them without a schema change.
- Enabling impact propagation or extraction behaviour for the architecture
  resource graph: the ticket's safety gate holds the change advisory-only
  until promotion, and resource-identity changes need controlled-corpus
  evidence this module does not gather.
- Naming what a module load refused: `agent-ix/quire-rs#221` (an unknown
  manifest key empties the model silently) and `agent-ix/quire-rs#394` (a
  `data_schema` digest mismatch drops the object type with no diagnostic).
  FR-003-AC-6's "naming the key or the path" half is blocked on them and is
  carried as an explicit expected failure.
- Record validation of a legacy-form artifact that declares `object:`:
  `agent-ix/quire-rs#391` (the engine validates an `unavailable` record as
  `{}`, so a legacy form errors even under `legacy_forms: warning`).
  NFR-001-AC-2 itself holds — no 0.2.0 artifact carries `object:` — and the
  defect is carried as an explicit expected failure beside it rather than
  worked around by relaxing a schema.
- Publishing the Quire 0.46.0 wheel to an index a repository may commit
  against: `agent-ix/quire-rs#392`. `internal-pypi` serves 0.33.0 at most and
  no `quire-rs` tag carries the semantic layer, so this module provisions the
  wheel with a documented `make dev-quire` target and its semantic tests fail
  rather than skip when the engine is absent (FR-005).
- Resolving a reference-form `data_schema` into a stored snapshot at
  activation: `agent-ix/filament-core-service#23`. Until it lands the service
  stores the reference verbatim, which is what FR-001-AC-4 and IT-001-SC-03
  assert.
- Editing any corpus repository or vendored fixture, and the malformed
  `lexicon` entries the corpus carries; the legacy-form sweep and corpus
  promotion are `agent-ix/quoin#291`.
- Replacing the measured cross-language resource-extraction contracts of
  Project 17: this module aligns resource vocabulary with them and does not
  restate or supersede them.

## System Overview

### System Description

`spec-objects-architecture` is a Python package that publishes a Filament
Module manifest declaring ten tier-2 ObjectTypes for technical architecture
modelling. The manifest is activated against `filament-core-service` over its
HTTP API, which registers the declared archetypes, object types, grammars, and
artifact types.

### Intended Users

The Filament platform (which activates and serves the contributed
ObjectTypes), spec authors (who model architecture using them), and agent CLI
generators such as `minijinja-cli` (which produce artifacts from the shipped
skeletons and schemas).

## Requirements Architecture

The requirement classes that make up this specification trace from the
stakeholder need for extractable architecture graph entities (`stakeholder/`)
through the maintainer's story of declaring those types against semantic-core
(`usecase/`) to the functional requirements (`functional/`): FR-001 activates
the manifest against `filament-core`; FR-002 emits the schemas; FR-003
declares the semantic contract in the manifest; FR-004 fixes each type's
role-distinct schema; FR-005 makes the skeletons executable fixtures; FR-006
fixes the three architecture-specific lowerings. NFR-001 bounds the change to
additive compatibility. Integration tests in `integration/` verify the
activation and Quoin-install boundaries; the third external boundary, the
Quire engine (loader, extraction, record surface), has no IT artifact of its
own — the FR-003, FR-005 and FR-006 test harness is this module's Quire
contract test, and the wheel version is pinned once in FR-005 Inputs. The Test
Matrix in `tests.md` records every criterion's test case.

## References

- ISO/IEC/IEEE 29148 — Requirements engineering.
- This module's source repository and `manifest.yaml`.
- `filament-core-service` FR-035 (Module Manifest Schema), the upstream
  specification this module's manifest conforms to.
- `agent-ix/filament-core-data` FR-031..FR-034 (semantic-core grammar,
  scalars, JSON Schema projection, lowering) and ADR-0005 (TypeSpec source).
- `agent-ix/quoin` FR-070..FR-075 (semantic-module contract, mappings,
  `data_schema` by digest, legacy forms, package manifests).
- `agent-ix/quire-rs` FR-069..FR-072 (contract at load, typed Properties,
  clauses and operations, extraction surface).
- `agent-ix/spec-objects-business` issue #4, the first module to adopt this
  contract and the shape this module follows.
