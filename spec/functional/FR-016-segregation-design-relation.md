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
  states the controlled interface across which the segregation holds. An `ADR` records the decision about segregation for the requirement and is a legitimate source; `spec-artifacts-process` lists the
  verb for `ADR` as the dependency below states. The requirement may author the inverse toward the element without
  editing it (`agent-ix/quire-rs` FR-041).

### Scope

The scope is the `when_any` of `agent-ix/quire-rs` FR-058, with two conditions, of which any one puts a requirement in scope. A
requirement is in scope when it has an outgoing `satisfies` edge to a `control` (the edge of `agent-ix/spec-objects-safety` FR-205,
authored on the requirement) or an incoming `satisfied_by` edge from a `control` (its inverse, authored by the control). The engine
matches a verb as authored, so both are named:
`when_any: [{verb: satisfies, direction: outgoing, other: [control]}, {verb: satisfied_by, direction: incoming, other: [control]}]`.
A requirement that no control is linked to yields no row and no finding.

**Accepted limitation.** `when_any` is an OR over the existence of an edge to or from a document of a kind (`agent-ix/quire-rs` FR-058).
It has no conjunction, no condition on a field of the other end and no condition on a field of the requirement that names a risk
control, so it cannot say that the control is used as a risk control. A requirement linked to a control that is not a risk control is
therefore also in scope. The remedy that keeps the trace is to state the segregation decision, including a decision that none is
needed, in an `ADR` that authors `segregates_for_requirement` toward the requirement, so the row is `covered` and the rationale is
recorded; mapping `trace:fr-without-segregation` or `trace:nfr-without-segregation` `off` hides every finding of the relation and
is the last resort. An exact scope needs either a risk-control marker that the module owning `control` authors, so a condition can
name it, or a field condition in `when_any` (`agent-ix/quire-rs` FR-058). Both are owner decisions of other repositories and this
requirement does not make them.

### Effect on the other readers of `design_relations`

The two relations are named in `design_relations` because quoin FR-161 reads a `segregation` entry from the design join, and the join
carries only relations named there. Naming them changes what every reader of the join sees:

- `quire matrix --strict` (`agent-ix/quire-cli` FR-043) exits non-zero on a live requirement with an `uncovered` block, and the block is
  one per relation. A requirement in scope of a segregation relation with no segregating element is therefore a design gap there
  and in the quoin matrix design column (quoin FR-165), shown with the check token of the relation. A requirement outside the scope
  has no block of it. A requirement that has a realizing element but no segregating element still shows the segregation gap, named
  by its own check token and not by the realization one.
- A quoin class policy entry `design-trace` with no `relation`, and a `detailed-design` entry with no `relation`, read the new
  relations as any other design relation (quoin FR-161). A policy pins `design-trace` to one relation by naming it.
- The dossier readers (quoin FR-193, FR-194) read the join verbatim.

These readers' own behaviour is theirs; the module's part is the declaration and the scope above, and nothing else.

### Relations

