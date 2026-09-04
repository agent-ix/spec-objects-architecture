---
id: Task-013
title: "Gate — ApiEndpoint, Queue and ExternalContract end-to-end"
type: Task
status: done
track: Gate
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-006
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/Task-008
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/Task-009
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/Task-010
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/US-001
    type: references
---
# Task-013: Gate — ApiEndpoint, Queue and ExternalContract end-to-end

## Scope

Before the plan is declared done, three types — one operation-shaped, one field-shaped,
one clause-shaped — must survive the whole path.

## Subtasks

- [x] **Validate.** All thirteen skeletons pass `validate_document` with no `semantic.record-invalid`.
- [x] **Extract.** Availability states match each type's declared set; the table and fence forms of the three alternates extract to identical `FieldDecl[]`.
- [x] **Resolve.** Every non-kernel `type.target` resolves under the bundle index with zero unresolved findings.
- [x] **Refuse.** Each of the ten negative fixtures fails with its own `expect:` code and a message carrying detail.
- [x] **Gates green.** `make lint` (ruff, black, schema drift) and `make test` both pass.

## Deliverables

- The passing suite: 163 passed, 7 skipped, 4 expected failures
- `quire validate`: structurally clean; `quire coverage`: 141/141 rows backed

## Notes

- The gate passed on the first attempt for the emitter recipe, and on the second for
  the skeletons: the first run surfaced the `pattern:` spelling and the bare `Decimal`,
  both of which are authoring corrections rather than schema relaxations.
