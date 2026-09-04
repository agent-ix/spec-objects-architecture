---
id: Task-004
title: "FR-003 — manifest 0.3.0, semantic block and reference-form data_schema"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-003
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-003
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-020
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-021
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-022
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-024
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-025
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-026
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-028
    type: verifies
---
# Task-004: FR-003 — manifest 0.3.0, semantic block and reference-form data_schema

## Scope

Turn `manifest.yaml` into a semantic module — without changing a single 0.2.0 locator
and without touching the `lexicon`.

## Subtasks

- [x] **`semantic` block.** Exactly the nine admitted keys, `exports` naming the ten object types.
- [x] **Reference-form `data_schema`.** `{ schema, digest }` on every exported type; no inline form survives.
- [x] **Version 0.3.0**, bumped with the `@jsonSchema` base in one commit.
- [x] **Locator preservation.** Every 0.2.0 locator keeps its facets, compared structurally against the Task-007 baseline.
- [x] **`lexicon` frozen.** All 113 entries byte-identical, including the eight this repo's issue #7 records as truncated — this change must not be confused with that fix.
- [x] **Loader verification, measured.** All ten archetypes load; an unknown `semantic` key empties the module; a wrong digest drops that type alone. Both refusals are silent, which is the expected failure of `agent-ix/quire-rs#221` and `#394`.

## Deliverables

- `spec_objects_architecture/manifest.yaml`
- `tests/test_manifest_semantic.py`

## Notes

- The digest behaviour is recorded as **measured on this module** rather than as
  quire-rs#394 reports it, because the two observations differ.
- This task is the only writer of the `semantic` block, the version and the
  `data_schema` values. Task-006 is the only writer of the added locators.
