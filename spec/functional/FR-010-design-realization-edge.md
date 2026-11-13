---
id: FR-010
title: "Declare the design-realization edge and the design relations"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-086"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-058"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-041"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-085"
    type: "depends_on"
---
# FR-010: Declare the design-realization edge and the design relations

## Description

A design element answers a requirement only if the spec says so in a form a tool can read. The
module SHALL declare, as manifest data, the edge by which a design element realizes a requirement and
the relations that ask each requirement for such an element, so the quire-rs design-element join
([FR-086](ix://agent-ix/quire-rs/FR-086)) reports, per requirement, the parts, connections and ADRs
that realize it and a gap when there are none. The engine knows no name below; this module owns them.

## Inputs

- quire-rs [FR-058](ix://agent-ix/quire-rs/FR-058) `required_relations`,
  [FR-041](ix://agent-ix/quire-rs/FR-041) inverse labels and FR-086 `design_relations`.
- The `part` and `connection` object types of [FR-007](./FR-007-systems-model-kinds.md).
- The requirement archetypes `FR` and `NFR` and the `ADR` archetype, declared by other modules.

## Outputs

- Edge verb `realizes_requirement` (category `traceability`) in `edge_types`, with
  `inverse: requirement_realized_by`. It is a new verb: the existing `realizes` verb means an
  enterprise capability and is left unchanged.
- `allowed_links` of `part` and `connection` admitting `realizes_requirement: ["*"]`.
- A `traceability` block with two `required_relations` and a `design_relations` list.

## Behavior

- The module SHALL declare `realizes_requirement` with its inverse in `edge_types`, so a design
  element authors `realizes_requirement` toward a requirement, and a requirement may author
  `requirement_realized_by` toward the element without editing it (FR-041).
- The module SHALL declare these relations, each `direction: incoming`, `edges: [realizes_requirement]`
  and `to: [part, connection, ADR]`, with distinct `name` and `check` tokens:
  `fr-has-design-element` (`from: FR`, `check: requirement-without-design`) and
  `nfr-has-design-element` (`from: NFR`, `check: nfr-without-design`).
- The module SHALL list both names, in that order, in `traceability.design_relations`.
- `to` is non-empty, so an edge from a document of another kind is a kind mismatch and a dangling
  edge never satisfies the relation (FR-058, FR-085).
- An edge may target a requirement document with a `#<criterion-id>` fragment to name the acceptance
  criterion realized; the join reports it (FR-086).
- The relations ship advisory like every FR-058 relation; this module sets no severity.
- The `ADR` archetype is declared by `spec-artifacts-process`, which does not list the verb in its
  `allowed_links`; an ADR authoring the verb draws the advisory `disallowed-edge-type` until that
  module lists it, and the relation counts the edge regardless, being verb-based. Authoring the
  inverse from the requirement avoids the warning (FR-041-AC-2).

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-010-AC-1 | `edge_types` declares `realizes_requirement` with `inverse: requirement_realized_by`, and `realizes` is unchanged. | Test |
| FR-010-AC-2 | `part` and `connection` admit `realizes_requirement`, and a part document authoring it toward an `FR` draws no `disallowed-edge-type` warning. | Test |
| FR-010-AC-3 | The manifest declares exactly the relations `fr-has-design-element` and `nfr-has-design-element` with the fields stated above, and `design_relations` lists them in that order; the module loads under quire-rs without error. | Test |
| FR-010-AC-4 | Over a fixture corpus, `quire relations --design --json` reports an `FR` with a realizing part as `covered` with that part's id and archetype `part`, and an `FR` with none as `uncovered`. | Test |
| FR-010-AC-5 | A requirement that authors `requirement_realized_by` toward a connection is `covered` with that connection in the same run, and a pair authored both ways yields one element. | Test |
| FR-010-AC-6 | An `NFR` realized by an `ADR` is `covered` with the ADR's id and archetype; the same edge from a document of an archetype outside `to` is a kind mismatch and the `NFR` is `uncovered`. | Test |
| FR-010-AC-7 | With the architecture repository and the requirements repository loaded as two members through `--repo`, an `FR` in one is `covered` by a part in the other; without the part's repository loaded the `FR` is `uncovered` and the reference is dangling as authored. | Test |
| FR-010-AC-8 | The `trace:requirement-without-design` and `trace:nfr-without-design` findings are advisory: a corpus whose only faults are those findings stays valid, and mapping a key `off` drops it. | Test |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-010-CON-1 | The declaration SHALL add no object type and no engine behavior: it is `edge_types`, `allowed_links` and `traceability` data only. | Scope | Inspection |

## Dependencies

- **Upstream**: quire-rs [FR-086](ix://agent-ix/quire-rs/FR-086), [FR-058](ix://agent-ix/quire-rs/FR-058), [FR-041](ix://agent-ix/quire-rs/FR-041), [FR-085](ix://agent-ix/quire-rs/FR-085); quire-cli [FR-041](ix://agent-ix/quire-cli/FR-041); [FR-007](./FR-007-systems-model-kinds.md)
- **Downstream**: the matrix design column (PLAT-1529)
