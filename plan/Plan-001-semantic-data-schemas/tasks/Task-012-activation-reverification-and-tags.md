---
id: Task-012
title: "FR-001 / StR-001 — activation re-verification, the generator demonstration and the expected failures"
type: Task
status: done
track: C
priority: P1
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-004
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/FR-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/StR-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-001
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-002
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-003
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-004
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-005
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-006
    type: verifies
---
# Task-012: FR-001 / StR-001 — activation re-verification, the generator demonstration and the expected failures

## Scope

Re-verify the 0.2.0-era activation requirement against the 0.3.0 manifest, and discharge
the stakeholder criteria with evidence that exists.

## Subtasks

- [x] **FR-035 pinned by digest.** The vendored schema's bytes are asserted against `sha256:69cf9738…`, the `a77f31e` revision Quoin and Quire both vendor.
- [x] **The `lexicon` refusal carried honestly.** FR-001-AC-1 is a strict expected failure naming `agent-ix/filament-core-service#25`, beside a passing row asserting that the `lexicon` key is the **only** violation — so nothing this issue added is refused.
- [x] **StR-001-VC-2 by a real generator run.** `minijinja-cli` renders all thirteen skeletons and each rendered artifact validates; the row fails rather than skips when the generator is absent.
- [x] **StR-001-VC-3** by schema alone: an api-endpoint record and a rate-limit record are mutually refused.
- [x] **The activation rows** stay environment-gated on `FILAMENT_CORE_URL` and are declared `🚧`, not green.

## Deliverables

- `spec/functional/FR-001-module-manifest-activates.md`
- `tests/test_activation_and_stakeholder.py`

## Notes

- FR-001's two uncatalogued verification methods (`Schema Test`, `Integration Test`)
  are replaced with the ISO catalog method.
- A test that ran no generator previously carried the VC-2 tag; the tag now sits on a
  test that runs one.
