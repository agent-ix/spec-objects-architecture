---
id: FR-016
title: "A risk-control requirement is asked for the design element that segregates it"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-010"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-012"
    type: "references"
  - target: "ix://agent-ix/quire-rs/FR-058"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/FR-086"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/FR-041"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-161"
    type: "references"
---
# FR-016: A risk-control requirement is asked for the design element that segregates it

## Description

Where a requirement is a risk control, a person decides how the software item that carries it is kept apart from
other items, so that a fault elsewhere cannot defeat the control. Quoin FR-161 has an activity kind `segregation`
that reads a **design relation** by name, one row per requirement. No default module declared one, so a class
policy that asked for it was refused. This requirement declares it in the style of
[FR-010](./FR-010-design-realization-edge.md).

[FR-012](./FR-012-software-safety-class-assignment.md) lets a child part state its own class and rationale, which
records why a part stands apart. It is a statement about a part and has no edge to a requirement, so it cannot give
a requirement a row. This requirement adds the requirement-facing edge and leaves FR-012 unchanged. The tool never
writes the edge, never judges whether the segregation is sufficient, and assigns no score, class or acceptability; a
person decides.

### The edge

- Verb `segregates_for_requirement` (category `traceability`), inverse `requirement_segregated_by`. It is new: no existing
  verb says that a design element keeps a requirement's implementation apart. `realizes_requirement` says the element
  realizes the requirement, a different fact; a requirement can be realized by an element that is not segregated.
- Authored by a `part` or a `connection` toward an `FR` or `NFR`. A `part` states the item it keeps apart; a `connection`
  states the controlled interface across which the segregation holds. An `ADR` records the decision to segregate
  and is a legitimate source, with the dependency below. The requirement may author the inverse toward the element without
  editing it (`agent-ix/quire-rs` FR-041).

### Scope

Only a risk-control requirement is in scope. A requirement is a risk-control requirement when it has an outgoing
`satisfies` edge to a `control` (the edge of `agent-ix/spec-objects-safety` FR-205, authored on the requirement). The scope is
the `when_any` of `agent-ix/quire-rs` FR-058: `when_any: [{verb: satisfies, direction: outgoing, other: [control]}]`.
A requirement that satisfies no control yields no row and no finding. Because `when_any` cannot nest a condition on the
control, a requirement that satisfies a control that is not used as a risk control is also in scope; a person who does not
want that finding maps its key `off` or removes the edge. The relations SHALL NOT be declared without the scope: unscoped they would
report every requirement in the corpus.

### Relations

`from` names one archetype, so the requirements of `FR` and `NFR` are two relations, as in FR-010. Both read the
incoming `segregates_for_requirement` edge from `part`, `connection` or `ADR`. They are named in `design_relations` after the two
realization relations, so quire's design join, `quire matrix --strict` and the quoin design column report them (see
quoin FR-161 and FR-165).

## Inputs

- `FR`, `NFR`, `part`, `connection` and `ADR` documents, and `control` documents the requirements `satisfy`.
- The `spec-artifacts-iso`, `spec-artifacts-process` and `spec-objects-security` kinds, where loaded.

## Outputs

- Edge verb `segregates_for_requirement` with inverse `requirement_segregated_by` in `edge_types`.
- `allowed_links` of `part` and `connection` admitting `segregates_for_requirement: [FR, NFR]`.
- Two `required_relations` entries and their names appended to `traceability.design_relations`.
- Advisory findings `fr-without-segregation` and `nfr-without-segregation`.

## Behavior

