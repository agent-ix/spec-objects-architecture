---
id: Task-002
title: "FR-004 — the ten role-distinct models and twenty-one support models"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-001
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-004
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-007
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-030
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-031
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-032
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-033
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-034
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-035
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-036
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-037
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-038
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-039
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-040
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-041
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-042
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-043
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-044
    type: verifies
---
# Task-002: FR-004 — the ten role-distinct models and twenty-one support models

## Scope

Declare one model per architecture object type in `typespec/main.tsp`, each refusing the
records its role forbids, with every grammar item a `$ref` to semantic-core 0.1.0.

## Subtasks

- [x] **Ten object-type models.** `ApiEndpoint`, `DataSchema`, `Queue`, `Action`, `UiComponent`, `Interface`, `ExternalContract`, `ExtensionPoint`, `BinaryFormat`, `RateLimit`, each sealed with `...Record<never>`.
- [x] **Item rules through the official decorators.** `@contains(IdentityField)` for the queue partition key, `@contains(IdentityField) @minContains(0) @maxContains(0)` for the identity-free UI props, `@contains(ReturningOperation)` for the endpoint that answers, `@contains(GuaranteedOperation)` for the external contract's postcondition, `@maxItems(1)` for the single-invocation action.
- [x] **Twenty-one support models.** Three open markers, nine architecture value models, nine closed enums.
- [x] **Kernel discipline.** No model redeclares a semantic-core model; `fields`, `params`, `clauses`, `operations`, `relations` and `associated_types` are `$ref`s.
- [x] **`{}` fails all ten.** Every type requires at least one extractable key, so the empty record is refused everywhere.

## Deliverables

- `typespec/main.tsp`
- `tests/test_role_schemas.py`

## Notes

- Quality gate 1 was met on the first emission: the decorator recipe survives the real
  2020-12 validator with `unevaluatedProperties: {not: {}}` in place.
- Every criterion over a key the extractor does not populate is verified against a
  hand-built record and says so in the test; those rows are schema evidence, not
  extraction evidence.
