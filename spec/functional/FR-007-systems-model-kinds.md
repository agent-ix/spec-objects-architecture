---
id: FR-007
title: "Declare the systems-model kinds as object types with construct declarations"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-002"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-003"
    type: "depends_on"
  - target: "ix://agent-ix/quire-specification/FR-152"
    type: "depends_on"
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "depends_on"
---
# FR-007: Declare the systems-model kinds as object types with construct declarations

## Description

The module SHALL declare the five QSpec FR-152 systems-model kinds —
`interface`, `part`, `port`, `connection` and `allocation` — each as its own
object type and its own `construct:` declaration (filament-core-service
FR-035 CR-004), with the FR-152 members and no others, so that a systems
model authored in Markdown reaches the IR and the QSL linker through module
data rather than a hard-coded kind list.

## Inputs

- QSpec FR-152 (`ix://agent-ix/quire-specification/FR-152`): the kinds and
  their members.
- QSpec FR-208 in `agent-ix/quire-specification#86`: the meaning ids
  `quire.meaning.systems.<kind>/v1`.
- The FR-035 module-manifest schema at filament-core-service `e33070e`,
  which admits `ObjectTypeEntry.construct`.
- The FCD IR member vocabulary (`owner`, `fields`, `operations`, `clauses`,
  `relationships`) and the rule `min_operations`.

## Outputs

- Object types `part`, `port`, `connection` and `allocation`, and a
  `construct:` on the existing `interface`, in `manifest.yaml`, all exported.
- TypeSpec models `Part`, `Port`, `Connection`, `Allocation` and the closed
  enums `PortDirection` and `ConnectionDirection`, emitted per
  [FR-002](./FR-002-emitted-json-schemas.md).
- Skeletons `skeletons/part.md`, `port.md`, `connection.md` and
  `allocation.md`.
- Edge verbs `owned_by`, `typed_by`, `connects`, `allocates`, `allocated_to`
  and roles `systems-part`, `systems-port`, `systems-interface`.

## Behavior

- Each kind's identity SHALL be its artifact `id`. No member is an identity field, so each construct declares `identity: none`.
- `owner`, a connection's ends and an allocation's elements SHALL be reference members, never part of identity.
- `part` SHALL require `owner`, `declaredType` and `multiplicity`.
- `port` SHALL require `owner` (a `systems-part`), `direction` (`in`, `out`, `inout`), `interfaceType` (a `systems-interface`) and `multiplicity`.
- `connection` SHALL require `sourceEnd` and `targetEnd` (each a `systems-port`) and `direction` (`source-to-target`, `target-to-source`, `bidirectional`).
- `allocation` SHALL require `sourceElement` and `targetElement` (a `systems-part`). The source may be an operation, which no role names, so it carries no reference constraint.
- `interface` SHALL keep its FR-004 schema and declare shape `interface`, `operations` required, `fields` forbidden and the rule `min_operations`.
- Every construct SHALL bind `meaning` to `quire.meaning.systems.<kind>/v1`.
- Every construct `references` entry SHALL name only roles the manifest declares, never `*`.
- Each of `part`, `port`, `connection` and `allocation` SHALL author its members as one row of one table under an H2 named for the kind, extracted by one required `table_row` locator asserting the column header and `min_rows: 1`.
- A systems table's first column SHALL NOT be a quire-rs FR-075 model-table key.
- Every skeleton cell that names a declaration SHALL name it by artifact `id`, and skeleton ids SHALL use underscores (QSpec #86 TC-197).
- The engine SHALL NOT be claimed to lower the systems table into the record: until `agent-ix/quire-rs#446` lands, each systems skeleton fails validation with exactly one `semantic.record-invalid` error, and that failure is pinned.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-007-CON-1 | No systems kind SHALL declare a member beyond QSpec FR-152: each schema's properties, its required set and its construct's required members are the same set. | Scope | Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-007-AC-1 | Each of the five kinds is an exported object type whose `data_schema` names its model file with a matching digest. | Test |
| FR-007-AC-2 | Each systems schema accepts a record carrying exactly its FR-152 members, refuses the record missing any one, refuses `fields`, `operations` and `identityFields`, and refuses `{}`; the direction enums refuse any value outside their three. | Test |
| FR-007-AC-3 | Each of `part`, `port`, `connection` and `allocation` has exactly one body locator: a required `table_row` under its H2 asserting its columns and `min_rows: 1`, whose first column is not an FR-075 table key. | Test |
| FR-007-AC-4 | The manifest's FR-035 violations name no `construct`, every construct binds its FR-208 meaning id, and every `references` entry names a declared member and only declared roles. | Test |
| FR-007-AC-5 | The five edge verbs and three roles are declared, `interface` carries `systems-interface`, and the systems kinds' `allowed_links` use exactly those verbs with declared roles or `*`. | Test |
| FR-007-AC-6 | Each systems skeleton carries its column header, has an underscore id, and `quire.extract` yields one row with one cell per column. | Test |
| FR-007-AC-7 | `validate_document` on each systems skeleton reports exactly one error, `semantic.record-invalid` naming a required FR-152 member, pinned until `agent-ix/quire-rs#446`. | Test |
| FR-007-AC-8 | Renaming a systems skeleton's H2 fails with the required locator missing, and reordering its columns fails with a column mismatch. | Test |

## Dependencies

- **Upstream**: QSpec FR-152, FR-208 (`agent-ix/quire-specification#86`); filament-core-service FR-035 CR-004 at `e33070e`; [FR-002](./FR-002-emitted-json-schemas.md), [FR-003](./FR-003-semantic-manifest-contract.md)
- **Upstream (extraction)**: `agent-ix/quire-rs#446` lowers the systems tables into record keys
- **Downstream**: `agent-ix/filament-core-data#172` adds the member names this requirement uses to the IR core vocabulary
