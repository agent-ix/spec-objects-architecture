---
id: FR-012
title: "A part carries an optional human-assigned software safety class with assigner and rationale as frontmatter"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-009"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-010"
    type: "depends_on"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-009"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/FR-090"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/FR-091"
    type: "depends_on"
---
# FR-012: A part carries an optional human-assigned software safety class with assigner and rationale as frontmatter

Tracked by Linear PLAT-1526 (implemented by PLAT-1577 and PLAT-1578).

## Description

A software system and each software item inside it is declared as a `part` ([FR-007](./FR-007-systems-model-kinds.md)). The
module **SHALL** let a person record, on that part, the software safety class they assign to it, who assigned it, and why. The
class is a separate axis from requirement criticality
([spec-artifacts-iso FR-008](ix://agent-ix/spec-artifacts-iso/FR-008)).

### One mechanism: frontmatter

The class is stated the way the ISO module states it on a requirement
([spec-artifacts-iso FR-009](ix://agent-ix/spec-artifacts-iso/FR-009)): three optional frontmatter fields,
`software_safety_class`, `software_safety_class_assigned_by` and `software_safety_class_rationale`, required together. The module
**SHALL** declare the three on a part frontmatter schema, `PartFrontmatter` (extending the open `ObjectFrontmatter` of
[FR-002](./FR-002-emitted-json-schemas.md), referenced by the `part` object type), as plain non-empty strings with **no value list**,
so that an all-unassigned corpus draws no undeclared-vocabulary finding for them. The module extracts them into three optional record
keys of the `part` declaration with `frontmatter_field` locators in the `part` `yield_pattern` ([FR-008](./FR-008-record-key-sections.md)
form, key optional per [FR-009](./FR-009-optional-sections-optional-keys.md)): `softwareSafetyClass`, `softwareSafetyClassAssignedBy`
and `softwareSafetyClassRationale`, declared in `model Part` (`typespec/main.tsp`) as plain strings: type only, no value list. The
authored `## Part` table is unchanged.

The ordered class vocabulary is declared once, in the ISO module, and this module holds no copy and no parity test of it. A part's value
is held to that vocabulary by the engine: the manifest declares a `vocabulary` entry
([quire-rs FR-091](ix://agent-ix/quire-rs/FR-091)) that applies to every part document that states the field, and an out-of-vocabulary
value is reported against the `carried_vocabulary` the engine exposes from the ISO module's `enum`
([quire-rs FR-090](ix://agent-ix/quire-rs/FR-090)). The system's class and each item's class are separate assignments; a system's
class is not the highest of its items' classes and an item's class is not the system's, because nothing derives one from the other.
The part-level class is used by the `field_consistency` check below and by nothing else: no per-item report reads it.

### No derivation, no default

The module **SHALL NOT** supply a default class, and no check, skeleton or example in the module fills one in. A part with none of
the three fields is "unassigned" and its record carries none of the three keys. An assigned class without a rationale or without an
assigner is invalid and is not downgraded to unassigned. That the named person is who they say is the concern of the signed git
history of the file, not of this module.

### Declarations this module owns

This module declares, in its manifest `traceability` block (the block that
[FR-010](./FR-010-design-realization-edge.md) introduces for the design relations; these entries are added to it):

- a `field_consistency` entry named `requirement-class-below-allocated-part` with `check: class-below-part`, `from: FR`,
  `field: software_safety_class`, `via: {archetype: allocation, edges: [allocates], direction: incoming}`,
  `edges: [allocated_to]`, `direction: outgoing`, `to: [part]`, `to_field: software_safety_class`,
  `order_from: {archetype: FR, field: software_safety_class}`, `rule: not_below`
  ([quire-rs FR-091](ix://agent-ix/quire-rs/FR-091)); it names the ISO module's archetype `FR`, which is checked when the corpus is
  merged, not at this module's load;
- a `vocabulary` entry named `part-class-in-vocabulary` with `check: undeclared-class-value`, `from: [part]`,
  `field: software_safety_class`, `carried: software_safety_class` (the name the ISO module's `carried_fields` entry declares);
- a `required_fields` entry named `part-needs-class` with `check: unassigned-class`, `from: [part]`, `field: software_safety_class`,
  with the severity key `trace:unassigned-class` set to `off` in the module's `grammar_severity`, so a project that enables it declares
  that classes are required.

These entries land after the engine accepts them (quire-rs FR-090 and FR-091).

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-012-AC-1 | `model Part` in `typespec/main.tsp` declares optional `softwareSafetyClass`, `softwareSafetyClassAssignedBy` and `softwareSafetyClassRationale` as plain strings of `minLength` 1 with no value list, and the emitted `Part.json` carries all three, optional, with `softwareSafetyClass` requiring the other two and each requiring `softwareSafetyClass`; none carries a `default` or an `enum`; `make schemas-check` passes. | Test |
| FR-012-AC-2 | The `part` `yield_pattern` declares three optional `frontmatter_field` locators reading `software_safety_class`, `software_safety_class_assigned_by` and `software_safety_class_rationale` into the three record keys. | Test |
| FR-012-AC-3 | A part document with all three frontmatter fields passes validation and its extracted declaration record carries the three keys with the values as written. | Test |
| FR-012-AC-4 | A part document with none of the three passes validation and its extracted record has none of the three keys. | Test |
| FR-012-AC-5 | A part with `software_safety_class` and an empty or absent rationale fails validation naming `softwareSafetyClassRationale`; the part is not treated as unassigned. | Test |
| FR-012-AC-6 | A part with `software_safety_class` and an empty or absent assigner fails validation naming `softwareSafetyClassAssignedBy`. | Test |
| FR-012-AC-7 | A part with an empty `software_safety_class` string, and one with an assigner or rationale and no class, each fail validation naming `softwareSafetyClass`. | Test |
| FR-012-AC-8 | A system part and an item part owned by it, carrying different classes, both validate; no module file computes one from the other. | Test |
| FR-012-AC-9 | The manifest declares the `vocabulary` entry `part-class-in-vocabulary` with `check: undeclared-class-value` stated above, and no file of the module lists a class value. | Test |
| FR-012-AC-10 | With the ISO module loaded, a part stating `software_safety_class: class-9` or `Class-1` yields one `trace:undeclared-class-value` finding (the quire-rs FR-091 `vocabulary` rule) naming the part, the field and the value, whether or not the part is allocated to any requirement; a part stating a value in the carried vocabulary yields none. | Test |
| FR-012-AC-11 | The `part` skeleton validates, names the three optional fields in its contract comment, and carries none of them. | Test |
| FR-012-AC-12 | The `part` object type references a `PartFrontmatter` schema that declares the three properties as plain strings; over a corpus in which every part is unassigned and the ISO module is loaded, the merged corpus yields no `trace:undeclared-relation-vocabulary` finding for `requirement-class-below-allocated-part`, `part-class-in-vocabulary` or `part-needs-class`. | Test |
| FR-012-AC-13 | The manifest declares the `field_consistency` entry `requirement-class-below-allocated-part` with `check: class-below-part` and the path stated above; over a fixture corpus with the ISO module loaded, a requirement stating a lower class than the part it reaches through an `allocation` yields `trace:class-below-part`, and a matching or higher requirement yields nothing. | Test |
| FR-012-AC-14 | The manifest declares the `required_fields` entry `part-needs-class` with `check: unassigned-class` and `grammar_severity` key `trace:unassigned-class` set to `off`; with the key enabled an unassigned part yields `trace:unassigned-class`, and by default it yields nothing. | Test |
| FR-012-AC-15 | The module loads on its own without error although its `field_consistency` and `vocabulary` entries name the ISO module's `FR` and carried name. | Test |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-012-CON-1 | The module SHALL NOT name a standard, or quote text from one, in any heading, description, example or fixture. | Design | Inspection |
| FR-012-CON-2 | No file in the module computes, fills in or rewrites a class, assigner or rationale value. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-004](./FR-004-role-schemas.md), [FR-007](./FR-007-systems-model-kinds.md), [FR-009](./FR-009-optional-sections-optional-keys.md), [FR-010](./FR-010-design-realization-edge.md) (the `traceability` block), spec-artifacts-iso FR-009 (vocabulary and field), quire-rs FR-090 and FR-091 (engine; AC-9, AC-10 and AC-13 to AC-15 land after them)
- **Downstream**: none
