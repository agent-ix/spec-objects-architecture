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
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
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
- The IR member names `agent-ix/filament-core-data#172` defines in the core
  vocabulary: `owner`, `declaredType`, `multiplicity`, `direction`,
  `interfaceType`, `sourceEnd`, `targetEnd`, `flowDirection`,
  `sourceElement`, `targetElement`, `fields`, `operations`, `featureOrder`,
  `supertypes`, `clauses` and `relationships`.
- The `specializes` edge verb as spec-objects-business declares it
  (structural, inverse `generalizes`).

## Outputs

- Object types `part`, `port`, `connection` and `allocation`, and a
  `construct:` on the existing `interface`, in `manifest.yaml`, all exported.
- TypeSpec models `Part`, `Port`, `Connection`, `ConnectionEnd`,
  `Allocation` and the closed enums `PortDirection` and
  `ConnectionDirection`, and the `Interface` feature members, emitted per
  [FR-002](./FR-002-emitted-json-schemas.md).
- Skeletons `skeletons/part.md`, `port.md`, `connection.md` and
  `allocation.md`.
- Edge verbs `owned_by`, `typed_by`, `connects`, `allocates`, `allocated_to`
  and roles `systems-part`, `systems-port`, `systems-interface`; the verb
  `specializes` on `interface`.

## Behavior

- Each kind's identity SHALL be its artifact `id`. No member is an identity field, so each construct declares `identity: none`.
- `owner`, a connection's ends and an allocation's elements SHALL be reference members, never part of identity.
- `part` SHALL require `owner`, `declaredType` and `multiplicity`.
- `port` SHALL require `owner` (a `systems-part`), `direction` (`in`, `out`, `inout`), `interfaceType` (a `systems-interface`) and `multiplicity`.
- `connection` SHALL require `sourceEnd` and `targetEnd` and `flowDirection` (`source-to-target`, `target-to-source`, `bidirectional`).
- A connection end SHALL be a `ConnectionEnd`: `type`, the port it attaches to (a `systems-port`), required, and `multiplicity`, the multiplicity at that end, optional.
- `allocation` SHALL require `sourceElement` and `targetElement` (a `systems-part`).
- The kind of an allocation's source (a part, a port or an operation) SHALL be enforced by the QSL model `quire.model.systems.allocation/v1` and its binder, not by construct `references`.
- `interface` SHALL declare shape `interface` with `fields` optional, `operations` optional and `featureOrder` required, and no minimum-feature rule.
- An interface's features SHALL be its fields and operations, ordered as one sequence across both by `featureOrder`, which lists the interface's own field and operation names.
- An interface SHALL declare its supertypes as `specializes` relationships to other interfaces: the verb is declared exactly as spec-objects-business declares it, `interface` admits `specializes: [interface]`, and the construct declares `supertypes` optional, referencing `systems-interface`.
- Every construct SHALL bind `meaning` to `quire.meaning.systems.<kind>/v1`.
- Every construct `references` entry SHALL name only roles the manifest declares, never `*`.
- Each of `part`, `port`, `connection` and `allocation` SHALL author its members as one row of one table under an H2 named for the kind, extracted by one required `table_row` locator asserting the column header and `min_rows: 1`.
- The `connection` table SHALL carry `Source`, `Source Multiplicity`, `Target`, `Target Multiplicity` and `Direction` columns.
- A systems table's first column SHALL NOT be a quire-rs FR-075 model-table key.
- Every skeleton cell that names a declaration SHALL name it by artifact `id`, or name a member of one as `<artifact id>/<member>`, and skeleton ids SHALL be word ids per [FR-003](./FR-003-semantic-manifest-contract.md) (QSpec #86 TC-197).
- Each systems skeleton SHALL validate with zero errors, its record carrying every FR-152 member of its kind.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-007-CON-1 | No systems kind SHALL declare a member beyond QSpec FR-152: for `part`, `port`, `connection` and `allocation` each schema's properties, its required set and its construct's required members are the same set; `Interface` carries exactly the FR-152 features beside its [FR-004](./FR-004-role-schemas.md) keys. | Scope | Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-007-AC-1 | Each of the five kinds is an exported object type whose `data_schema` names its model file with a matching digest. | Test |
| FR-007-AC-2 | Each of the `part`, `port`, `connection` and `allocation` schemas accepts a record carrying exactly its FR-152 members, refuses the record missing any one, refuses `fields`, `operations` and `identityFields`, and refuses `{}`; a connection end with a multiplicity validates, an end without its port or with an unknown key fails; the direction enums refuse any value outside their three. | Test |
| FR-007-AC-3 | Each of `part`, `port`, `connection` and `allocation` has exactly one body locator: a required `table_row` under its H2 asserting its columns and `min_rows: 1`, whose first column is not an FR-075 table key. | Test |
| FR-007-AC-4 | The manifest's FR-035 violations name no `construct` path, a `*` reference or an unknown member state is refused, every construct binds its FR-208 meaning id, and every `references` entry names a declared member and only declared roles. | Test |
| FR-007-AC-5 | The five edge verbs and three roles are declared, `interface` carries `systems-interface`, and the systems kinds' `allowed_links` use exactly those verbs with declared roles or `*`. | Test |
| FR-007-AC-6 | Each systems skeleton carries its column header, has an underscore id, and `quire.extract` yields one row with one cell per column, each reference cell an artifact id or `<artifact id>/<member>`. | Test |
| FR-007-AC-7 | `validate_document` on each systems skeleton reports zero errors, and its record carries every FR-152 member of its kind. | Test |
| FR-007-AC-8 | Renaming a systems skeleton's H2 fails with the required locator missing, and reordering its columns fails with a column mismatch. | Test |
| FR-007-AC-9 | An interface record with only fields, one with only operations, and one with both validates against `Interface.json` with its `featureOrder`; one without `featureOrder` fails; the construct declares `fields` and `operations` optional, `featureOrder` required, and no rule. | Test |
| FR-007-AC-10 | `specializes` is declared as spec-objects-business declares it; `interface` admits `specializes: [interface]`; the construct declares `supertypes` optional with `references` `[systems-interface]`; an interface document with a `specializes` relationship extracts that edge with no `disallowed-edge-type` warning, while an `owned_by` relationship draws one. | Test |

## Dependencies

- **Upstream**: QSpec FR-152, FR-208 (`agent-ix/quire-specification#86`); filament-core-service FR-035 CR-004 at `e33070e`; [FR-002](./FR-002-emitted-json-schemas.md), [FR-003](./FR-003-semantic-manifest-contract.md)
- **Upstream (extraction)**: `agent-ix/quire-rs#446` lowers the systems tables into record keys
- **Upstream (vocabulary)**: `agent-ix/filament-core-data#172` defines the IR member names this requirement uses
