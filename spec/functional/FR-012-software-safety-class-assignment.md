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
`software_safety_class`, `software_safety_class_assigned_by` and `software_safety_class_rationale`, required together. A part
declaration shares the open `ObjectFrontmatter` ([FR-002](./FR-002-emitted-json-schemas.md)), which admits keys beyond its own, so no
frontmatter schema change is needed to author them. The module extracts them into three optional record keys of the `part`
declaration with `frontmatter_field` locators in the `part` `yield_pattern` ([FR-008](./FR-008-record-key-sections.md) form, key
optional per [FR-009](./FR-009-optional-sections-optional-keys.md)): `softwareSafetyClass`, `softwareSafetyClassAssignedBy` and
`softwareSafetyClassRationale`. The authored `## Part` table is unchanged. A requirement and a part therefore state the class in
the same fields, so one engine rule can read both (quire-rs [FR-090](ix://agent-ix/quire-rs/FR-090) and [FR-091](ix://agent-ix/quire-rs/FR-091)).

The ordered class vocabulary is declared once, in the ISO module. This module declares `softwareSafetyClass` in `model Part`
(`typespec/main.tsp`) as the same string-literal union in the same order, because the emitted record schema needs a closed value,
and AC-9 pins the two lists identical so a rank read from either cannot diverge. The system's class and each item's class are
separate assignments; a system's class is not the highest of its items' classes and an item's class is not the system's, because
nothing derives one from the other.

### No derivation, no default

The module **SHALL NOT** supply a default class, and no check, skeleton or example in the module fills one in. A part with none of
the three fields is "unassigned" and its record carries none of the three keys. An assigned class without a rationale or without an
assigner is invalid and is not downgraded to unassigned. That the named person is who they say is the concern of the signed git
history of the file, not of this module.

### Declarations this module owns

This module declares, in its manifest `traceability` block (shared with the design relations of
[FR-010 in spec-objects-architecture#44](ix://agent-ix/spec-objects-architecture/FR-010); whichever pull request lands second merges
into the one block and rebases the `spec/functional/index.md` line):

- a `carried_fields` entry `name` and `key` `software_safety_class`, `from: [part]`, which merges with the ISO module's entry of the
  same name ([quire-rs FR-090](ix://agent-ix/quire-rs/FR-090));
- a `field_consistency` entry named `requirement-class-below-allocated-part` with `check: class-below-part`, `from: FR`,
  `field: software_safety_class`, `via: {archetype: allocation, edges: [allocates], direction: incoming}`,
  `edges: [allocated_to]`, `direction: outgoing`, `to: [part]`, `to_field: software_safety_class`,
  `order_from: {archetype: FR, field: software_safety_class}`, `rule: not_below`
  ([quire-rs FR-091](ix://agent-ix/quire-rs/FR-091)); it names the ISO module's archetype `FR`, which is checked when the corpus is
  merged, not at this module's load;
- a `required_fields` entry named `part-needs-class` with `check: unassigned-class`, `from: [part]`, `field: software_safety_class`,
  with the severity key `trace:unassigned-class` set to `off` in the module's `grammar_severity`, so a project that enables it declares
  that classes are required.

These entries land after the engine accepts them (quire-rs FR-090 and FR-091).

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-012-AC-1 | `model Part` in `typespec/main.tsp` declares optional `softwareSafetyClass` (a string-literal union), `softwareSafetyClassAssignedBy` and `softwareSafetyClassRationale` (non-empty strings), and the emitted `Part.json` carries all three, optional, with `softwareSafetyClass` requiring the other two and each requiring `softwareSafetyClass`; none carries a `default`; `make schemas-check` passes. | Test |
| FR-012-AC-2 | The `part` `yield_pattern` declares three optional `frontmatter_field` locators reading `software_safety_class`, `software_safety_class_assigned_by` and `software_safety_class_rationale` into the three record keys. | Test |
| FR-012-AC-3 | A part document with all three frontmatter fields passes validation and its extracted declaration record carries the three keys with the values as written. | Test |
| FR-012-AC-4 | A part document with none of the three passes validation and its extracted record has none of the three keys. | Test |
| FR-012-AC-5 | A part with `software_safety_class` and an empty or absent rationale fails validation naming `softwareSafetyClassRationale`; the part is not treated as unassigned. | Test |
| FR-012-AC-6 | A part with `software_safety_class` and an empty or absent assigner fails validation naming `softwareSafetyClassAssignedBy`. | Test |
| FR-012-AC-7 | A part with an empty `software_safety_class` string, and one with an assigner or rationale and no class, each fail validation naming `softwareSafetyClass`. | Test |
| FR-012-AC-8 | A system part and an item part owned by it, carrying different classes, both validate; no module file computes one from the other. | Test |
| FR-012-AC-9 | The union of `softwareSafetyClass` in `model Part` has the same members in the same order as the `enum` of `software_safety_class` in the installed spec-artifacts-iso frontmatter schemas; a test reads the installed ISO schema and fails when they differ. | Test |
| FR-012-AC-10 | A part with `software_safety_class: class-9` or `Class-1` fails validation against `Part.json` naming `softwareSafetyClass`. | Test |
| FR-012-AC-11 | The `part` skeleton validates, names the three optional fields in its contract comment, and carries none of them. | Test |
| FR-012-AC-12 | The manifest declares the `carried_fields` entry stated above. | Test |
| FR-012-AC-13 | The manifest declares the `field_consistency` entry `requirement-class-below-allocated-part` with `check: class-below-part` and the path stated above; over a fixture corpus with the ISO module loaded, a requirement stating a lower class than the part it reaches through an `allocation` yields `trace:class-below-part`, and a matching or higher requirement yields nothing. | Test |
| FR-012-AC-14 | The manifest declares the `required_fields` entry `part-needs-class` with `check: unassigned-class` and `grammar_severity` key `trace:unassigned-class` set to `off`; with the key enabled an unassigned part yields `trace:unassigned-class`, and by default it yields nothing. | Test |
| FR-012-AC-15 | The module loads on its own without error although its `field_consistency` entry names the ISO module's `FR`. | Test |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-012-CON-1 | The module SHALL NOT name a standard, or quote text from one, in any heading, description, example or fixture. | Design | Inspection |
| FR-012-CON-2 | No file in the module computes, fills in or rewrites a class, assigner or rationale value. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-004](./FR-004-role-schemas.md), [FR-007](./FR-007-systems-model-kinds.md), [FR-009](./FR-009-optional-sections-optional-keys.md), spec-artifacts-iso FR-009 (vocabulary and field), quire-rs FR-090 and FR-091 (engine; AC-12 to AC-14 land after them)
- **Downstream**: [quoin FR-161](ix://agent-ix/quoin/FR-161) (per-class obligations)
