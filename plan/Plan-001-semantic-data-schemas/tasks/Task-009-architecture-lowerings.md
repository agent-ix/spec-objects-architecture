---
id: Task-009
title: "FR-006 — the three architecture-specific lowerings"
type: Task
status: done
track: B
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-005
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-006
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-080
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-081
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-082
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-083
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-084
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-085
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-086
    type: verifies
---
# Task-009: FR-006 — the three architecture-specific lowerings

## Scope

Fix the mappings this module owns and prove each by an agreement assertion between two
sections of one authored artifact.

## Subtasks

- [x] **`interface.contract_yaml` to `OperationDecl[]`.** The mapping stated key by key; the `## Operations` section is the authority and the YAML fence its derived view, and the two agree on names, params and returns.
- [x] **`data_schema.schema_json` as a `TypeRef` target.** The record registers under `ix://agent-ix/spec-objects-architecture/type/<title>`; the JSON fence and the typed table agree on property names and the required set.
- [x] **`api_endpoint` I/O by `TypeRef`.** Every non-kernel param and return resolves to a shipped `data_schema` title with zero unresolved findings; an unknown token yields exactly one `semantic.unresolved-type` and the `unresolved` placeholder, never a kernel scalar.
- [x] **The 0.2.0 fence locators unchanged**, and each still yields its text at 0.3.0.

## Deliverables

- `spec/functional/FR-006-architecture-lowerings.md`
- `tests/test_architecture_lowerings.py`

## Notes

- No assertion depends on an engine lowering that does not exist; the static row
  walks this module's own AST to prove the only engine entry points reached are
  `extract_semantic` and `extract`. The engine-side mapping is `agent-ix/quoin#335`,
  which today enumerates the business keys only.
