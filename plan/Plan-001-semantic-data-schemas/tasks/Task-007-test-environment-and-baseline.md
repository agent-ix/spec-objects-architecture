---
id: Task-007
title: "FR-005 — Quire provisioning, the no-vacuous-skip gate and the 0.2.0 baseline"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/FR-005
    type: references
  - target: ix://agent-ix/spec-objects-architecture/NFR-001
    type: references
---
# Task-007: FR-005 — Quire provisioning, the no-vacuous-skip gate and the 0.2.0 baseline

## Scope

Make the engine a hard dependency of the semantic rows, and freeze the 0.2.0 tree the
additivity claim is measured against, before any of it moves.

## Subtasks

- [x] **`make dev-quire`.** A documented target that installs the Quire wheel exposing `extract_semantic` from the dev-only `pypi.ix`. `quire` is deliberately not a committed dependency: `internal-pypi` serves 0.33.0 at most and no `quire-rs` tag carries the semantic layer (`agent-ix/quire-rs#392`).
- [x] **Fail, never skip.** `tests/conftest.py::require_quire` calls `pytest.fail` naming the missing function, the target and the blocking issue. No `skipif` guards a semantic row.
- [x] **The 0.2.0 baseline.** `tests/fixtures/baseline-0.2.0/` captured from `origin/main`: the ten skeletons verbatim, plus `body_extraction.json`, `edge_vocabulary.json` and `lexicon.json` extracted from the 0.2.0 manifest.
- [x] **Schema registry.** A 2020-12 validator factory resolving every `$ref` locally — module models from the committed tree, grammar models from the installed `@agent-ix/semantic-core`.

## Deliverables

- `Makefile` / `pyproject.toml`: `dev-quire`, `schemas`, `schemas-check`
- `tests/conftest.py`
- `tests/fixtures/baseline-0.2.0/`

## Notes

- The baseline is captured **before** the manifest moves, so NFR-001 compares against
  what was actually shipped rather than against a reconstruction.
- Unblocks: every other task.
