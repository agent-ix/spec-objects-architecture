---
id: Task-010
title: "FR-003-AC-8 / FR-005-CON-3 — the measured consumer boundaries"
type: Task
status: done
track: B
priority: P1
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-004
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/Task-005
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-003
    type: references
  - target: ix://agent-ix/spec-objects-architecture/FR-005
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-090
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-091
    type: verifies
---
# Task-010: FR-003-AC-8 / FR-005-CON-3 — the measured consumer boundaries

## Scope

Turn two prose claims into runs, so each turns red the day its blocking issue is fixed.

## Subtasks

- [x] **The Filament snapshot boundary.** Handed the ten reference-form values verbatim, `extract_filament_core` refuses each with `semantic.data-schema-unresolved-reference` and emits no node; handed the same schemas resolved, it refuses none. `agent-ix/filament-core-service#23` owns the resolution.
- [x] **The bundle index keyed by declaration id.** Ten entries for thirteen files; a per-file index makes `ArtifactRecord` ambiguous with itself, which is the expected failure of `agent-ix/quire-rs#398`.
- [x] **Upstream issues filed** with the house shape: `agent-ix/quire-rs#397`, `#398`, `agent-ix/filament-core-service#25`, `agent-ix/spec-objects-business#6`.

## Deliverables

- `tests/test_consumer_boundaries.py`

## Notes

- `agent-ix/quire-rs#397` was filed as "the keyword is refused" and corrected on the
  same ticket after re-measuring: the slash-delimited form works, and what remains is
  a diagnostic that never names it. The skeletons were reverted to the real pattern.
