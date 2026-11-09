---
id: SR-013
title: "Code review — PLAT-277 F1 optional record keys (PR #42)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; typespec/main.tsp, spec_objects_architecture/schemas/*.json, tests/test_role_schemas.py, tests/test_skeletons_semantic.py, tests/fixtures/negative/"
review_set: subset
---
# SR-013: Code review — PLAT-277 F1 optional record keys (PR #42)

## Summary

Ticket: PLAT-277 (finding F1). Reviewed `git diff origin/main...HEAD` at
`plat-277-optional-record-keys`: the TypeSpec change (eleven `?` additions in
nine models), the nine regenerated JSON schemas, the fixture deletion and
rename, and the two test files. Three findings, one medium, two low.

Verified by running, not by reading:

- `node scripts/generate-schemas.mjs --check` with `npm ci` of the pinned
  devDependencies (`@agent-ix/semantic-core` 0.3.3, `@typespec/*` 1.15.0):
  "40 schema(s) match the committed output". The regenerated JSON equals what
  the TypeSpec emits. The main checkout's `node_modules` holds a stale
  semantic-core 0.3.0, which reports 21 files of false drift.
- The JSON diff is 29 deleted lines across nine `required` arrays and nothing
  else. No `minItems`, `maxItems`, `contains`, `minContains` or `maxContains` is
  touched, and neither the manifest, a locator nor a construct is changed.
- Each relaxed key is checked against `manifest.yaml`. `operations` comes from
  `## Operations`, `fields` from `## Properties` and `clauses` from
  `## Invariants`, and every one of those locators is `required: false` on
  each of the nine types. `Interface` keeps `required: [featureOrder]`, whose
  `features` locator is `required: true`. Part, Port, Connection and Allocation
  keep their required keys, which come from required `table_row` locators.
- The full suite ran under quire 0.54.0, from the existing
  spec-objects-business venv: 253 passed. The PR adds no failure. The two
  remaining failures (`test_a_per_file_bundle_index_...` and
  `test_underscore_and_hyphenated_...`) fail the same way on `origin/main`, and
  `make build` fails only because the borrowed venv has no `build-tools`. All
  nine negative fixtures fail for their own reason, including
  `external_contract-no-guaranteed-operation.md`.
- ruff and black are clean on both changed test files.
- I checked each relaxed type against filament-core-data's construct
  enforcement (`crates/extraction-frontend/src/constructs.rs` `shape()`).
  `shape()` returns `Ok` when the type has no `construct:` declaration. None of
  the nine relaxed types (`api_endpoint`, `data_schema`, `queue`, `action`,
  `ui_component`, `external_contract`, `extension_point`, `binary_format`,
  `rate_limit`) declares a `construct:` block in `manifest.yaml`, so no
  construct requires `fields`, `operations`, `clauses`, min_clauses,
  min_operations or an identity field. A document without those keys is not
  refused with ARTIFACT_NOT_LOWERED, and the relaxation is consistent. Only
  `interface`, `part`, `port`, `connection` and `allocation` carry constructs,
  and this PR changes none of their schemas. `interface`'s construct requires
  `featureOrder` and leaves `fields`, `operations` and `clauses` optional,
  which still matches `Interface.json`.

## Verdict

**CONDITIONAL.** The schema change is correct and minimal. Item rules still
apply to a present key in both directions: TC-130 checks an empty `fields`, an
empty `clauses`, an `ApiEndpoint` with no returning operation, an
`ExternalContract` with no guaranteed operation and an `Action` with two
operations, and the FR-004 per-type tests cover queue identity and the
ui-component identity ban. FND-001 must be fixed, because the test that claims
FR-009-AC-3 and FR-009-CON-1 cannot fail for five of the nine types.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | TC-131 cannot detect a regression on `fields` or `clauses`. It intersects a schema's `required` set with the locator names in `yield_pattern.match`, but locators are named by section (`properties`, `invariants`), not by record key, so `{fields}` and `{clauses}` never intersect. Mutation check: restoring `"required": ["fields"]` in DataSchema.json and `["clauses"]` in RateLimit.json leaves TC-131 green; only TC-130's hand-kept map catches it. `Interface` is asserted by a literal. The fix is to map each record key to its source heading (`fields`→Properties, `clauses`→Invariants, `operations`→Operations, `featureOrder`→Features) through `after_heading`/`under_section`, then assert per key. | tests/test_role_schemas.py:525-537 | correct-requirement-no-evidence |
| FND-002 | low | `OPTIONAL_SECTION_KEYS` is a hand-kept table that restates FR-009 Outputs, and its object-type dict keys are never read, because only `.values()` is used. Deriving it from the manifest and the key-to-section mapping that FND-001 needs would remove the duplicate. | tests/test_role_schemas.py:496-508 | correct-requirement-no-evidence |
| FND-003 | low | The trace on TC-131 does not match the matrix. tests.md maps TC-131 to "FR-009-AC-3, FR-009-CON-1", but the test is tagged only `@pytest.mark.trace("TC-131", "FR-009-AC-3")`, so no tagged test covers FR-009-CON-1 in the computed matrix. Add `FR-009-CON-1` to the marker. | tests/test_role_schemas.py:525, spec/tests.md TC-131 | correct-requirement-no-evidence |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (0576d80). TC-131 now uses `KEY_LOCATOR` to map each record key to the locator that feeds it and asserts `(key in required) == locator.required` per type. Mutation-verified: restoring the `origin/main` `required` list in DataSchema, RateLimit, ApiEndpoint, Queue, UiComponent, BinaryFormat or ExtensionPoint, or dropping Interface's `required`, each makes TC-131 fail. |
| FND-002 | fixed | Round 1 (0576d80). `OPTIONAL_SECTION_KEYS` is deleted. TC-130 iterates `OBJECT_TYPES`/`MODEL_OF`, and the only remaining table is the key-to-locator mapping FR-009 Inputs states. |
| FND-003 | fixed | Round 1 (0576d80). The marker is now `@pytest.mark.trace("TC-131", "FR-009-AC-3", "FR-009-CON-1")`. |
