---
id: SR-023
title: "Gap analysis — PLAT-1577 part software safety class (PR #46)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-012-software-safety-class-assignment.md, tests/test_software_safety_class.py, typespec/main.tsp, spec_objects_architecture/manifest.yaml, spec_objects_architecture/schemas/Part.json, spec_objects_architecture/schemas/PartFrontmatter.json, spec_objects_architecture/skeletons/part.md"
review_set: subset
---
# SR-023: Gap analysis — PLAT-1577 part software safety class (PR #46)

## Summary

Ticket: PLAT-1577. Plan completion was not assessed. This review traces the
FR-012 criteria the PR claims (AC-1 to AC-8, AC-11, AC-12, CON-1 and CON-2)
to the tagged tests and the code. AC-9, AC-10, AC-13, AC-14 and AC-15 are out
of scope: they need quire-rs FR-090/091 (PLAT-1578), and the PR says it does
not cover them. The spec is not changed by this PR, so spec-review did not
run.

Each binding was checked against its asserts:

- AC-1: correct. Schema inspection covers type, minLength, no enum, no
  default, not required, and both directions of `dependentRequired`.
  `make schemas-check` passes.
- AC-2: correct. All three locators are checked for `from`, `path` and
  `required: false`.
- AC-3: correct. The document validates and extract carries the three values
  as written.
- AC-4: correct. The skeleton validates and its record has none of the keys.
- AC-5, AC-6 and AC-7: tests exist at both the record-schema and
  `quire validate` levels, but some cases are missing (FND-001).
- AC-8: the tests validate two parts with different classes. The fixture
  does not make the item owned by the system (FND-003). The "no module file
  computes one from the other" clause is confirmed by inspection: no file
  reads or derives a class.
- AC-11: correct. The test checks that the skeleton names and does not carry
  the fields. Skeleton validity is covered by
  `test_every_skeleton_validates_with_no_error` and by AC-4.
- AC-12: the schema half is tested. The corpus half is not (FND-002).
- CON-1 and CON-2: Inspection. Both hold by inspection. The test tagged
  CON-1 is wrongly bound (SR-022 FND-001).

## Verdict

**CONDITIONAL.** The code meets the claimed FR-012 criteria. I checked by
hand that `quire validate` refuses an empty assigner, a missing class and a
missing rationale. The gaps are missing test cases and one AC claimed in
full when only half of it is covered.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | FR-012-AC-6 ("empty **or** absent assigner") has no test for the empty case at any level. The record-schema parametrisation covers absent rationale, absent assigner, absent class, empty class and empty rationale. The `quire validate` parametrisation covers absent rationale, absent assigner, absent class and empty class. The empty assigner case appears in neither. The empty rationale case (AC-5) is tested only against `Part.json`, not through `quire validate`. Dropping `minLength` from `software_safety_class_assigned_by` in `PartFrontmatter` would pass every test. I confirmed by hand that engine 0.59.1 does refuse it today (`"" is shorter than 1 character (at software_safety_class_assigned_by)`). Add the empty-assigner case to both parametrisations and the empty-rationale case to the `quire validate` one. | tests/test_software_safety_class.py:136-200 | correct-requirement-no-evidence |
| FND-002 | medium | `test_fr012_ac12_part_frontmatter_ref_is_self_contained_and_open` carries the `FR-012-AC-12` tag, which reads as full coverage. It covers only the schema half. The second clause, that an all-unassigned corpus with the ISO module loaded yields no `trace:undeclared-relation-vocabulary` finding for the three named entries, is not tested. That clause depends on manifest entries this PR defers to PLAT-1578, and neither the PR body nor the test docstring lists AC-12 as partial. Either list AC-12 as partially deferred (with AC-9/10/13-15) in the PR body and the module docstring, or add the corpus test when the entries land. | tests/test_software_safety_class.py:220-230 | correct-requirement-no-evidence |
| FND-003 | low | The AC-8 fixture does not model "an item part owned by" the system part. Both documents come from the skeleton unchanged, so both have Owner `search_service`, and `pump_item` is not owned by `pump_system`. The test shows that two parts carry independent classes, but not the system/item ownership the AC describes. Set the item's Owner cell to `pump_system`. | tests/test_software_safety_class.py:203-209 | correct-requirement-no-evidence |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (c34ee27). An empty-assigner case is added to the record-schema parametrisation. Empty-assigner and empty-rationale cases are added to the `quire validate` parametrisation, with key-specific assertions. Focused run with quire 0.44.0: 19 passed. |
| FND-002 | fixed | Round 1 (c34ee27). The `FR-012-AC-12` tag is removed and the test is renamed `test_part_frontmatter_ref_is_self_contained_and_open`, with a comment saying the criterion is not claimed. The PR body now lists FR-012-AC-12 as partially covered (schema half only), with the corpus clause blocked on PLAT-1578. |
| FND-003 | fixed | Round 1 (c34ee27). The item fixture's Owner cell is rewritten to `pump_system`, guarded by `assert "\| pump_system \|" in item_text`, and both documents validate. |
