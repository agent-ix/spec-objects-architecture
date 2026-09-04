---
id: SR-009
title: "Code review — spec-objects-architecture semantic module contract (#8)"
type: SpecReview
analysis: code-review
scope: "typespec/, scripts/generate-schemas.mjs, scripts/stage-npm.mjs, spec_objects_architecture/, tests/, plan/Plan-001-semantic-data-schemas/"
review_set: subset
---
# SR-009: Code review — semantic module contract (#8)

## Summary

Reviewed the whole `spec/8-semantic-module-contract` branch diff against
`origin/main`: the TypeSpec source and the two Node build scripts, the 0.3.0
manifest, the thirty-one emitted schemas, the thirteen rewritten skeletons and
ten negative fixtures, and the sixteen-file / 164-case Python suite, together
with an implementation-gap pass over the six FRs, NFR-001, IT-002 and StR-001.
Every gate was run rather than assumed. Thirteen findings — no high, seven
medium, six low. The house-rule checks the program cares most about all pass:
no `@pytest.mark.trace` is black-wrapped, no trace id sits on a module
docstring or a plain helper, no bare TC id sits in a comment,
`conftest.require_quire` fails rather than skips, and each of the four strict
`xfail` rows names a GitHub issue that is real and OPEN.

## Verdict

**CONDITIONAL** — no high finding. Seven medium findings are partial
acceptance criteria (a tagged test asserting only half of what its criterion
states), one tautological assertion, one latent generator defect in a branch no
test reaches, a coverage gate that measures nothing the change delivers, and a
`quire coverage` status column that silently disables the complete-but-unbacked
check the matrix's own coverage claim leans on.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | FR-006-AC-1 requires "for each of those the same return **type token**"; TC-080 compares only `bool(yaml_op.get("output")) == bool(typed_op.get("returns"))`. The interface skeleton's `## Contract` fence declares `output: Bytes` and `output: Decimal(18,9)` against extracted `returns.target` values, so the token comparison is feasible and simply is not made. A fence that renamed a return type would keep the row green. | tests/test_architecture_lowerings.py:80, spec/functional/FR-006-architecture-lowerings.md | correct-requirement-no-evidence |
| FND-002 | medium | FR-005-AC-7 requires "no placeholder token **and every asserted section body is non-empty**"; TC-056 asserts the placeholder half and then only `len(body.strip()) > 200` over the whole document. No per-section emptiness is checked, so a skeleton could ship an empty `## Invariants` or `## Operations` body and pass. | tests/test_skeletons_semantic.py:239 | correct-requirement-no-evidence |
| FND-003 | medium | FR-004-AC-13 requires the placeholder target to be "accepted by the schema **and reported by the extractor as `semantic.unresolved-type`**"; TC-042 exercises the schema only. The extractor half is asserted by TC-084, which is tagged to FR-006-AC-5, so FR-004-AC-13's own row is backed by half its criterion. | tests/test_role_schemas.py:276, tests/test_architecture_lowerings.py:145 | correct-requirement-no-evidence |
| FND-004 | medium | Tautological assertion. TC-091's `assert len(ids) == len(set(ids))` cannot fail: the `bundle_index` fixture it reads already de-duplicates by `front["id"]` with a `seen` set before the test sees the list. The companion `len(ids) == len(OBJECT_TYPES)` is real; the uniqueness half tests the fixture, not the module. | tests/test_consumer_boundaries.py:110, tests/conftest.py:203 | correct-requirement-no-evidence |
| FND-005 | medium | Latent generator defect in an untested branch. `normalize()` treats every `$ref`/`$id` value not matching `/^https?:\/\//` as a bare file name, so a fragment ref (`#/$defs/Foo`) or a file-plus-fragment ref (`Foo.json#/$defs/Bar`) would be rewritten to `https://schemas.agent-ix.org/semantic-core/0.1.0/#/$defs/Foo` — a wrong, silently-emitted URI. It cannot fire today (`toolchain.json` records `applied: false`), and no test reaches the branch at all, so the day the emitter emits a relative ref this ships corrupt `$ref`s and TC-012 accepts them (it only checks the semantic-core prefix). | scripts/generate-schemas.mjs:118 | correct-requirement-no-evidence |
| FND-006 | medium | The coverage gate measures nothing this change delivers. `--cov=spec_objects_architecture --cov-fail-under=100` reports 4/4 statements on `__init__.py`; the 319-line generator that is the actual implementation of FR-002 has no coverage measurement, and five of its error branches have no test: `requireNode()` (Node < 20), `dependencyVersion()` (toolchain not installed), the `tsp compile` failure path, `mine.length === 0` (emitted no module model), and `manifestWithDigests`'s "manifest references schemas/X, which is not emitted". Four of those are FR-002 Behavior statements. | pyproject.toml:127, scripts/generate-schemas.mjs:54, scripts/generate-schemas.mjs:161 | correct-requirement-no-evidence |
| FND-007 | medium | `quire coverage` emits `[status-column-matches-nothing]`: the Functional Requirement Coverage table in `spec/tests.md` has a `Coverage Status` column while `traceability.status.column` is configured as `Status`, so "Status classification was skipped, so complete-but-unbacked rows could not be checked". The Coverage Gaps section nonetheless asserts "`quire coverage` reports every declared row backed". The 130/130 backed figure is real; the complete-but-unbacked check behind the claim is disabled. | spec/tests.md:66, spec/tests.md:204 | correct-requirement-no-evidence |
| FND-008 | low | `manifestWithDigests` leaks `pending` across lines: a `schema: schemas/X` line with no following `digest:` line before the next `schema:` line silently updates nothing, and any unrelated `digest:` key appearing after a `schema:` line would be overwritten with that schema's hash. Today the manifest has no such shape and FR-003-AC-2's Python test catches a missing digest, so the exposure is latent. | scripts/generate-schemas.mjs:216 | missing-requirement |
| FND-009 | low | `pytest.raises(Exception)` in TC-026's refusal loop is broad enough to pass on a `TypeError` from the call signature itself, not only on the load refusal it means to observe. The strict-xfail companion row (`test_the_refusal_names_the_offending_key_and_path`) has the same shape, which is why it can only assert on `str(error.value)`. | tests/test_manifest_semantic.py:172, tests/test_manifest_semantic.py:195 | correct-requirement-no-evidence |
| FND-010 | low | TC-071 mutates the live repository root: `npm pack` runs `prepack` staging into `REPO_ROOT`, and the test's `finally` unconditionally `rmtree`s repo-root `manifest.yaml`, `schemas/` and `skeletons/`. An interrupted run leaves the staged payload behind, which is exactly the failure mode the test exists to catch (a root `manifest.yaml` makes every Filament tool discover a second module). The staged paths are gitignored, so nothing else would notice. | tests/test_schema_emission.py:264 | missing-requirement |
| FND-011 | low | FR-002-AC-6 names "the wheel built by `make build`"; TC-015 shells `poetry build` directly. The `build-tools build` path the criterion names is never exercised, so a `build-tools` regression that dropped `schemas/*.json` would leave the row green. | tests/test_schema_emission.py:174, spec/functional/FR-002-emitted-json-schemas.md | correct-requirement-no-evidence |
| FND-012 | low | FR-005-AC-5 requires "at least the ten cases listed in Behavior are present"; TC-054 asserts `len(fixtures) >= 10` and that all four expected diagnostic codes are seen, but pins none of the ten named cases by name. Deleting `queue-no-identity-row.md` and duplicating another `semantic.record-invalid` fixture would still pass. | tests/test_skeletons_semantic.py:173 | correct-requirement-no-evidence |
| FND-013 | low | TC-027 and TC-070 are `✅` in the matrix but skip in `make test`: both are gated on `QUOIN_INSTALL_ROUNDTRIP=1` because they write the operator's global `quoin module` store. The evidence is a manual run recorded in tests.md prose against quoin `0.23.1-2-g3e842ce`, which does match the quoin on this machine — so the claim checks out — but FR-003-AC-5 and all six IT-002 scenarios have no gate that re-verifies it. This is a Demonstration by declaration, not a skipped row masquerading as coverage, and it is documented as such. | tests/test_quoin_install_roundtrip.py:30, spec/tests.md:183 | correct-requirement-no-evidence |

