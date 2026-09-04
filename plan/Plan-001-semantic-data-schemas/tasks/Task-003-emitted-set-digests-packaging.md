---
id: Task-003
title: "FR-002 (emitted-set half) — the thirty-one schemas, toolchain.json, digests and packaging"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-002
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-002
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-010
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-011
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-012
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-015
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-071
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-072
    type: verifies
---
# Task-003: FR-002 (emitted-set half) — the thirty-one schemas, toolchain.json, digests and packaging

## Scope

Emit, ship and package the schema set, and pin the version-bump procedure.

## Subtasks

- [x] **Emitted set.** Thirty-one files — ten object-type models plus twenty-one support models — each with the 2020-12 `$schema` and an `$id` under the manifest-version base.
- [x] **`toolchain.json`.** Compiler and emitter names and versions, the base, the file list, the normalization record and a digest over the emitted bytes.
- [x] **Digests.** `data_schema.digest` rewritten over the shipped bytes for every exported type.
- [x] **Packaging.** `schemas/*.json` in the wheel and sdist; `scripts/stage-npm.mjs` stages `schemas/` beside `manifest.yaml` at pack time and `postpack --clean` removes the staged copies, so no stray root `manifest.yaml` makes the repo look like a second module.
- [x] **Bump procedure.** Source base and manifest version move in one commit; half a bump is refused.

## Deliverables

- `spec_objects_architecture/schemas/` (31 files + `toolchain.json`)
- `scripts/stage-npm.mjs`
- `tests/test_schema_emission.py`

## Notes

- No test hard-codes the `$id` version segment; each reads it from the manifest
  `version` (FR-002-CON-5).
