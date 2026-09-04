---
id: FR-006
title: "Fix the three architecture-specific lowerings the module owns"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-005"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-072"
    type: "depends_on"
---
# FR-006: Fix the three architecture-specific lowerings the module owns

## Description

The module SHALL fix the three lowerings its object types own — the
`interface` `contract_yaml` fence to `OperationDecl[]`, the `data_schema`
`schema_json` fence to a record registered as a `TypeRef` target, and the
`api_endpoint` operation params and returns to `TypeRef`s naming those
records — and SHALL prove each by an agreement test between the kernel section
and the typed section of the same artifact, so that the untyped fences the
0.2.0 manifest yields and the typed record the 0.3.0 manifest yields describe
one declaration rather than two.

## Inputs

- The skeletons of [FR-005](./FR-005-executable-skeletons.md) and the
  `contract_yaml`, `schema_json`, and `message_schema` locator yields the
  0.2.0 manifest already produces.
- The models of [FR-004](./FR-004-role-schemas.md): `Interface`, `DataSchema`,
  `Queue`, `ApiEndpoint`.

## Outputs

- One mapping table per lowering, stated in Behavior, that a reader or a
  future extractor implements.
- Agreement assertions between each kernel fence and its typed counterpart.

## Behavior

- The `interface` `contract_yaml` fence SHALL lower to `OperationDecl[]` by the mapping: `operations[].name` to `OperationDecl.name`; `operations[].inputs[]` to `OperationDecl.params[]` (one `FieldDecl` per input, its `type` a `TypeRef`); `operations[].output` to `OperationDecl.returns`; `operations[].pre[]` and `operations[].post[]` to `OperationDecl.pre[]` and `OperationDecl.post[]` as `ClauseRef`s; `associated_types[]` to the record's `associated_types` key.
- A `contract_yaml` key with no counterpart in `OperationDecl` (`semantics`, `dispatch`, `invariants` prose) SHALL remain documentation of the derived view.
- The lowering SHALL NOT invent a record target for such a key, because that would put an unmodelled key in the record.
- The `interface` skeleton SHALL author `## Operations` as the authority and `## Contract` as the derived view.
- The `interface` skeleton's two sections SHALL declare the same operation names, the same param names per operation, and the same return type token where a return is declared.
- The `data_schema` `schema_json` fence SHALL stay a JSON Schema fence.
- The bundle index SHALL register each `data_schema` record as a `TypeRef` target under `ix://agent-ix/spec-objects-architecture/type/<title>`, so an `entity`, a DTO, an `api_endpoint` operation, or a `queue` message field can name it in a `Type` cell.
- The `data_schema` skeleton's `## Schema` fence and its `## Properties` table SHALL declare the same property names and the same required set, the table being the authority.
- The `queue` skeleton's `## Message Format` fence and its `## Properties` table SHALL declare the same property names, the table being the authority.
- Every `api_endpoint` operation param and return whose type is not a `KernelScalar` SHALL name a `data_schema` skeleton `title`, so that under the bundle index it resolves to `ix://agent-ix/spec-objects-architecture/type/<Title>`.
- A `TypeRef` target this module cannot resolve SHALL surface as the engine's `semantic.unresolved-type` finding.
- The module SHALL NOT drop such a target silently or rewrite it to a kernel scalar.
- The module SHALL NOT implement the `contract_yaml` lowering inside the extraction engine: the engine-side mapping is `agent-ix/quoin#335` and its quire-rs successor. This requirement fixes the mapping and asserts the agreement of the two authored forms; a test that claimed the engine performed the lowering would claim evidence this module does not have.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-006-CON-1 | This requirement SHALL state the lowering as a mapping over existing 0.2.0 locator yields, changing no 0.2.0 locator. | Compatibility | Test |
| FR-006-CON-2 | The test suite SHALL assert agreement between two sections of the same authored artifact, never depending on an engine lowering that does not exist. | Integrity | Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-006-AC-1 | Parsing the `interface` skeleton's `## Contract` YAML fence yields the same operation names as its extracted `OperationDecl[]`, the same param names per operation, the same set of operations that declare a return, and for each of those the same return type token. | Test |
| FR-006-AC-2 | Parsing the `data_schema` skeleton's `## Schema` JSON fence yields the same property names as its extracted `fields[].name`, and the fence's `required` set equals the set of fields whose multiplicity lower bound is 1. | Test |
| FR-006-AC-3 | Parsing the `queue` skeleton's `## Message Format` JSON fence yields the same key set as its extracted `fields[].name`. | Test |
| FR-006-AC-4 | Every non-kernel `type.target` in the extracted `api_endpoint` record resolves under the skeleton bundle index to `ix://agent-ix/spec-objects-architecture/type/<Title>` of a shipped `data_schema` skeleton, with zero `semantic.unresolved-type` findings. | Test |
| FR-006-AC-5 | An `api_endpoint` fixture whose return names a token no skeleton declares produces exactly one `semantic.unresolved-type` finding naming that token, and the target is the `ix://…/unresolved/<Token>` placeholder rather than a kernel scalar. | Test |
| FR-006-AC-6 | The `contract_yaml`, `schema_json`, and `message_schema` locators are byte-identical to their 0.2.0 definitions, and each still yields its fence text at 0.3.0. | Test |

## Dependencies

- **Upstream**: [FR-004](./FR-004-role-schemas.md), [FR-005](./FR-005-executable-skeletons.md); quoin FR-072 (`ix://agent-ix/quoin/FR-072`)
- **Upstream (mapping owner)**: `agent-ix/quoin#335` publishes the engine-side mapping for the keys beyond `Properties`, `Invariants`, and `Operations`
- **Downstream**: `agent-ix/quire-contract-ir#52` reads these mappings as the architecture frontend's fixture contract