- The module SHALL declare `segregates_for_requirement` with `inverse: requirement_segregated_by` in `edge_types`.
- The module SHALL admit `segregates_for_requirement: [FR, NFR]` in the `allowed_links` of `part` and of `connection`.
- The module SHALL declare the relation `fr-has-segregation` with `from: FR`, `edges: [segregates_for_requirement]`, `to: [part, connection, ADR]`, `direction: incoming`, `check: fr-without-segregation` and `when_any: [{verb: satisfies, direction: outgoing, other: [control]}]`.
- The module SHALL declare the relation `nfr-has-segregation` with the same fields and `from: NFR`, `check: nfr-without-segregation`.
- The module SHALL append `fr-has-segregation` and `nfr-has-segregation`, in that order, to `traceability.design_relations` after the two relations of FR-010.
- Quire SHALL report a requirement that satisfies a `control` and has no incoming `segregates_for_requirement` edge from a resolved `part`, `connection` or `ADR`.
- Quire SHALL report nothing for a requirement that satisfies no `control`.
- Quire SHALL report nothing for an in-scope requirement with such an edge, authored by the element or as `requirement_segregated_by` by the requirement.
- Each finding SHALL be a warning, tunable on `trace:fr-without-segregation` and `trace:nfr-without-segregation`.
- The relations SHALL NOT read, set or require a score, class, acceptability or approval value.
- The relations SHALL NOT read the class of the part that carries the edge.
- Where no loaded module declares a kind the relations name (`control`, `ADR`, `FR`, `NFR`) and no document of that kind exists, each relation SHALL report `trace:undeclared-relation-vocabulary` naming it, as in FR-010.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-016-AC-1 | `edge_types` declares `segregates_for_requirement` with `inverse: requirement_segregated_by`, and merging the manifest with spec-artifacts-iso raises no `DuplicateEdgeType`. | Test |
| FR-016-AC-2 | `part` and `connection` admit `segregates_for_requirement` with targets `FR` and `NFR`, and a part or connection authoring it toward an `FR` or `NFR` draws no `disallowed-edge-type` or `disallowed-edge-target` warning; a part authoring it toward a `part` is `disallowed-edge-target`. | Test |
| FR-016-AC-3 | The manifest declares `fr-has-segregation` and `nfr-has-segregation` with the fields and `when_any` stated above, and the last two entries of `design_relations` are those names in that order after the two relations of FR-010. | Test |
| FR-016-AC-4 | Over a fixture where an `FR` satisfies a `control` and no element segregates it, `quire relations --json` reports that `FR` `uncovered` in `fr-has-segregation` and `quire validate --okf` yields one `fr-without-segregation` finding naming it. | Test |
| FR-016-AC-5 | A part authoring `segregates_for_requirement` toward that `FR`, or the `FR` authoring `requirement_segregated_by` toward the part, makes it `covered` with the part linked and removes the finding; the same edge from a `connection` or an `ADR` has the same result, and a pair authored both ways yields one element. | Test |
| FR-016-AC-6 | An `FR` and an `NFR` that satisfy no `control` yield no row and no finding in either relation, and an edge from a document of an archetype outside `to` leaves an in-scope requirement `uncovered`. | Test |
| FR-016-AC-7 | `realizes_requirement` from a part toward an in-scope `FR` leaves it `uncovered` in `fr-has-segregation` and `covered` in `fr-has-design-element`; `segregates_for_requirement` from that part alone has the opposite result, and both edges together leave it `covered` in both. | Test |
| FR-016-AC-8 | `--severity trace:fr-without-segregation=error` promotes the finding and the run exits non-zero; mapping the key `off` drops it. | Test |
| FR-016-AC-9 | A part with and a part without `software_safety_class` both satisfy the relation when they author the edge, and no finding or row reads the class. | Test |
| FR-016-AC-10 | Over the same fixture, `quoin class obligations` with a `segregation` entry naming `relation: fr-has-segregation` reads the `FR` row `unmet` before the edge and `met` after it, and `not-available` for an `FR` that satisfies no control. | Demonstration |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-016-CON-1 | The declaration SHALL add no object type and no engine behavior: it is `edge_types`, `allowed_links` and `traceability` data only. | Scope | Inspection |
| FR-016-CON-2 | The module SHALL NOT write or infer a `segregates_for_requirement` edge. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-007](./FR-007-systems-model-kinds.md), [FR-010](./FR-010-design-realization-edge.md), [FR-012](./FR-012-software-safety-class-assignment.md); `agent-ix/quire-rs` FR-058 (`when_any`), FR-086 (design join), FR-041 (inverse labels); `agent-ix/spec-objects-safety` FR-205 (`satisfies` from a requirement to a control); quoin FR-161.
- **Cross-repository**: the `ADR` archetype is declared by `spec-artifacts-process`, whose `allowed_links` for `ADR` must list `segregates_for_requirement` (targets `FR`, `NFR`) to remove the advisory `disallowed-edge-type` an ADR draws; the relation counts the edge regardless, being verb-based, and authoring the inverse from the requirement avoids the warning. This repository does not edit that one.
- **Downstream**: quoin FR-161, FR-165 and the dossier, which read the new design relations.
