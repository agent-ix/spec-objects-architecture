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
filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) and
activates idempotently against
`POST /api/v1/modules/activate`.

## Inputs

- `manifest.yaml` (this repo's package).
- Activation endpoint: `POST /api/v1/modules/activate`.

## Outputs

- A module row in the service's `modules` table.
- The contributed archetypes, object types, grammars and artifact types the
  manifest declares.

## Behavior

- Re-activation **SHALL** produce no change, being idempotent by content hash
  (filament-core-service FR-026-AC-1).

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-2 | Activation against a clean filament-core succeeds with HTTP 200. | Test |
| FR-001-AC-3 | Re-activation is a no-op with the same content hash. | Test |
| FR-001-AC-4 | Each declared archetype, object type and artifact type appears in the corresponding filament-core table after activation, and each exported object type's registered `data_schema` equals the reference object as posted while `agent-ix/filament-core-service#23` is open. | Test |

## Dependencies

- **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035), FR-026, FR-034
- **Upstream (blocking)**: `agent-ix/filament-core-service#25` (the FR-035 schema refuses `lexicon`), `agent-ix/filament-core-service#23` (reference-form `data_schema` is stored verbatim)
- **Downstream**: consumer agents and editors discovering this module's contributions; [FR-003](./FR-003-semantic-manifest-contract.md)