## Gates Run

| Gate | Result |
|---|---|
| `make lint` (ruff + black + `schemas-check`) | pass — all checks passed, 31 schemas match the committed output |
| `make test` | pass — 153 passed, 7 skipped, 4 xfailed in 42.6s, coverage 100% (`--cov-fail-under=100`) |
| `quire validate --scope . "spec/**/*.md"` | pass — zero errors |
| `quire validate --scope . "plan/**/*.md"` | pass — zero errors |
| `quire coverage` | 130/130 rows backed (100%); `spec/tests.md` 71/71; one `status-column-matches-nothing` warning (FND-007) |
| `node scripts/generate-schemas.mjs --check` | pass on the committed tree |
| `poetry build` / `npm pack` | exercised by TC-015 and TC-071 |
| GitHub issue check on every `xfail` and skip reason | all nine referenced issues exist and are OPEN |

## Language Dispatch

Python (`pyproject.toml`, sixteen `tests/*.py`) plus two Node build scripts and
one TypeSpec source. No Rust and no React in the change, so those lanes do not
apply. The repo's own idiom — module-level `test_*` functions carrying
`@pytest.mark.trace(...)`, not `TestFeature` classes — was followed and
outranks the generic "leverage test classes" rule, matching the pre-existing
`tests/test_manifest.py` and `tests/test_skeletons_and_validate.py`.

