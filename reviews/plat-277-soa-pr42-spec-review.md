---
id: SR-015
title: "Spec review — PLAT-277 F1 FR-009 and the FR-004/FR-005 edits (PR #42)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-009-optional-sections-optional-keys.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-005-executable-skeletons.md, spec/tests.md, spec/spec.md, spec/functional/index.md"
review_set: base
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-009", type: references}
  - {target: "ix://agent-ix/spec-objects-architecture/FR-004", type: references}
  - {target: "ix://agent-ix/spec-objects-architecture/FR-005", type: references}
---
# SR-015: Spec review — FR-009 and the FR-004/FR-005 edits (PR #42)

## Summary

Ticket: PLAT-277 (finding F1). This is a base checklist review of the spec
diff, with no analysis lenses: the scope is one small FR plus edits, and no
AssuranceProfile exists in the repo. Reviewed: the new FR-009
(Description/Inputs/Outputs/Behavior, CON-1, AC-1 to AC-3); FR-004's Behavior
lead sentence, the nine edited table rows, AC-8, AC-9, AC-12 and the removed
CON-2; the FR-005 negative-fixture bullet and AC-5; the tests.md rows TC-037,
TC-038, TC-041, TC-054, TC-130 and TC-131; and the spec.md and index.md
entries.

Clean on this pass:

- The ids are well-formed and unique. FR-009, TC-130 and TC-131 do not clash
  with PR #41's FR-008 and TC-120 to TC-126.
- Every new AC has a TC.
- CON-2 is removed everywhere outside historical review records. Only
  `spec/reviews/8-...` and old `reviews/` files still mention it, and those
  stay as they are.
- AC-8, AC-9 and AC-12 match the schemas.
- `quire validate` passes on the FR files. `tests.md` fails on its
  `Coverage Status` column header, which this PR does not change.

## Verdict

**CONDITIONAL.** No high findings, two medium. FR-009's central rule names
"the manifest locator for the key" but never says which locator sources which
key, and its Inputs list names the wrong locators. FR-005 still describes
types that "require" `operations` and `clauses`.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | FR-009-CON-1 ("A schema SHALL require a key only where that type's manifest locator for the key is `required: true`") cannot be checked as written. Locators are named after sections (`properties`, `invariants`, `features`), not record keys (`fields`, `clauses`, `featureOrder`), and FR-009 never states the mapping. Its Inputs also give the optional sections as "`operations`, `properties` and `api_contract`", which leaves out `invariants`, the source of `clauses` for four types, and includes `api_contract`, which sources no record key. The vacuous TC-131 (SR-013 FND-001) follows from this. Fix: state the mapping `fields`←Properties, `clauses`←Invariants, `operations`←Operations, `featureOrder`←Features (FR-004 Inputs already says most of it) and correct the list. | FR-009 Inputs, FR-009-CON-1, FR-009-AC-3, FR-004 Behavior lead sentence | wrong-requirement |
| FND-002 | medium | FR-005 Behavior still says "Each skeleton whose type requires `operations` (...)" and "Each skeleton whose type requires `clauses` (...)". After FR-009 no type requires either key, so the condition matches nothing and only the parenthesised lists keep the rule meaningful. That contradicts FR-009 Outputs. Fix: reword to "whose type carries an item rule on `operations`" (or `clauses`), or name the types outright. | FR-005-executable-skeletons.md:54, FR-005-executable-skeletons.md:57 | wrong-requirement |
| FND-003 | low | In the FR-004 table, nine rows now read "Required keys: none (FR-009)", but `operations`, `fields` and `clauses` were not added to the Optional keys column, so each of those keys is in neither column and appears only in Item rules. FR-004-AC-1 also still says "`BinaryFormat` and `RateLimit` share a required set", when nine types now share the empty set. | FR-004 Behavior table, FR-004-AC-1 | wrong-requirement |
| FND-004 | low | Value test: hand-kept counts and ranges are ceremony. "at least the nine cases" (FR-005-AC-5), the TC-054 title, the test name `..._named_nine_...`, the comment "six of the nine", and the tests.md coverage ranges (`FR-004-CON-1, FR-004-CON-3`) all had to be edited by hand for one fixture removal. The `NEGATIVE_FIXTURES` tuple already pins the set, so drop the numbers from the AC, TC title, test name and comment. | FR-005-AC-5, spec/tests.md TC-054, tests/test_skeletons_semantic.py:202,226,257 | wrong-requirement |
