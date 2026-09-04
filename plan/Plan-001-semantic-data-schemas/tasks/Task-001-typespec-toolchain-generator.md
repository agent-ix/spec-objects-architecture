---
id: Task-001
title: "FR-002 (enablement half) — TypeSpec toolchain, schema generator and drift gate"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-007
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-002
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-013
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-014
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-016
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-017
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-018
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-019
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-073
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-074
    type: verifies
---
# Task-001: FR-002 (enablement half) — TypeSpec toolchain, schema generator and drift gate

## Scope

Stand up the emission pipeline: the pinned toolchain, the generator that runs the
official emitter, and the drift gate `make lint` runs.

## Subtasks

- [x] **Pinned toolchain.** `@typespec/compiler` 1.15.0, `@typespec/json-schema` 1.15.0 and `@agent-ix/semantic-core` 0.1.0 as exact `devDependencies`. No `.npmrc`, no `file:`/`link:`, no upper bound.
- [x] **Lockfile.** `package-lock.json` resolves every public package from `registry.npmjs.org` and `@agent-ix/semantic-core` from npm.ix, produced with `npm install --registry=https://registry.npmjs.org/ --@agent-ix:registry=http://npm.ix/`.
- [x] **Generator.** `scripts/generate-schemas.mjs`: `tsp compile`, keep the module namespace, absolutize relative `$id`/`$ref`, write `schemas/` plus `toolchain.json`, rewrite the manifest digests textually so anchors and comments survive.
- [x] **Drift gate.** `--check` writes nothing and names every differing, stale or mismatched file; `make lint` runs it.
- [x] **Version coupling.** A `@jsonSchema` base whose version differs from the manifest `version` fails naming both.

## Deliverables

- `package.json`, `package-lock.json`, `.gitattributes`
- `typespec/tspconfig.yaml`
- `scripts/generate-schemas.mjs`

## Notes

- FR-002 is split across two tasks because its emitted-set criteria cannot exist
  before FR-004 declares the models. This task owns the mechanism; Task-003 owns
  the emitted set.
- The generator never hand-edits an emitted file: a wrong schema is fixed in
  `typespec/main.tsp` and regenerated.
