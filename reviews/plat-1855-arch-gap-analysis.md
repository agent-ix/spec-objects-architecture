---
id: SR-052
title: "Gap analysis — PLAT-1855 FR-016 and FR-010-AC-3 against the code step (PR #59)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-016-segregation-design-relation.md, spec/functional/FR-010-design-realization-edge.md, tests/test_design_edges.py, tests/conftest.py, spec_objects_architecture/manifest.yaml"
review_set: subset
---
# SR-052: Gap analysis — PLAT-1855 FR-016 and FR-010-AC-3 against the code step (PR #59)

## Summary

Ticket: PLAT-1855. Spec-only PR; the review asks what the code step will have to build and test, and
whether the criteria let it. Plan completion: not assessed.

`quire matrix --scope .` on the PR head: FR-016-AC-1 to AC-10 are `untagged` (expected for a spec-first
PR); CON-1 and CON-2 are `method-without-symbol` (Inspection). FR-010-AC-3 is tagged to
`tests/test_design_edges.py:100` (TC-142).

What the code step must do, by criterion:

- FR-010-AC-3: relax TC-142 (see FND-001).
- FR-016-AC-1..3: manifest `edge_types`, `part`/`connection` `allowed_links`, two `required_relations`
  with `when_any`, `design_relations` append; assertions in the style of TC-140..142.
- FR-016-AC-4..9: a fixture with a `control` document and an FR/NFR that `satisfies` it, plus part,
  connection and ADR sources. `tests/conftest.py` `module_args` loads spec-objects-security by default
  (`security=True`), so `control` is declared in the test corpus and `when_any` is live.
- FR-016-AC-10: Demonstration via `quoin class obligations` (see FND-002).

No manifest or test change is in this PR, so there is no stub, orphan or coverage inflation to report.

## Verdict

**CONDITIONAL.** The criteria are implementable; one medium gap (the existing test pins what the new AC
disclaims) and two low gaps the code step will trip on. The missing criterion for the design-gate
consequence is recorded in SR-051 FND-001 and not repeated here.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | TC-142 (`test_fr010_ac3_manifest_declares_exactly_the_two_relations`) asserts the exact seven-entry `required_relations` list (lines 101-109) and `design_relations == [fr-has-design-element, nfr-has-design-element]` (line 123). The new FR-010-AC-3 says it states no count and only fixes the first two entries, so the bound test now exceeds its criterion and will fail as soon as FR-016's manifest change lands. The code step must change both asserts to a prefix check, drop the full-list assert, and rename the test; FR-016-AC-3 then owns the tail. | tests/test_design_edges.py:99-123 | correct-requirement-no-evidence |
| FND-002 | low | FR-016-AC-10 does not say the fixture `FR` carries a `software_safety_class` that the class policy lists. Under quoin FR-161 a requirement without a class is listed `unassigned` with no rows, so a classless fixture can show neither `unmet` nor `met`. State the class in the criterion. | spec/functional/FR-016-segregation-design-relation.md:104 | wrong-requirement |
| FND-003 | low | The Behavior bullet requiring `trace:undeclared-relation-vocabulary` when no loaded module declares `control` (or `ADR`, `FR`, `NFR`) has no criterion. Because tests load spec-objects-security by default, the case needs `security=False`; FR-010-AC-9 is the analogue for `ADR`. Add a criterion or drop the bullet as inherited quire-rs FR-058-AC-35 behaviour. | spec/functional/FR-016-segregation-design-relation.md:91 | missing-requirement |
