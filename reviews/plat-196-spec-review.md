---
id: SR-012
title: "Spec review — FR-008 and the FR-004/FR-006/spec.md edits (PR #41)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; PR #41: spec/functional/FR-008-record-key-sections.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-006-architecture-lowerings.md, spec/spec.md, spec/tests.md, spec/functional/index.md"
review_set: subset
---
# SR-012: Spec review — FR-008 and the FR-004/FR-006/spec.md edits (PR #41)

## Summary

Ticket: PLAT-196 (also PLAT-201). Checked FR-008 (statement and AC-1..7), the
FR-004 and FR-006 Behavior and Dependencies edits, spec.md's Scope, Out of Scope
and References edits, and tests.md TC-120..TC-126, against quoin FR-121 and
FR-122 (quoin `origin/main`, normative) and quire-rs FR-081.

FR-008's key/heading/form table matches the FR-122 table exactly. The
route-operation, `Status`-required, `associated_types`-table-only, `## Layout`
`size`, `format`/`magic`-as-documentation, prose `## Endianness`/`## Records`,
and relation-keys-from-`## Relationships` rules match FR-122 Behavior. Every
item on FR-122's Downstream list is done: the three tables converted, both
tokens added, the five new sections, `associated_types[]` dropped from FR-006,
the `LayoutField` doc widened, decision #20 reversed, and Out of Scope naming
PLAT-196. `quire validate` passes FR-008. The `tests.md` structural failure
(`Coverage Status` column) is pre-existing on `origin/main`.

## Verdict

**CONDITIONAL.** No high spec finding. One medium contradiction is left inside
FR-006, plus three lows: one wording issue and two ceremony/grammar issues.
Merge is blocked by the code-review highs (SR-010), not by the spec.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | FR-006 Behavior still says "the engine-side mapping is `agent-ix/quoin#335` and its quire-rs successor". The same PR changes FR-006 Dependencies to name quoin FR-122 as the mapping owner, and FR-122 says Quire adopts the FR-006 `operations` lowering unchanged. FR-006 now names two different owners for one mapping. | spec/functional/FR-006-architecture-lowerings.md:56, :79 | wrong-requirement |
| FND-002 | low | FR-008-AC-5 reads "two `RecordLayout`s with `tag` `\"0x21\"`", which says both records carry the tag. Only `posting_tuple` does, which is what TC-124 asserts. Reword to "two `RecordLayout`s, `posting_tuple` with `tag` `\"0x21\"`". | spec/functional/FR-008-record-key-sections.md AC-5 | wrong-requirement |
| FND-003 | low | The rewritten FR-004 bullet ("The schema criteria over those keys SHALL be verified against hand-built JSON records and SHALL say so in the test itself...") is a test-labelling rule, not behaviour. It is ceremony under the value test, since tests test functionality, and `quire validate` flags it `ears:non-singular` and `quality:agentless-passive`. Delete it. Its `tests.md` Test Environment counterpart can go with it. | spec/functional/FR-004-role-schemas.md:84 | wrong-requirement |
| FND-004 | low | `tests.md` adds hand-written ✅ status cells for FR-008 and TC-120..TC-126, but `quire matrix` computes the matrix. The cells are false today: TC-121 fails against the declared semantic-core, and every TC fails under the locked `quire`. A hand-kept status column is ceremony that drifts. Drop the status cells, or at least do not claim ✅. | spec/tests.md (FR-008 row, TC-120..TC-126) | correct-requirement-no-evidence |
