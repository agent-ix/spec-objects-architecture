---
id: SR-014
title: "Gap analysis — PLAT-277 F1 optional record keys (PR #42)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-009-optional-sections-optional-keys.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-005-executable-skeletons.md, spec/tests.md, tests/"
review_set: subset
---
# SR-014: Gap analysis — PLAT-277 F1 optional record keys (PR #42)

## Summary

Ticket: PLAT-277 (finding F1). This review traces the criteria the PR adds or
edits to the tagged tests and the code: FR-009-AC-1 to AC-3 and FR-009-CON-1
(TC-130 and TC-131), FR-004-AC-8, AC-9 and AC-12 (TC-037, TC-038 and TC-041),
and FR-005-AC-5 (TC-054). Plan completion was not assessed. There is one
medium finding.

Each binding was checked against the asserts:

- TC-130 → FR-009-AC-1 and FR-009-AC-2: correct. It checks both directions,
  absent validates and present-but-bad is refused.
- TC-131 → FR-009-AC-3 and FR-009-CON-1: the tag is correct but the evidence is
  weak (SR-013 FND-001).
- TC-037 → FR-004-AC-8 and TC-038 → FR-004-AC-9: correct. The test with no
  `clauses` is now positive, and the no-`post` and `fields` refusals are kept.
- TC-041 → FR-004-AC-12: correct. `{}` fails only `Interface`.
- TC-054 → FR-005-AC-5: correct. The pinned set is now nine files.

The deleted and renamed negative fixtures still match real failures. I checked
this end to end with quire 0.54.0 `validate_document`:

- The deleted `rate_limit-no-invariants.md` failed `clauses is a required
  property` on `origin/main` and has zero errors on this PR, so it really is a
  valid document now.
- The old `external_contract-no-invariants.md` text now fails at `operations`
  because no item has a `post`. That is the failure the renamed
  `external_contract-no-guaranteed-operation.md` claims, and that fixture
  passes TC-054 and its own-reason test.

## Verdict

**CONDITIONAL.** The code meets FR-009. The defect PLAT-277 F1 reports is a
document refused as `semantic.record-invalid`. That is now verified only on a
hand-built `{}` record, and no committed test exercises a document.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | No engine-level test covers FR-009-AC-1. The F1 failure is a *document* missing `## Invariants`, `## Operations` or `## Properties` being refused, but TC-130 only checks a hand-built `{}` against the JSON schema. The fix works only because the extractor *omits* the key for an absent section; emitting `clauses: []` would still fail `minItems`. No test pins that behaviour, and the one document that exercised it (`rate_limit-no-invariants.md`) was deleted rather than turned into a positive case. Add a test that runs `validate_document` on a rate_limit document with no `## Invariants` and on an api_endpoint document with no `## Operations`, and asserts zero errors. I reproduced this by hand: zero errors on the PR, `clauses is a required property` on main. | tests/test_role_schemas.py:510-521, spec/functional/FR-009-optional-sections-optional-keys.md | correct-requirement-no-evidence |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (0576d80). `test_a_document_without_the_optional_section_validates` (TC-130) cuts the section from a skeleton and runs `validate_document`. On `origin/main` schemas, the rate_limit, api_endpoint, action and binary_format cases fail `record-invalid`; on the PR they give zero errors. The external_contract and extension_point cases are vacuous (FND-002). |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-002 | medium | Two of the six cases in the new document test are vacuous. Cutting `## Invariants` from the external_contract and extension_point skeletons leaves `Post:` lines naming undeclared clauses. Those documents then fail `semantic.dangling-clause-ref` on both `origin/main` and the PR schemas, and no `record-invalid` is raised either way. The test only filters for `record-invalid`, so these cases pass on main too. Despite the test's name, the documents do not validate. Fix: also strip the `Pre:`/`Post:` lines (or use a fixture without them) and assert zero errors, so each case fails on the main schemas. | tests/test_role_schemas.py:555-576 | correct-requirement-no-evidence |
