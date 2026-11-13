---
id: FR-012
title: "A part carries an optional human-assigned software safety class with assigner and rationale"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-008"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-009"
    type: "depends_on"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-009"
    type: "references"
---
# FR-012: A part carries an optional human-assigned software safety class with assigner and rationale

Tracked by Linear PLAT-1526 (implemented by PLAT-1577 and PLAT-1578).

## Description

A software system and each software item inside it is declared as a `part`
([FR-007](./FR-007-systems-model-kinds.md)). The module SHALL let a person record, on that part, the
software safety class they assign to it, who assigned it, and why. The class is a separate axis from
requirement criticality ([spec-artifacts-iso FR-008](ix://agent-ix/spec-artifacts-iso/FR-008));
its ordered vocabulary is module data owned by
[spec-artifacts-iso FR-009](ix://agent-ix/spec-artifacts-iso/FR-009), and this module names no class
value and holds no copy of the list.

### Authored form

The assignment is the optional record key `safetyClass`, authored as the optional heading `## Safety Class`
holding a one-row table with columns `Class | Assigned By | Rationale`
([FR-008](./FR-008-record-key-sections.md) form). `Class` is one value of the iso vocabulary,
`Assigned By` is the name of the person who made the assignment, and `Rationale` is that person's reason in prose.
The system's class and each item's class are separate assignments; a system's class is not the highest of its
items' classes and an item's class is not the system's, because nothing derives one from the other.

### No derivation, no default

The module SHALL NOT supply a default class, and no check, skeleton or example in the module fills one in. An absent
section is the real state "unassigned" and the extracted record carries no `safetyClass` key
([FR-009](./FR-009-optional-sections-optional-keys.md)). An assigned class without a rationale or without an
assigner is invalid, not downgraded to unassigned. That the named person is who they say is the concern of the
signed git history of the file, not of this module.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-012-AC-1 | `Part.json` declares an optional `safetyClass` object with required `class`, `assignedBy` and `rationale`, each a string of `minLength` 1, sealed against other keys; `safetyClass` is in no `required` list and carries no `default`. | Test |
| FR-012-AC-2 | The `part` manifest declares an optional `## Safety Class` section locator whose single-table assert has columns `Class`, `Assigned By`, `Rationale` and exactly one data row. | Test |
| FR-012-AC-3 | A part document with a complete `## Safety Class` row passes `quire validate` and its extracted declaration record carries `safetyClass` with the three cells as written. | Test |
| FR-012-AC-4 | A part document with no `## Safety Class` section passes `quire validate` and its extracted record has no `safetyClass` key. | Test |
| FR-012-AC-5 | A `## Safety Class` row with an empty `Rationale` cell fails validation naming `rationale`; the part is not treated as unassigned. | Test |
| FR-012-AC-6 | A `## Safety Class` row with an empty `Assigned By` cell fails validation naming `assignedBy`. | Test |
| FR-012-AC-7 | A `## Safety Class` section with two data rows, or with a header other than `Class \| Assigned By \| Rationale`, fails validation. | Test |
| FR-012-AC-8 | A system part and an item part owned by it, carrying different classes, both validate; no module file computes one from the other. | Test |
| FR-012-AC-9 | `Part.json` declares no enumeration for `class` and the module contains no class value list; the allowed values are read from the iso vocabulary ([spec-artifacts-iso FR-009](ix://agent-ix/spec-artifacts-iso/FR-009)) by [quire-rs FR-091](ix://agent-ix/quire-rs/spec/functional/FR-091). | Inspection |
| FR-012-AC-10 | The `part` skeleton validates, names the optional `## Safety Class` section in its contract comment, and carries no `## Safety Class` row. | Test |
| FR-012-AC-11 | The record emitted for a part with a `## Safety Class` row reaches `quire trace` output with `safetyClass.class` as written. | Test |
| FR-012-AC-12 | The manifest declares a `traceability.field_consistency` entry with `rule: not_below` comparing a requirement's `software_safety_class` to the `safetyClass.class` of the part reached over its allocation edge, and a `traceability.required_fields` entry on `part` for `safetyClass.class` whose severity defaults to `off`; fixture corpora with a lower-stating requirement, an unassigned part and a consistent pair produce the findings and the silence [quire-rs FR-091](ix://agent-ix/quire-rs/spec/functional/FR-091) states. | Test |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-012-CON-1 | The module SHALL NOT name a standard, or quote text from one, in any heading, description, example or fixture. | Design | Inspection |
| FR-012-CON-2 | No file in the module computes, fills in or rewrites a `safetyClass` value. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-004](./FR-004-role-schemas.md), [FR-007](./FR-007-systems-model-kinds.md), [FR-008](./FR-008-record-key-sections.md), [FR-009](./FR-009-optional-sections-optional-keys.md), spec-artifacts-iso FR-009 (vocabulary)
- **Downstream**: [quire-rs FR-091](ix://agent-ix/quire-rs/spec/functional/FR-091) (inconsistency findings), [quoin FR-161](ix://agent-ix/quoin/FR-161) (per-class obligations)
