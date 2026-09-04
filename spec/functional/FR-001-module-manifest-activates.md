---
id: FR-001
title: "Module manifest activates against filament-core"
type: FR
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/StR-001"
    type: "traces_to"
---
# FR-001: Module manifest activates against filament-core

## Description

The module **SHALL** publish a Filament Module manifest
(`spec_objects_architecture/manifest.yaml`) that conforms to
filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) at
revision `a77f31e` and activates idempotently against
`POST /api/v1/modules/activate`.

## Inputs

- `manifest.yaml` (this repo's package).
- The FR-035 module-manifest schema at `agent-ix/filament-core-service`
  revision `a77f31e` (CR-003), which is the revision that admits the
  `semantic` block and the reference-form `data_schema`, and the revision
  Quoin and Quire each vendor byte-identically
  (`sha256:69cf9738600e7d8daa45ed5cd7231b17ca8dc58d068bd36af9b0d2c9b69dcbbc`).
  No release tag contains it. [FR-003](./FR-003-semantic-manifest-contract.md)
  names the same revision, so both requirements judge one schema.
- Activation endpoint: `POST /api/v1/modules/activate`.

## Outputs

- A module row in the service's `modules` table.
- The contributed archetypes, object types, grammars and artifact types the
  manifest declares.

## Behavior

- The manifest **SHALL** validate against the `module-manifest.schema.json`
  revision Inputs pins.
- Re-activation **SHALL** produce no change, being idempotent by content hash
  (filament-core-service FR-026-AC-1).
- The manifest carries a top-level `lexicon` block (the FR-043 concrete-term
  vocabulary Quire reads) which the pinned FR-035 schema does not declare and
  its `additionalProperties: false` therefore refuses. This is measured, not
  assumed, and it predates the semantic contract: the 0.2.0 manifest fails the
  same way. `agent-ix/filament-core-service#25` owns admitting the key. Until
  it lands FR-001-AC-1 is carried as an explicit expected failure naming that
  issue, beside a criterion that the `lexicon` key is the **only** violation —
  so nothing this module added is refused.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | The manifest validates against the pinned FR-035 schema, whose bytes hash to the digest Inputs records; today the only violation is the `lexicon` key of `agent-ix/filament-core-service#25`, which is carried as an expected failure. | Test |
| FR-001-AC-2 | Activation against a clean filament-core succeeds with HTTP 200. | Test |
| FR-001-AC-3 | Re-activation is a no-op with the same content hash. | Test |
| FR-001-AC-4 | Each declared archetype, object type and artifact type appears in the corresponding filament-core table after activation, and each exported object type's registered `data_schema` equals the reference object as posted while `agent-ix/filament-core-service#23` is open. | Test |

## Dependencies

- **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035), FR-026, FR-034
- **Upstream (blocking)**: `agent-ix/filament-core-service#25` (the FR-035 schema refuses `lexicon`), `agent-ix/filament-core-service#23` (reference-form `data_schema` is stored verbatim)
- **Downstream**: consumer agents and editors discovering this module's contributions; [FR-003](./FR-003-semantic-manifest-contract.md)
