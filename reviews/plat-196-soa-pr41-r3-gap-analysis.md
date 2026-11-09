---
id: SR-017
title: "Gap analysis r3 — FR-008 and the engine-drift adaptations at e164b70 (PR #41)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; PR #41 diff origin/main...e164b70: spec/functional/FR-008-record-key-sections.md (AC-1..7), FR-002-CON-4, FR-003-AC-9, FR-005-AC-10, FR-009-AC-1, spec/tests.md, tests/"
review_set: subset
---
# SR-017: Gap analysis r3 — FR-008 and the engine-drift adaptations at e164b70 (PR #41)

## Summary

Ticket: PLAT-196 (also PLAT-201). `quire matrix --scope .` at e164b70 shows
FR-008-AC-1..7, FR-003-AC-9, FR-005-AC-10 and FR-009-AC-1 each `tagged`.
FR-002-CON-4 is `method-without-symbol` because it is an Inspection constraint;
`origin/main` reports the same, so this PR did not introduce it.

Each changed binding was read for intent:

| Test case | Criterion | Reading |
|---|---|---|
| TC-120 | FR-008-AC-1 | correct |
| TC-121 (both tests) | FR-008-AC-2 | correct: exactly the table's keys, `available`, each value valid against its model; the interface value now validates against the published semantic-core 0.4.1 `TypeRefTarget` |
| TC-122 | FR-008-AC-3 | correct |
| TC-123 | FR-008-AC-4 | correct |
| TC-124 (both tests) | FR-008-AC-5 | correct |
| TC-125 | FR-008-AC-6 | correct; it also pins the `## Stability` and `## Thresholds` bullet refusals |
| TC-126 | FR-008-AC-7 | correct |
| TC-091 | FR-005-AC-10 | correct; the AC now states the engine collapses shared-id entries, and the test asserts no `semantic.ambiguous-type`, with no xfail |
| TC-019 | FR-002-CON-4 | correct |
| TC-130 | FR-009-AC-1 | correct |
| TC-111 | FR-003-AC-9 | wrong: see FND-001 |

No code exists without an owning requirement. No stubs were found. Plan
completion: not assessed.

## Verdict

**MERGEABLE after one medium wording fix.** One criterion's text no longer
states what its test asserts. Every other changed criterion has passing,
intent-matched evidence (coder-reported run at e164b70; not re-run here).

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | FR-003-AC-9 still ends "while a doubled hyphen is refused with its required `id` missing". The FR-003 Behavior bullet ("yields no value and Quire refuses the artifact with its required `id` missing") and the TC-111 title say the same. The engine-drift adaptation changed the test to assert a different observable: the message `[queue] required 'id' (frontmatter_field(id)) value "queue--001" does not match pattern /…/`, a pattern mismatch on a present value rather than a missing one. The criterion now names behaviour that no longer occurs, and its bound test asserts something else. Reword AC-9, the Behavior bullet and the TC-111 title to "refused because its `id` does not match the pattern". | spec/functional/FR-003-semantic-manifest-contract.md:50, :67; spec/tests.md:164; tests/test_manifest_semantic.py:145-150, :200 | wrong-requirement |

## Dispositions

| FND | Outcome | Reason |
|---|---|---|
| FND-001 | fixed | Round 1 (2970c1a). FR-003-AC-9, the FR-003 Behavior bullet (line 50) and the TC-111 title now say a doubled hyphen is "refused because its `id` does not match the pattern". That matches the message TC-111 asserts. `quire validate` passes FR-003. |
