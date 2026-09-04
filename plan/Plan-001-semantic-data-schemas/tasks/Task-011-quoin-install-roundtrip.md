---
id: Task-011
title: "IT-002 — Quoin install roundtrip with a restore that restores"
type: Task
status: done
track: C
priority: P1
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-004
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-003
    type: references
  - target: ix://agent-ix/spec-objects-architecture/IT-002
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-027
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-070
    type: verifies
---
# Task-011: IT-002 — Quoin install roundtrip with a restore that restores

## Scope

Verify the Quoin boundary and leave the operator's global module store exactly as it
was found.

## Subtasks

- [x] **Record, install, inspect, restore.** The four steps of IT-002, with the restore in a `finally` so a failed install never leaves the store half-written.
- [x] **A restore that restores.** The install source is rebuilt from the recorded listing entry (`path:` / `github:owner/repo//subdir@ref` / `package:name@version`); a bare module name is not a source and never restored anything.
- [x] **State equality on the entry**, not on the whole listing string, so a moving `installedAt` cannot mask a failed restore, and the restore's exit code is asserted.
- [x] **Opt-in.** `QUOIN_INSTALL_ROUNDTRIP=1`, because the row writes a global store.

## Deliverables

- `tests/test_quoin_install_roundtrip.py`

## Notes

- Run against quoin `0.23.1-2-g3e842ce` on 2026-09-04: install exits zero, the derived
  `semantic/package-manifest.json` names `agent-ix/spec-objects-architecture` and ten
  exports, and the prior `git-subdir@v0.6.0` entry is back.
- The same defect in the sibling module's port is `agent-ix/spec-objects-business#6`.
