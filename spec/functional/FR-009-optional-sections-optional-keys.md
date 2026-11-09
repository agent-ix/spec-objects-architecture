---
id: FR-009
title: "Require a declaration key only when its source section is required"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-005"
    type: "depends_on"
---
# FR-009: Require a declaration key only when its source section is required

## Description

An object type's declaration schema SHALL NOT require a record key whose source
section the same module's manifest locator marks optional (`required: false`) or
declares no locator for, so that a document satisfying every mandatory locator is
not refused as `semantic.record-invalid` for a key it was allowed to omit.

## Inputs

- The manifest `body_extraction` locators of the object types, whose
  `operations`, `properties` and `api_contract` sections are `required: false`.
- The declaration record Quire assembles per artifact, which omits a key whose
  section is absent ([FR-004](./FR-004-role-schemas.md) Inputs).

## Outputs

- `ApiEndpoint`, `DataSchema`, `Queue`, `Action`, `UiComponent`,
  `ExternalContract`, `ExtensionPoint`, `BinaryFormat` and `RateLimit` list no
  required key.
- `Interface` still requires `featureOrder`: its `## Features` locator is
  `required: true` and carries the keys.

## Behavior

- A key made optional here keeps every item rule it had: `minItems`, `maxItems`
  and the `contains` markers apply to the key whenever it is present.
- The absence of `operations`, `fields` or `clauses` is a valid declaration, not a
  defect; a record carrying none of them validates.
- Locators stay as they are: no section is made mandatory by this requirement.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-009-CON-1 | A schema SHALL require a key only where that type's manifest locator for the key is `required: true`. | Integrity | Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-009-AC-1 | A record lacking `operations`, `fields` or `clauses` validates against each of `ApiEndpoint.json`, `DataSchema.json`, `Queue.json`, `Action.json`, `UiComponent.json`, `ExternalContract.json`, `ExtensionPoint.json`, `BinaryFormat.json` and `RateLimit.json`. | Test |
| FR-009-AC-2 | A present key is still checked: an empty `fields` or `clauses` array, an `operations` array with no returning operation on `ApiEndpoint`, with no guaranteed operation on `ExternalContract`, or with two operations on `Action` fails. | Test |
| FR-009-AC-3 | No schema requires a key whose manifest locator is `required: false`, and `Interface.json` still requires `featureOrder`. | Test |

## Dependencies

- **Upstream**: [FR-004](./FR-004-role-schemas.md), [FR-005](./FR-005-executable-skeletons.md)
