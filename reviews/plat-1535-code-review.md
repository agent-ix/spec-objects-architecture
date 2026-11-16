---
id: SR-044
title: "Code review — data sink object and delivery edges"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; typespec/main.tsp, spec_objects_architecture/manifest.yaml, spec_objects_architecture/schemas/{DataSink,PurposeToken}.json, spec_objects_architecture/skeletons/data_sink.md, tests/test_data_sink.py, tests/fixtures/data_flow/"
review_set: subset
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/FR-015"
    type: references
---

## Summary

Reviewed PR #55's changed files against PLAT-1535's eight acceptance criteria, with FR-015 as context. The main sink, edge, schema, fixture, and relation-report paths are present; the review found a purpose-token validation hole and colliding trace IDs that leave the new criteria absent from the computed matrix.

## Verdict

**FAIL** — a required value can be blank whitespace, and the new test IDs conflict with existing test catalog entries, so the computed matrix does not bind any FR-015 criterion to these tests.

## Coverage

The ticket's eight acceptance criteria were examined. The valid fixtures cover all eight kinds and all four processor-agreement values; the invalid fixtures cover the required agreement, bad kind, region, wrong-kind edge, dangling target, wrong carries target, and unknown record key. The report test checks sink IDs, kinds, agreement presence, and both authored processors. I inspected the assertions but did not run the test suite. `make schemas-check` was run separately and passed.

## Findings

| ID      | Severity | Summary                                                                                  | Refs                                      |
| ------- | -------- | ---------------------------------------------------------------------------------------- | ----------------------------------------- |
| FND-001 | high     | New sink tests reuse TC IDs already assigned to unrelated tests, leaving FR-015 unbound | tests/test_data_sink.py:35-165            |
| FND-002 | medium   | PurposeToken accepts whitespace-only values despite the non-empty purpose contract       | spec_objects_architecture/schemas/PurposeToken.json:4-6 |

The matrix issue is recorded as a traceability defect: `TC-160..162` are already assigned to FR-012 tests and `TC-163..166` to FR-014 tests in `spec/tests.md`; the new functions reuse `TC-160..165`. `quoin matrix --repo . --json` reports FR-015-AC-1 through FR-015-AC-12 as `untagged`, with no binders, and reports each new test annotation as `tagged-without-citing-matrix-row`.

The purpose schema's `minLength: 1` rejects only the empty string. It accepts values such as `"   "`, while `tests/test_data_sink.py` checks only `purpose: [""]`.

## Dispositions

Not applicable in the review pass.
