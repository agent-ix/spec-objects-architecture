---
id: Plan-001
title: "spec-objects-architecture — semantic data schemas (issue #8)"
type: Plan
status: active
relationships:
  - target: ix://agent-ix/spec-objects-architecture/StR-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/US-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-002
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-003
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-004
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-005
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-006
    type: references
  - target: ix://agent-ix/spec-objects-architecture/NFR-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/IT-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/IT-002
    type: references
---
# Implementation Plan: semantic data schemas

## Requirements Summary

### Stakeholder Requirements
- [x] **StR-001**: Architecture specifications yield extractable graph entities; every architecture object carries one typed structural contract downstream frontends can read (VC-1..VC-3).

### User Stories
- [x] **US-001**: Declare every architecture object type against the shared semantic-core grammar, so one declaration record per object validates identically in Quire, Quoin and the compiler.

### Functional Requirements
- [x] **FR-001**: The manifest conforms to filament-core-service FR-035 at revision `a77f31e` and activates idempotently; the `lexicon` refusal is carried as an expected failure naming `agent-ix/filament-core-service#25`.
- [x] **FR-002**: Emit one JSON Schema 2020-12 document per model from `typespec/main.tsp` with the official `@typespec/json-schema` emitter at a pinned toolchain; normalize `$id`/`$ref`; gate drift; package the schemas into the wheel and the npm tarball; version-embedded `$id` with an atomic bump procedure.
- [x] **FR-003**: `manifest.yaml` at version 0.3.0 carries the quoin FR-070 `semantic` block and a reference-form `data_schema` (path + digest) per exported object type, with every 0.2.0 locator and the `lexicon` unchanged.
- [x] **FR-004**: One role-distinct model per architecture object type — required, forbidden and item rules — with every grammar item by `$ref` to semantic-core 0.1.0 and no redeclaration.
- [x] **FR-005**: Every skeleton is an executable typed fixture in the quoin FR-071/FR-072 Markdown forms, with three `sysml` alternates and ten negative fixtures; the semantic suite fails rather than skips when the engine is absent.
- [x] **FR-006**: The three architecture-specific lowerings this module owns — `interface.contract_yaml` to `OperationDecl[]`, `data_schema.schema_json` as a registered `TypeRef` target, and `api_endpoint` inputs and outputs by `TypeRef` — each proved by an agreement assertion between two sections of one authored artifact.

### Non-Functional Requirements
- [x] **NFR-001**: Additive compatibility — the checked-in 0.2.0 skeleton set still validates at 0.3.0, every 0.2.0 locator definition and edge vocabulary is unchanged, and every 0.2.0 locator yield is byte-identical.

### Integration Test Requirements
- [ ] **IT-001**: Activation roundtrip against a running filament-core-service at `a77f31e` or later. Not run: no release tag contains that revision and this repository cannot provision the service.
- [x] **IT-002**: `quoin module install path:<dir>` accepts the semantic contract and the prior module state is restored unconditionally.

## Dependency Graph

### Core dependency edges

- `FR-002 (toolchain half) -> FR-004`
  The models cannot be authored until `tsp compile` runs against
  `@agent-ix/semantic-core` 0.1.0 and the generator normalizes what it emits.
- `FR-004 -> FR-002 (emitted-set half)`
  FR-002-AC-1/AC-2/AC-3 assert the emitted file set, its `$id`s and its `$ref`s,
  none of which exist before FR-004 declares the models. The apparent cycle is
  broken by splitting FR-002 into an enablement half (generator, drift gate,
  packaging) that precedes FR-004 and an emitted-set half that follows it.
- `FR-002 (emitted set) + FR-001 -> FR-003`
  The manifest references the emitted files by path and digest, and the 0.3.0
  manifest must still be an FR-035-valid manifest.
- `FR-003 + FR-004 -> FR-005`
  A skeleton cannot be an executable fixture until the manifest resolves a
  schema for its type.
- `FR-005 -> FR-003 (added locators)`
  A locator can only assert a section that exists. Task-005 lands the sections,
  Task-006 adds their `required: false` locators.
- `FR-005 -> FR-006`
  The agreement assertions read the authored skeletons.
- `FR-003 + FR-005 + FR-006 -> NFR-001`
  Additivity is measured against the finished 0.3.0 manifest.

### Critical path

Task-007 (environment) → Task-001 (toolchain) → Task-002 (models) →
Task-003 (emitted set) → Task-004 (manifest) → Task-005 (skeletons) →
Task-006 (locators) → Task-013 (gate).

## Execution Tracks

- **Track A (critical path)**: Task-007, Task-001, Task-002, Task-003, Task-004, Task-005, Task-006.
- **Track B (parallel once Track A reaches Task-005)**: Task-008 (NFR-001), Task-009 (FR-006), Task-010 (consumer boundaries).
- **Track C (post-critical-path)**: Task-011 (IT-002), Task-012 (FR-001 and the expected failures).
- **Gate**: Task-013.

## Quality Gates

1. **Emitter feasibility** (after Task-002): the `@contains` / `@minContains` /
   `@maxContains` / `@maxItems` recipe survives a real 2020-12 validator with the
   schemas sealed. Failing this, the item rules are re-expressed, never dropped.
2. **No vacuous skip** (Task-007): a semantic test with no engine **fails**. A
   skipped row is not coverage.
3. **Additivity** (Task-008): zero 0.2.0 locators changed, zero error findings on
   the 0.2.0 skeleton set, zero edge-vocabulary changes.
4. **End-to-end gate** (Task-013): three types — an operation-shaped one, a
   field-shaped one and a clause-shaped one — validate, extract, resolve and refuse
   as specified before the plan is declared done.

## Test Plan

The matrix in `spec/tests.md` is authoritative; this plan owns which task lands
each row.

| Rows | Task |
|---|---|
| TC-010..TC-019, TC-071..TC-074 | Task-001, Task-003 |
| TC-007, TC-030..TC-044 | Task-002 |
| TC-020..TC-026, TC-028 | Task-004 |
| TC-050..TC-059, TC-065 | Task-005 |
| TC-023 | Task-006 |
| TC-060..TC-064 | Task-008 |
| TC-080..TC-086 | Task-009 |
| TC-090, TC-091 | Task-010 |
| TC-027, TC-070 | Task-011 |
| TC-001..TC-006 | Task-012 |

`quire coverage` reports 141/141 rows backed: 71 `TC-` rows plus 59 criterion
rows minted from the requirements. `make test` reports 163 passed, 7 skipped and
4 expected failures; the skips are environment-gated and the expected failures
each name the issue that owns them.
