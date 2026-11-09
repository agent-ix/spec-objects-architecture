---
id: SR-010
title: "Code review — FR-008 record-key sections (PR #41)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; PR #41 diff origin/main...0d8c4af: spec_objects_architecture/manifest.yaml, spec_objects_architecture/skeletons/, spec_objects_architecture/schemas/LayoutField.json, typespec/main.tsp, tests/, pyproject.toml, poetry.lock"
review_set: subset
---
# SR-010: Code review — FR-008 record-key sections (PR #41)

## Summary

Ticket: PLAT-196 (also PLAT-201). Reviewed the manifest mapping tokens and
`section_body` locators, the seven rewritten skeletons, the hand-edited
`LayoutField.json`, `typespec/main.tsp`, `tests/test_record_sections.py`, the
conftest fixtures and the converted negative fixture, against quoin FR-121 and
FR-122 (quoin `origin/main`) and quire-rs FR-081 (merged as `4b744c6`).

The suite was run against a `quire` wheel built from quire-rs `origin/main`
(0.54.0 + FR-081) and the real semantic-core 0.3.3 JSON schemas taken from the
`semantic-core-v0.3.3` tag of `agent-ix/filament-core-data` (not a stand-in):
10 failed, 260 passed, 7 skipped, 1 xfailed. Seven failures are
`test_schema_emission.py` (no TypeSpec toolchain in the review worktree), two are
the engine drifts the PR body names, and one is new:
`test_each_skeleton_authors_its_record_keys_and_they_validate[interface]`.

## Verdict

**NOT MERGEABLE.** Two high findings block merge. TC-121 fails for `interface`
against the published semantic-core 0.3.3, because the engine emits a `TypeRef`
target in the adjacent `{kind, value}` form that only unreleased
filament-core-data `main` defines. With the locked `quire` 0.52.0, every
FR-008 test fails, and fails rather than skips (`require_quire` is designed that
way), so merging turns `main` red. Two medium skeleton values name the wrong
declaration.