`from` names one archetype, so the requirements of `FR` and `NFR` are two relations, as in FR-010. Both read the
incoming `segregates_for_requirement` edge from `part`, `connection` or `ADR`. They are named in `design_relations` after the two
realization relations, so quire's design join, `quire matrix --strict` and the quoin design column report them, as the section above states.

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
- The module SHALL declare the relation `fr-has-segregation` with `from: FR`, `edges: [segregates_for_requirement]`, `to: [part, connection, ADR]`, `direction: incoming`, `check: fr-without-segregation` and `when_any: [{verb: satisfies, direction: outgoing, other: [control]}, {verb: satisfied_by, direction: incoming, other: [control]}]`.
- The module SHALL declare the relation `nfr-has-segregation` with the same fields and `from: NFR`, `check: nfr-without-segregation`.
- The module SHALL append `fr-has-segregation` and `nfr-has-segregation`, in that order, to `traceability.design_relations` after the two relations of FR-010.
- Each relation SHALL report an in-scope requirement that has no incoming `segregates_for_requirement` edge from a resolved `part`, `connection` or `ADR`.
- Each relation SHALL report nothing for a requirement that no `control` is linked to by `satisfies` or `satisfied_by`.
- Each relation SHALL report nothing for an in-scope requirement with such an edge, authored by the element or as `requirement_segregated_by` by the requirement.
- The manifest SHALL declare each relation of this requirement with the `when_any` above and no relation without it.
- The manifest SHALL NOT make a design relation of this requirement depend on the class of any part.
- Each finding SHALL be a warning, tunable on `trace:fr-without-segregation` and `trace:nfr-without-segregation`.
- The relations SHALL NOT read, set or require a score, class, acceptability or approval value.
- Where no loaded module declares a kind the relations name (`control`, `ADR`, `FR`, `NFR`) and no document of that kind exists, each relation SHALL report `trace:undeclared-relation-vocabulary` naming it, as in FR-010.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-016-AC-1 | `edge_types` declares `segregates_for_requirement` with `inverse: requirement_segregated_by`, and merging the manifest with spec-artifacts-iso raises no `DuplicateEdgeType`. | Test |
| FR-016-AC-2 | `part` and `connection` admit `segregates_for_requirement` with targets `FR` and `NFR`, and a part or connection authoring it toward an `FR` or `NFR` draws no `disallowed-edge-type` or `disallowed-edge-target` warning; a part authoring it toward a `part` is `disallowed-edge-target`. | Test |
| FR-016-AC-3 | The manifest declares `fr-has-segregation` and `nfr-has-segregation` with the fields and the two-condition `when_any` stated above, and the entries of `design_relations` after the two relations of FR-010 include those names in that order; the test is a prefix and membership check, not an exact list. | Test |
| FR-016-AC-4 | Over a fixture where an `FR` authors `satisfies` toward a `control` and no element segregates it, `quire relations --json` reports that `FR` `uncovered` in `fr-has-segregation` and `quire validate --okf` yields one `fr-without-segregation` finding naming it. | Test |
| FR-016-AC-5 | A part authoring `segregates_for_requirement` toward that `FR`, or the `FR` authoring `requirement_segregated_by` toward the part, makes it `covered` with the part linked and removes the finding; the same edge from a `connection` or an `ADR` has the same result, and a pair authored both ways yields one element. | Test |
| FR-016-AC-6 | An `FR` and an `NFR` that no `control` is linked to yield no row and no finding in either relation, and an edge from a document of an archetype outside `to` leaves an in-scope requirement `uncovered`. | Test |
| FR-016-AC-7 | `realizes_requirement` from a part toward an in-scope `FR` leaves it `uncovered` in `fr-has-segregation` and `covered` in `fr-has-design-element`; `segregates_for_requirement` from that part alone has the opposite result, and both edges together leave it `covered` in both. | Test |
| FR-016-AC-8 | `--severity trace:fr-without-segregation=error` promotes the finding and the run exits non-zero; mapping the key `off` drops it. | Test |
| FR-016-AC-9 | A part with and a part without `software_safety_class` both satisfy the relation when they author the edge, and no finding or row reads the class. | Test |
| FR-016-AC-10 | Over the same fixture with the `FR` carrying a `software_safety_class`, its assigner and its rationale, `quoin class obligations` with a `segregation` entry naming `relation: fr-has-segregation` reads the row `unmet` before the edge and `met` after it, and `not-available` for an `FR` no control is linked to; an `FR` without the class is listed as unassigned with no rows (quoin FR-161). | Demonstration |
| FR-016-AC-11 | A `control` authoring `satisfied_by` toward an `FR` puts that `FR` in scope: it is `uncovered` and yields one `fr-without-segregation` finding until an element segregates it, and a `control` authoring `satisfied_by` toward an `NFR` does the same for `nfr-has-segregation`. | Test |
| FR-016-AC-12 | An `ADR` authoring `segregates_for_requirement` toward an in-scope `FR` makes it `covered` with the `ADR` linked and draws no `disallowed-edge-type` where the `spec-artifacts-process` module lists the verb. | Test |
| FR-016-AC-13 | An `FR` that carries a realizing part but no segregating element is `covered` in `fr-has-design-element` and `uncovered` in `fr-has-segregation`, and `quire matrix --strict` names the check token `fr-without-segregation` for the gap and not `requirement-without-design`. | Test |
| FR-016-AC-14 | Loading the module with spec-objects-security off and no document of kind `control` yields `trace:undeclared-relation-vocabulary` naming `control` for each relation of this requirement, advisory; with the security module loaded, or a `control` document present, it yields none for that kind. | Test |

### Code-step consequence for existing tests

`tests/test_design_edges.py` (TC-142) pins the complete `required_relations` list and `design_relations` equal to the realization pair.
With this requirement and FR-010 it becomes a prefix check on `design_relations` and a membership check on `required_relations`; the
change is made in the code step, not in this specification step.

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-016-CON-1 | The declaration SHALL add no object type and no engine behavior: it is `edge_types`, `allowed_links` and `traceability` data only. | Scope | Inspection |
| FR-016-CON-2 | The module SHALL NOT write or infer a `segregates_for_requirement` edge. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-007](./FR-007-systems-model-kinds.md), [FR-010](./FR-010-design-realization-edge.md), [FR-012](./FR-012-software-safety-class-assignment.md); `agent-ix/quire-rs` FR-058 (`when_any`), FR-086 (design join), FR-041 (inverse labels); `agent-ix/spec-objects-safety` FR-205 (`satisfies` from a requirement to a control); quoin FR-161.
- **Cross-repository**: the `ADR` archetype is declared by `spec-artifacts-process`, whose `allowed_links` for `ADR` must list `segregates_for_requirement` (targets `FR`, `NFR`) to remove the advisory `disallowed-edge-type` an ADR draws; the relation counts the edge regardless, being verb-based, and authoring the inverse from the requirement avoids the warning. This repository does not edit that one.
- **Downstream**: quoin FR-161, FR-165 and the dossier, which read the new design relations.
