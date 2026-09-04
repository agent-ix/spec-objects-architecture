---
id: Task-005
title: "FR-005 — executable skeletons, sysml alternates and negative fixtures"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-004
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-005
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-050
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-051
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-052
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-053
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-054
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-055
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-056
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-057
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-058
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-059
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-065
    type: verifies
---
# Task-005: FR-005 — executable skeletons, sysml alternates and negative fixtures

## Scope

Rewrite the ten skeletons as executable typed fixtures and pin what the schemas refuse.

## Subtasks

- [x] **Typed forms.** `## Properties` tables on the three field-bearing types, `## Operations` subsections on the five operation-bearing types, `## Invariants` `ocl` fences on the four clause-bearing types, and `object:` beside `type:` in every frontmatter.
- [x] **Three `sysml` alternates** declaring the same fields as their table skeletons under the same `id` and `title`.
- [x] **Identifier titles.** One per object type, outside `KernelScalar`, so a `Type` cell can name it.
- [x] **Ten negative fixtures**, each with `expect:` and `because:`, covering the four diagnostic codes.
- [x] **Heading discipline.** No skeleton carries an H2 the manifest does not assert; every `required: true` heading is present.

## Deliverables

- `spec_objects_architecture/skeletons/` (13 files)
- `tests/fixtures/negative/` (10 files), `tests/fixtures/api_endpoint-unresolved-return.md`
- `tests/test_skeletons_semantic.py`

## Notes

- The `pattern:` constraint is authored slash-delimited (`pattern: /^[a-f0-9]{64}$/`),
  which is the form the reader accepts; the unslashed spelling earns a misleading
  diagnostic, which is `agent-ix/quire-rs#397`.
- `Decimal` is authored with a policy (`Decimal(18,9)`), which semantic-core requires.
