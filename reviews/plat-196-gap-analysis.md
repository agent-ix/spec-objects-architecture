---
id: SR-011
title: "Gap analysis — FR-008 record-key sections (PR #41)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; PR #41: spec/functional/FR-008-record-key-sections.md (AC-1..7), spec/tests.md TC-120..TC-126, tests/test_record_sections.py"
review_set: subset
---
# SR-011: Gap analysis — FR-008 record-key sections (PR #41)

## Summary

Ticket: PLAT-196 (also PLAT-201). `quire matrix --scope .` shows FR-008-AC-1
through AC-7 each tagged by at least one test in `tests/test_record_sections.py`.
Each binding was read for intent. AC-1 is backed by TC-120, AC-2 by both TC-121
tests, AC-3 by TC-122, AC-4 by TC-123, AC-5 by both TC-124 tests, AC-6 by
TC-125 and AC-7 by TC-126. Every test asserts what its criterion states,
including the negative halves: `route-operation-unknown`, the fence-only
`associated_types` being `not_applicable`, `size-unknown-field`,
`size-ambiguous`, the `## Endianness` prose, `status-required`, the bullet-list
`## Registration` refusal, and no diagnostic for `## Requires`. No code exists
without an owning requirement. No stubs were found. Plan completion: not
assessed.

## Verdict

**NOT MERGEABLE.** FR-008-AC-2's test fails against the declared semantic-core
0.3.3 for `interface` (code-review SR-010 FND-001 has the root cause), so AC-2 has
no passing evidence. The low gap: FR-008 says three bullet-list sections break,
but only one is tested.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | FR-008-AC-2 requires each extracted value "valid against its model", but `test_each_skeleton_authors_its_record_keys_and_they_validate[interface]` fails against the published semantic-core 0.3.3 `TypeRef.json`, because the extracted `target` is the adjacent `{kind, value}` object. The matrix row is `tagged` and `tests.md` marks TC-121 ✅, yet the criterion has no passing evidence under the module's declared dependency. | tests/test_record_sections.py:109-125, spec/tests.md TC-121 | correct-requirement-no-evidence |
| FND-002 | low | FR-008 Behavior says the conversion breaks `## Thresholds`, `## Registration` and `## Stability` bullet lists ("the engine refuses each as `semantic.feature-not-extractable`"), but only the `## Registration` refusal is asserted (AC-6). No test pins the `## Thresholds` or `## Stability` refusal that the breaking-change statement relies on. | spec/functional/FR-008-record-key-sections.md (breaking-change bullet), tests/test_record_sections.py:264-313 | correct-requirement-no-evidence |

## Dispositions

| FND | Outcome | Reason |
|---|---|---|
| FND-001 | deferred | Release-blocked, same root as SR-010 FND-001 and FND-002. AC-2 has passing evidence only once a semantic-core release carries the `{kind, value}` `TypeRef` target and a quire release carries FR-081. On `7b21aef` TC-121[interface] still fails against published 0.3.3. `tests.md` no longer claims ✅ (d24396c). It blocks merge. |
| FND-002 | fixed | d24396c: TC-125 now asserts the `semantic.feature-not-extractable` refusal for bullet-list `## Registration`, `## Stability` and `## Thresholds`, with reason equal to the key (passes on a FR-081 build). |
