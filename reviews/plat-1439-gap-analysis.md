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

## Round 2 (a61972d)

a61972d changes only FR-013 prose and AC-2. It changes no test, manifest or fixture. FR-013-AC-1 to AC-8 are still untagged, and that is expected for a spec-only ticket. Removing AC-2's cross-repository sentence takes away a criterion that PLAT-1440 could not have met. No criterion lost its evidence.

FND-001 is still **deferred to PLAT-1440**, and the deferral is correct. TC-104 passes at HEAD, because the manifest has no `carries`. When PLAT-1440 adds `carries: [data_classification]`, TC-104 fails at `tests/test_systems_kinds.py:262`: `data_classification` is not a manifest role (see SR-026 FND-002). So PLAT-1440 cannot land without editing TC-104. That edit is the natural place to add the positive assertion.

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-002 | low | The TC-104 deferral is recorded only in this artifact and in the PLAT-1439 tracker comment. The PLAT-1440 ticket body does not mention TC-104. Its AC 8 ("existing tests stay green") would pass if the implementer only relaxed line 262 and never asserted `carries: [data_classification]` on `connection`. That would leave FR-007-AC-5's positive clause without evidence. The PLAT-1440 Scope list also predates round 1 and omits the reverse relation `classification-carried-by-connection` and the `trace:classification-without-connection` key that FR-013 now requires. Fix (owner or code lead, not this PR): add both points to PLAT-1440. FR-013 is the authority. | PLAT-1440; FR-007-AC-5; FR-013 Outputs; tests/test_systems_kinds.py:246-267 | correct-requirement-no-evidence |

**Round-2 verdict: CONDITIONAL.** No defect in this PR. One low tracker-hygiene finding on the downstream ticket.

## Round 3 (f5970b9)

f5970b9 changes only the FR-013 dangling Behavior line. FR-013-AC-1 to AC-8 are still untagged. That is
expected for a spec-only ticket, and their implementation is PLAT-1440's. No criterion lost its evidence.

| FND | Outcome | Reason |
|---|---|---|
| FND-001 | deferred | PLAT-1440, and the deferral is still accurate. TC-104 at HEAD is unchanged. It asserts `used_verbs - {"carries"} == EDGE_VERBS \| {DESIGN_VERB}` and that no systems kind other than `connection` declares `carries`. The manifest still has no `carries` on `connection` (`manifest.yaml:532` lists only `connects`), so FR-007-AC-5's positive clause has no evidence yet, and PLAT-1440 owns adding it. |
| FND-002 | fixed | The PLAT-1440 description, read with `linear issue view`, now covers everything this finding asked for. Its Where section has the TC-104 positive assertion, keeps `carries` absent on the other kinds, and exempts this typed link from the role-target rule. Its Scope and Design notes have both the forward `connection-carries-classification` relation and the incoming reverse `classification-carried-by-connection` relation. Both `trace:` keys default to `off`. AC 6 asserts both report views. AC 8 restates the TC-104 change. |

New findings (round 3): none of my own. SR-028 FND-007 (FR-013-AC-7 is not limited to systems kinds,
and `queue` already declares `carries`) affects the test PLAT-1440 will write for AC-7. It is counted
there, not here.

**Round-3 verdict: PASS.** No open gap-analysis finding. FND-001 stays correctly deferred to PLAT-1440.
