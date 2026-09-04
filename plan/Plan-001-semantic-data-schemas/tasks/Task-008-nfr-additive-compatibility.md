---
id: Task-008
title: "NFR-001 — additive compatibility and the promotion census"
type: Task
status: done
track: B
priority: P0
relationships:
  - target: ix://agent-ix/spec-objects-architecture/Task-006
    type: depends_on
  - target: ix://agent-ix/spec-objects-architecture/NFR-001
    type: references
  - target: ix://agent-ix/spec-objects-architecture/TC-060
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-061
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-062
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-063
    type: verifies
  - target: ix://agent-ix/spec-objects-architecture/TC-064
    type: verifies
---
# Task-008: NFR-001 — additive compatibility and the promotion census

## Scope

Measure that 0.3.0 costs the artifacts that exist today nothing, and say what the
measurement does and does not cover.

## Subtasks

- [x] **Zero locators changed** against the frozen baseline.
- [x] **Zero error findings** over the ten 0.2.0 skeletons, and the reason asserted: none carries `object:`, so the semantic layer never runs on them.
- [x] **The legacy-form warning population is empty**, and the row asserts the emptiness rather than a count it cannot produce. No 0.2.0 architecture skeleton has a `## Properties` section at all.
- [x] **Every 0.2.0 locator yield byte-identical**, compared against the fixture text rather than against a second engine run.
- [x] **Zero `allowed_links` or `roles` changes.**
- [x] **The promotion census recorded.** 24 wild architecture artifacts in three types, 0 carrying `object:` — stated in NFR-001 Scope as the risk the promotion sweep inherits, with no corpus artifact edited.

## Deliverables

- `tests/test_additive_compatibility.py`
- The NFR-001 Scope, Measurement and Verification sections

## Notes

- The legacy-form metric was inherited from `spec-objects-business` and would have
  been a green row over an empty population; it is corrected rather than carried.
- The `object:`-declaring legacy case is an expected failure on
  `agent-ix/quire-rs#391`, not a relaxed schema.
