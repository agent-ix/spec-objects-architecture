---
id: SR-054
title: "Gap analysis — PLAT-1855 segregation design relation (PR #60)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-016-segregation-design-relation.md, spec/functional/FR-010-design-realization-edge.md, spec_objects_architecture/manifest.yaml, tests/test_segregation.py, tests/test_design_edges.py, tests/test_systems_kinds.py"
review_set: subset
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/FR-016"
    type: references
---
# SR-054: Gap analysis — PLAT-1855 segregation design relation (PR #60)

## Summary

Ticket: PLAT-1855. A planless audit, scoped to FR-016 and the FR-010-AC-3/AC-10 edits in
`git diff origin/main...HEAD` at `beff9a8`. `quire matrix --scope . --format json` (quire 0.52.0)
over a scratch copy of the PR head, with sibling modules from each repository's `origin/main`,
reports all fourteen criteria FR-016-AC-1..14 `tagged`. FR-016-AC-14 is tagged by two tests, one
of them a strict xfail.

Each AC was checked against its test and its behaviour, by running the test and a manifest
mutation that should make it fail (all killed; see SR-053):

- AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-11 and AC-13 are asserted as written.
  AC-11 is the only behavioural test of the `satisfied_by` condition, and dropping that condition
  fails it.
- AC-12: the ADR edge covers the requirement. The advisory is asserted to follow the loaded
  process manifest. It is measured in single-file validation, since `--okf` does not emit
  `disallowed-edge-type`, and it disappears with spec-artifacts-process PR #163.
- AC-10 is `Demonstration`. The test checks the design-join rows the `segregation` kind reads,
  before and after the edge, and that unlinked requirements have no row. `quoin class obligations`
  is not run: the installed quoin 0.36.8 refuses the policy with
  `unknown field relation, expected one of id, kind, method`, which I reproduced. The 🚧 on TC-184
  is accurate.
- AC-14: only the "security loaded" half passes. The "security off" half is a strict xfail; see
  FND-001.
- FR-016-CON-1 (inspection): the diff adds no object type and no engine behaviour, only
  `edge_types`, `allowed_links`, `required_relations` and `design_relations` data. FR-016-CON-2:
  nothing in the module writes an edge.

Reverse gap: every manifest line the PR adds is owned by FR-016. No stub and no coverage
inflation was found; the xfail is strict.

## Verdict

**CONDITIONAL.** No criterion is untagged. FND-001 is medium, and SR-053 FND-001 carries the
required edit. FND-002 is low.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | medium | FR-016-AC-14's security-off half has no passing test. It is a strict xfail whose stated cause is not the measured one: the engine silently drops all required relations when a `record_keys` relation names an undeclared kind (the module's own `data_classification` / `trust_boundary` relations). UnknownRole is not the cause. With `record_keys` removed from those three relations, the AC holds as written (`undeclared-relation-vocabulary` naming `control` for both relations). The AC stays; the xfail reason and the TC-188 row must state the real cause and cite a quire-rs issue, as SR-053 FND-001 requires. | tests/test_segregation.py:400-419 |
| FND-002 | low | The passing AC-14 test asserts the `ADR` advisory only for `fr-has-segregation`, though the AC says "for each relation of this requirement". The "a `control` document present" variant is not exercised. Add `NFR_REL` to the assertion. | tests/test_segregation.py:384-397 |

## Coverage

- FR-016-AC-1..14: 14 of 14 tagged in the computed matrix. 13 have a passing test; AC-14 is
  partial (FND-001).
- FR-010-AC-3 (TC-142) and FR-010-AC-10: tagged and passing, with and without security PR #80
  loaded.
- Semantic review: skipped (not requested); intent was checked per AC by hand above.
- Plan completion: not assessed

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (d035469). The security-off half is a probe-conditional strict xfail tied to PLAT-1856 (the engine defect), with the measured cause. It runs as a plain test once the engine reports, and passes against a module copy without the triggering `record_keys`. FR-016-AC-14 is unchanged, as recommended. |
| FND-002 | fixed | Round 1 (d035469). The security-loaded AC-14 test now also asserts the `ADR` advisory for `nfr-has-segregation`. Mutation: removing `ADR` from `nfr-has-segregation.to` fails it at that assertion. |