Verified clean: the manifest names `relationships` and `record-sections`, and
every H2 of the seven skeletons has exactly one locator with the right
`required` flag (`Routes`, `Delivery`, `Provider`, `Versioning`, `Exposes`,
`Associated Types` are optional `section_body`). The Thresholds, Registration
and Stability tables match FR-122's headers and cell grammar. `associated_types`
is removed from the `## Contract` fence and appears only in the table. The
`LayoutField.json` description was regenerated in a scratch dir with `tsp
compile` (@typespec/json-schema from the main checkout's `node_modules`) and
matches the hand edit byte for byte. The rest of that file differs only by the
semantic-core base, which comes from the older local install (0.3.0). Decision
#20's reversal is consistent in FR-008, the manifest comment and the
`api_endpoint` skeleton.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | TC-121 fails for `interface` against the real published semantic-core 0.3.3. The engine extracts `associated_types[0].target` as `{"kind": "KernelScalar", "value": "Bytes"}`, but `TypeRef.json` at tag `semantic-core-v0.3.3` declares `target` as `anyOf[SemanticId, KernelScalar]` (bare strings), so the value is invalid against the module's own `Interface.json`. The adjacent wire form comes from filament-core-data `main` (IR-994, `7e6f209e`, after the tag), which still calls itself 0.3.3. The PR body's "locally patched `TypeRef`" hid this. FR-008-AC-2 is not met with the declared dependency. Unblock: release semantic-core with the adjacent form under a new version and bump the module to it, or get the engine to emit the published form. | tests/test_record_sections.py:109-125, spec_objects_architecture/manifest.yaml (semantic_core 0.3.3), package.json | correct-requirement-no-evidence |
| FND-002 | high | The `quire` dev dependency is `^0.52.0`, locked at 0.52.0, which predates FR-081 (merged after v0.54.0 and not released). `require_quire` fails rather than skips, so every `test_record_sections.py` row fails under the locked environment and `main` goes red on merge. FR-008's own Dependencies say "the `quire` dev dependency must carry them". Bumping to an FR-081 build also fails `test_consumer_boundaries.py::test_a_per_file_bundle_index_does_not_make_a_declaration_ambiguous_with_itself` and `test_manifest_semantic.py::test_underscore_and_hyphenated_frontmatter_ids_validate` (reproduced), so those two need adapting in this PR. This blocks merge: it needs a quire-rs release carrying FR-081, then `poetry lock` run by the tool (not a hand edit), in this PR. | pyproject.toml:34, poetry.lock:934-935, tests/conftest.py:273-283 | missing-requirement |
| FND-003 | medium | The `external_contract` skeleton's `## Provider` is `` `api_endpoint_001` ``, which is `ArtifactUploadEndpoint`, the module's internal artifact upload endpoint. The contract is `IdentityServiceContract`, and its prose says the Identity service, an external system, provides it. The value is semantically wrong, and the skeleton is the authoring template agents copy. TC-121 also pins this wrong value. Name an identity-service declaration instead, such as a bare `identity_service` that resolves to the FR-104 `unresolved` placeholder as an advisory rather than an error. | spec_objects_architecture/skeletons/external_contract.md:44-46, tests/test_record_sections.py:138 | wrong-requirement |
| FND-004 | medium | The `extension_point` skeleton's `## Exposes` is `` `quant_codec` `` (`QuantCodec`, a vector quantisation codec), and the `## Contract` prose was edited to say the `RendererRegistry` interface is "`quant_codec` in this skeleton set". That is false: a renderer registry is not a codec, and the edit writes the false identity into the prose. TC-121 pins it. Use a `renderer_registry` id, which resolves as an unresolved-target advisory, and restore the prose. | spec_objects_architecture/skeletons/extension_point.md:36-43, tests/test_record_sections.py:139 | wrong-requirement |
| FND-005 | low | In the `extension_point` `## Registration` row, the `Discovery` cell holds a fallback rule ("unregistered types fall back to the generic payload renderer"), not a discovery mechanism. The conversion also dropped the "duplicate registrations log a warning" guarantee without a home. | spec_objects_architecture/skeletons/extension_point.md:49-51 | implementation-bug-despite-evidence |
| FND-006 | low | The `tests/test_architecture_lowerings.py` module docstring still names `agent-ix/quoin#335` as the engine-side mapping, which FR-122 now owns. | tests/test_architecture_lowerings.py:7 | implementation-bug-despite-evidence |

## Gates Run

- `pytest -o addopts=""` over `tests/`, with a quire wheel built from quire-rs `origin/main` (`4b744c6`) and the semantic-core 0.3.3 JSON schemas from the `semantic-core-v0.3.3` tag: 10 failed, 260 passed, 7 skipped, 1 xfailed.
- `tsp compile typespec/main.tsp` into a scratch dir: the `LayoutField` description is byte-identical to the committed edit.
- Not run: `make schemas-check` (the private npm registry returns 401) and the full `make ci`.

## Language Dispatch

Python and Markdown only. No Rust, no React lane.

## Test Standards

The `@pytest.mark.trace` tags sit on test functions. `require_quire` fails
rather than skips. No mocks. Records are extracted by the real engine, not
hand-built.

## Dispositions

| FND | Outcome | Reason |
|---|---|---|
| FND-001 | deferred | Release-blocked, not fixed. It needs a `@agent-ix/semantic-core` release (above 0.3.3) whose `TypeRef.target` takes the adjacent `{kind, value}` form already on filament-core-data `main` (IR-994, `7e6f209e`), plus a module `semantic_core` bump. Re-checked on `7b21aef` against the published 0.3.3 schemas: TC-121[interface] still fails. FR-008 Dependencies now name the blocker (d24396c). It still blocks merge, because merging makes `main` red. |
| FND-002 | deferred | Release-blocked, not fixed. It needs a quire-rs release carrying FR-081 (merged as `4b744c6`, after v0.54.0), then `poetry lock` by tooling in this PR. On bump, `test_consumer_boundaries::test_a_per_file_bundle_index_does_not_make_a_declaration_ambiguous_with_itself` and `test_manifest_semantic::test_underscore_and_hyphenated_frontmatter_ids_validate` still fail on `7b21aef` (reproduced) and must be adapted in the same change. FR-008 Dependencies now name the blocker (d24396c). It still blocks merge. |
| FND-003 | fixed | d24396c: `## Provider` is `` `identity_service` ``, and TC-121 asserts `ix://agent-ix/spec-objects-architecture/identity_service` with zero errors (passes on a FR-081 build). |
| FND-004 | fixed | d24396c: `## Exposes` is `` `renderer_registry` ``, the Contract prose is restored to its pre-PR text, and TC-121 pins `renderer_registry` (passes). |
| FND-005 | fixed | d24396c: the Discovery cell is now the registration call and the duplicate-registration warning, so the dropped guarantee is restored. |
| FND-006 | fixed | d24396c: the docstring names quoin FR-122 (quire-rs FR-081). |