## Test Standards

Trace tags: 84 `@pytest.mark.trace(...)` markers across nine files, **every one
on a single line** — the black-wrapping defect of `agent-ix/quire-rs#395` is
absent. No trace id appears on a module docstring or a non-test helper, and no
bare `TC-NNN` appears in a comment where it would bind to the next symbol. Two
markers stack a second id set onto one test (`TC-004`/`TC-005`,
`TC-001` repeated across three rows) but always inside one call, never as two
stacked decorators.

Engine dependency: `tests/conftest.py::require_quire` calls `pytest.fail`, not
`pytest.skip`, both when `import quire` raises and when `extract_semantic` is
absent, and the message names `make dev-quire` and `agent-ix/quire-rs#392`.
`schema_registry` likewise fails when `@agent-ix/semantic-core` is not
installed. The `minijinja-cli` generator row (TC-006) fails rather than skips
when the binary is absent. This is the policy the ticket asks for and it is
implemented exactly.

Expected failures: four strict `xfail` rows, each naming a real OPEN issue —
`agent-ix/filament-core-service#25` (FR-035 refuses the top-level `lexicon`),
`agent-ix/quire-rs#391` (a legacy form declaring `object:` validates as `{}`),
`agent-ix/quire-rs#221` + `#394` (module-load refusal names nothing), and
`agent-ix/quire-rs#398` (a per-file bundle index reports a declaration
ambiguous with itself). None hides a defect this module could fix: all four are
engine or neighbouring-service behaviour, no schema is relaxed to make them
green, and the module's own bundle index is built by id, which is the correct
construction.

Mock compliance: the suite uses no `mocker`, no `unittest.mock` and no
`@patch`. Every row runs the real engine, the real generator subprocess, real
`poetry build` / `npm pack`, or the shipped bytes. There is no mock at any
boundary, correct or otherwise.

Skips: seven, in two gated groups — four on `FILAMENT_CORE_URL` (FR-001-AC-2..4,
IT-001, StR-001-VC-1; carried as `🚧` in the matrix, pre-existing debt from
issue #1) and three on `QUOIN_INSTALL_ROUNDTRIP` (FND-013). No skip is
tagged to a row the matrix reports `✅` without saying so in the row note.

## Completeness

No `TODO`, `FIXME` or `XXX` in `typespec/`, `scripts/`, `spec_objects_architecture/`
or `tests/`. No stub module, no `pass`-bodied test, no import-only test, no
empty class. The one `# pragma: no cover` pair sits on genuinely unreachable
environment guards in the test tree (a detached clone with no `origin/main`, a
machine with no prior quoin module entry) and suppresses nothing, since
coverage is scoped to `spec_objects_architecture/` — see FND-006 for the real
problem with that scoping.

## Spec-Code Faithfulness

The manifest, the thirty-one emitted schemas and the thirteen skeletons match
what FR-002 through FR-006 state, with the three partial-criteria exceptions
recorded as FND-001, FND-002 and FND-003. Spot checks that hold: the `semantic`
block carries exactly the nine admitted keys; every exported type is in
reference form with a digest equal to the shipped bytes; every added
`body_extraction` locator is `required: false`; `Identifier`, `SemanticId`,
`FieldDecl`, `OperationDecl`, `ClauseRef` and `RelationDecl` are `$ref`'d to
semantic-core and never redeclared; every model is sealed with
`unevaluatedProperties: {"not": {}}`; and `UiComponent` forbids an identity prop
through `contains` + `maxContains: 0` rather than by omitting the check.

The FR-004 reader rules JSON Schema cannot express (`RouteDecl.operation`
naming a sibling operation, `LayoutField.size` naming a sibling field) are
declared as reader rules in the TypeSpec doc comments and are explicitly not
claimed as schema refusals — correctly scoped, not a gap.
