---
id: Task-006
title: "FR-003-CON-2 — required:false locators for the sections the skeletons introduced"
type: Task
status: done
track: A
priority: P1
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-005
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-003
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-005
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-023
    type: verifies
---
# Task-006: FR-003-CON-2 — required:false locators for the sections the skeletons introduced

## Scope

Assert the new sections in the manifest without making them mandatory for artifacts
that predate them.

## Subtasks

- [x] **One `section_body` locator per introduced section**: `operations` on the five operation-bearing types, `properties` on the three field-bearing types, `invariants` on the four clause-bearing types.
- [x] **Every one `required: false`**, so a 0.2.0 artifact that lacks the section stays valid.

## Deliverables

- The added locators in `spec_objects_architecture/manifest.yaml`

## Notes

- Ordered after Task-005 on purpose: a locator can only assert a section that
  exists, and asserting one that does not would make every existing artifact fail.
