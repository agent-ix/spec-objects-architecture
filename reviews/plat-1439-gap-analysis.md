---
id: SR-027
title: "Gap analysis - PLAT-1439 connection carries data_classification (PR #49)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md, spec/functional/FR-007-systems-model-kinds.md, spec_objects_architecture/manifest.yaml, tests/test_systems_kinds.py"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
  - {target: "ix://agent-ix/spec-objects-architecture/FR-007", type: references}
---
# SR-027: Gap analysis - PLAT-1439 (PR #49)

## Summary

Ticket: PLAT-1439. Planless gap analysis. Plan completion: not assessed. Ran
`quoin matrix --json` (quoin 0.34.0) on the PR head and read the manifest and
the tests bound to the changed criteria.

- FR-013-AC-1 to AC-8: all `untagged`, with no binder. That is expected for a
  spec-only PR. The implementation is PLAT-1440 (manifest, skeleton,
  fixtures, tests) and the category vocabulary is PLAT-1441. It is not
  counted as a defect of this PR.
- FR-007-AC-5: bound to TC-104
  (`tests/test_systems_kinds.py::test_edge_verbs_and_roles_are_declared_and_used`).
  The amended AC no longer agrees with that test (FND-001).
- The manifest `connection` entry still has only `connects` and
  `realizes_requirement`. The new FR-007 Behavior line ("SHALL admit
  `carries`") is ahead of the code until PLAT-1440 lands. That is the
  normal spec-first state.
- No production code changed, so there is no code without an owning
  requirement, no stub and no coverage inflation from new code.

## Verdict

**CONDITIONAL.** One binding becomes wrong when this PR merges: the matrix
will count the amended FR-007-AC-5 as tagged, but its test asserts the old
verb set.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | TC-104 is tagged to FR-007-AC-5 and asserts `used_verbs == EDGE_VERBS \| {DESIGN_VERB}`, so it requires `carries` to be absent. The amended AC-5 requires `carries` on `connection` only. Once this merges, the matrix shows AC-5 as tagged by a test that asserts the opposite of the new clause. Fix: in PLAT-1440, update TC-104 to require `carries: [data_classification]` on `connection` and on no other kind, or say in this PR that the binding is stale until PLAT-1440. | tests/test_systems_kinds.py:246-262; FR-007-AC-5 | correct-requirement-no-evidence |

## Dispositions

| FND | Outcome | Reason |
|---|---|---|
| FND-001 | deferred | PLAT-1440. TC-104 no longer asserts the opposite of the amended FR-007-AC-5: it now asserts `used_verbs - {"carries"} == EDGE_VERBS \| {DESIGN_VERB}` and that no systems kind other than `connection` declares `carries`. It does not yet require `carries: [data_classification]` on `connection`, because the manifest does not declare it until PLAT-1440 lands, so the positive clause of AC-5 still has no evidence. PLAT-1440 implements the FR-007 amendment and adds the edge; it owns adding that positive assertion to TC-104. |
