---
id: SR-007
title: "Evidence review of the #8 semantic module contract spec set"
type: SpecReview
analysis: evidence
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-declare-architecture-objects-against-semantic-core.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-emitted-json-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-005-executable-skeletons.md, spec/functional/FR-006-architecture-lowerings.md, spec/non-functional/NFR-001-additive-compatibility.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-quoin-module-install.md, spec/tests.md"
review_set: all
---
# SR-007: Evidence review of the #8 semantic module contract spec set

## Summary

Every `Verification` cell in FR-001..FR-006, every `Validation` cell in the
constraint and StR-001 tables, every NFR-001 `Method` cell, and every Test
Matrix `Type` was checked against the declared catalog
(`spec-artifacts-process/manifest.yaml`: 33 method ids across the classes
`Test`, `Analysis`, `Inspection`, `Demonstration`; matrix `Type` vocabulary
`Unit | Integration | E2E | Property | Fuzz | Benchmark | Static | Compile |
Snapshot | Manual | Eval | Inspection | Analysis | Demonstration`; matrix
`Status` pattern `^(✅|❌|🚧|⛔)(\s+.*)?$`, in which `⚠️` is not admitted —
`agent-ix/quoin#337`). No cell in this spec set uses `⚠️`, and no `Type` or
`Priority` value is outside the archetype vocabulary; `Static` and `Manual`
are both legal, so the divergence from the sibling's `Inspection`/
`Demonstration` typing is a naming question, not a validation failure.

`quoin advise` was run over the 59 obligations `quire coverage --json`
derives (54 acceptance criteria, 5 NFR-001 measurement rows): **1 mismatch, 4
uncatalogued, 0 inconclusive**. Unlike the sibling, this review is run against
a landed implementation (commit `92d8355`), so the matrix's status column is
checkable rather than aspirational.

What the engine found on its own: the four FR-001 cells (`Schema Test`,
`Integration Test`) are strings no catalog entry or class declares
(`uncatalogued-verification-method`); FR-003-AC-5 is authored `Demonstration`
against a criterion with an exit-code oracle; three trace ids on an untracked
test file (`FR-003-AC-8`, `FR-005-CON-3`) are not minted trace targets; and
status classification of the `Functional Requirement Coverage` table was
**skipped** because its header is `Coverage Status` while the module
configures `traceability.status.column: Status`.

What running the suite adds, and what judgement adds: `poetry run pytest`
reports **152 passed, 7 skipped, 4 xfailed** over 77 `mark.trace` symbols
binding 126/126 matrix rows (100%). Every ✅ row does have a test bearing its
TC id — there is no unbacked ✅ row — but three rows are green over evidence
that does not discharge them. TC-001 is ✅ while the test that asserts its
criterion is a strict `xfail`; TC-058 is ✅ over three assertions that cannot
fail in this repository; and TC-006 is tagged to a test that runs no
generator. Separately, the environment invalidates two 🚧 notes: quoin
`0.23.1-2-g3e842ce` with the semantic installer *is* on `PATH` and its
`module install` understands `path:`, so "needs a Quoin built from main" is a
stale blocker — the real gate is the `QUOIN_INSTALL_ROUNDTRIP=1` opt-in over
the operator's global store, which `--config-root` / `IX_CONFIG_ROOT` can
remove. `quire` 0.46.0 with `extract_semantic` is present and all 13
skeletons validate and extract, so no Quire row is environment-blocked.

The advisor's `property-based-testing` on 24 criteria is the `universal`
catch-all (quire reports `catch-all-universal` for 8 of 8 documents), and its
`dast`/`iast`, `fuzzing` and `demonstration` hits are characteristic misreads;
those are recorded as residue, not followed. No `fault-detection-*`
characteristic minted, so `mutation-testing`/`concolic-execution` were
correctly recommended for nothing — but with 77 bound symbols and a populated
evidence store, mutation measurement is now the cheap escalation this module
could not run at spec time.

## Verdict

**Revise the three green-over-nothing rows and the four uncatalogued FR-001
cells; the rest of the matrix is the strongest in the family.** 54 of 59
obligations carry a declared class the advisor agrees with at class level,
every acceptance criterion, named constraint and NFR criterion has a matrix
row, every row is backed by a tagged test, and the module carries its three
declared expected failures as strict xfails rather than skips. The blocking
items are FND-400 (a ✅ over a strict xfail, undeclared anywhere), FND-401 and
FND-402 (two ✅ rows whose evidence cannot discharge the criterion), and
FND-403 (the four uncatalogued cells the sibling already fixed and this module
did not). FND-405 is uncommitted work that must be reconciled before merge.

Counts: 3 high, 6 medium, 7 low.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|----|----------|---------|------|--------------|
| FND-400 | high | TC-001 is `✅` but the test that asserts FR-001-AC-1 — `test_the_manifest_validates_against_the_pinned_fr035_schema` — is a `strict=True` xfail on `agent-ix/filament-core-service#25`: the manifest does **not** validate against the pinned FR-035 schema, because FR-035 is `additionalProperties: false` and admits no `lexicon`. Two sibling tests under the same TC id (digest pin, "the only violation is `lexicon`") pass and carry the row's green. Nothing in the matrix declares this: the TC-001 row has no note, the FR-001 coverage row notes only "AC-2..AC-4 need a running filament-core", and `Test Environment` states "The one exception is TC-061" while three xfails exist (TC-001, TC-026, TC-061). Mark TC-001 `✅` with the expected-failure note the peer rows carry, or `🚧` naming filament-core-service#25. | FR-001-AC-1, TC-001, TM-001 | correct-requirement-no-evidence |
| FND-401 | high | StR-001-VC-2 ("agent CLI generators (minijinja-cli) can produce valid artifacts using the templates and schemas this module ships") is authored `Demonstration`, typed `Manual`, `🚧 needs a generator run`. Its tagged test, `test_a_generator_produces_an_artifact_that_validates_against_the_shipped_module`, invokes no generator at all: it reads `skeletons/api_endpoint.md` and calls `validate_document` on it. It is also gated on `FILAMENT_CORE_URL`, which a generator run does not need, so the row's own note ("needs a generator run") and its actual gate ("needs a running filament-core") disagree. The criterion's evidence — an artifact produced by minijinja-cli from a shipped skeleton — does not exist in this repository, and the tag makes it look like it nearly does. Either drive `minijinja-cli` over a skeleton and assert the product validates, or discharge VC-2 through an inspections registry and drop the tag. | StR-001-VC-2, TC-006 | correct-requirement-no-evidence |
| FND-402 | high | FR-005-CON-1 ("editing no corpus repository and no vendored quoin/quire fixture") is authored `Inspection`, typed `Static`, `✅` via TC-058. The test diffs `origin/main...HEAD` **of this repository** and asserts no changed path starts with `corpus/`, contains `fixtures/semantic-module`, or contains `/vendor/`. This repository contains none of those directories (verified: 115 changed paths, all under `spec/`, `spec_objects_architecture/`, `scripts/`, `tests/`, `typespec/` and build files), so all three assertions are vacuous and the row cannot go red. The constraint's actual subject is *other* repositories, which a diff of this one can never observe. This is the evidence-cannot-exist-here case: recommend `inspection` discharged through an Inspections registry (which does not exist — FND-406), or narrow CON-1 to a claim this repo can falsify. | FR-005-CON-1, TC-058 | correct-requirement-no-evidence |
| FND-403 | medium | The four FR-001 `Verification` cells are `Schema Test` (AC-1) and `Integration Test` (AC-2..AC-4) — strings that are neither a catalog method id nor a class, so quire reports `uncatalogued-verification-method` twice and nothing can say what discharging them means. Recommend `unit-testing` (Unit) for AC-1 — `quire.validate_manifest` against a vendored schema pinned by digest is one component against a fixed oracle — and `integration-testing` (Integration) for AC-2..AC-4, which cross a real HTTP boundary into filament-core. `contract-testing` is the stronger reading of AC-1 if the schema is ever fetched rather than vendored; that is judgement, not a rule match. The sibling module raised this as FND-160/FND-161 and applied the fix (`Test`); this module inherited the unfixed cells from the issue-#1 era and did not. | FR-001-AC-1, FR-001-AC-2, FR-001-AC-3, FR-001-AC-4, IT-001, TC-001, TC-002, TC-003, TC-004 | wrong-requirement |
| FND-404 | medium | FR-003-AC-5 is the advisor's one mismatch: authored `Demonstration`, recommended `unit-testing`/`bdd-spec-by-example` on the `example` shape. The criterion has a fully executable oracle (exit code 0, listing contains the name, prior entry restored) and IT-002 writes it as a five-step CLI procedure. Its rows TC-027 and TC-070 are `Manual`, `🚧 needs a Quoin built from quoin main ≥ 3e842ce (no release carries it)` — but the installed quoin is `0.23.1-2-g3e842ce` and its `module install` accepts `path:`, so that blocker no longer holds. The real gate is `QUOIN_INSTALL_ROUNDTRIP=1`, imposed because the install mutates the operator's global module store — and `quoin` accepts `--config-root` / `IX_CONFIG_ROOT`, so a `tmp_path` config root removes the gate entirely. Recommend `integration-testing` (Integration) against an isolated config root, which turns three 🚧 rows green and discharges IT-002 for real. At minimum, correct the stale blocker text. | FR-003-AC-5, IT-002, TC-027, TC-070 | wrong-requirement |
| FND-405 | medium | `tests/test_consumer_boundaries.py` is **untracked** at commit `92d8355` and traces to ids that exist nowhere: `FR-003-AC-8` (FR-003 mints AC-1..AC-7), `FR-005-CON-3` (FR-005 declares CON-1..CON-2), `TC-090` and `TC-091` (no matrix rows). quire reports three `untracked-id-has-minted-children` diagnostics and six "matches no declared row" lines for it. It also carries a **fourth** strict xfail, on `agent-ix/quire-rs#398` (`semantic.ambiguous-type` naming the same id on both sides), beyond the three expected failures the spec set declares — so the suite's xfail census (4) already exceeds the specification's (3). Either author FR-003-AC-8, FR-005-CON-3 and the two TC rows, or drop the file; leaving it uncommitted means the matrix and the tree disagree about what is verified. | FR-003, FR-005, TM-001 | missing-requirement |
| FND-406 | medium | Four constraint cells are authored `Inspection` — FR-002-CON-1, FR-002-CON-2, FR-002-CON-4, FR-005-CON-1 — and all four are `✅` via tagged pytest symbols (TC-017 `Static`, TC-018 `Static`, TC-019 `Unit`, TC-058 `Static`). The catalog's `inspection` is `[Inspection] → Manual` and explicitly "produces no source symbol, so it is discharged through the inspections registry rather than by a tagged test"; quire reports `archetype-matches-nothing` for both `Inspections` and `SuiteRegistry`, and `tests.md` Coverage Gaps admits neither document exists. So four rows are green on an evidence kind their authored method cannot produce. Three of the four have executable oracles and should be retyped: FR-002-CON-2 and FR-002-CON-4 → `unit-testing` (Unit) over `package.json`/`package-lock.json`; FR-002-CON-1 → `sast` or `architecture-conformance` (Analysis → Static), which is what TC-017 actually does (it greps `scripts/generate-schemas.mjs` and re-runs the drift gate). FR-005-CON-1 is the one that genuinely needs the registry (FND-402). | FR-002-CON-1, FR-002-CON-2, FR-002-CON-4, FR-005-CON-1, TC-017, TC-018, TC-019, TC-058 | wrong-requirement |
| FND-407 | medium | `IT-002-SC-02`, `SC-03`, `SC-04` and `SC-05` each "match no declared row" per `quire coverage`, although tests carry all six ids. TC-070's `Traces To` cell uses the range form `IT-002-SC-01..IT-002-SC-06`, and the engine reads a range as its two endpoints, not as an expansion — so four of the six success criteria have a tagged symbol and no declaring row. The `Integration Test Coverage` table names `IT-002-SC-01..06` but is not a minting surface. Enumerate the six ids in the `Traces To` cell, or split TC-070 into rows that name them. IT-001-SC-01..03 are unaffected: TC-002..TC-004 name them individually. | IT-002, TC-070, TM-001 | correct-requirement-no-evidence |
| FND-408 | medium | `status-column-matches-nothing`: the `Functional Requirement Coverage` table's header is `Coverage Status` while the module configures `traceability.status.column: Status`, so quire skipped status classification for that table and complete-but-unbacked rows could not be checked there. This is the layer that would have caught FND-400 automatically. The `Test Case Summary` table does carry `Status` and was classified. The sibling recorded the same diagnostic (FND-169) and declined it as a process-module configuration question; with a landed implementation the cost is now concrete — a status lie in the requirement-level table is invisible to the engine. | TM-001 | correct-requirement-no-evidence |
| FND-409 | low | NFR-001-M-1..M-5 are obligations (`quoin advise` derives all five) but no matrix row bears their ids: TC-060..TC-064 trace to NFR-001-AC-1..AC-5, which mirror the five metrics 1:1, and the `Non-Functional Requirement Coverage` table names only the AC range. The coverage is real; the id trace is not authored, and the Overview's claim that "every NFR metric maps to at least one test case" is true only by that mirroring. Separately the advisor recommends `performance-benchmarking` on `quantified-threshold` for all five — a rule misfire, since the targets are `0`, `1` and `identical` counts, not latency or throughput. Judgement: M-1 and M-4 are baseline diffs against checked-in bytes → `golden-approval-testing` (Snapshot); M-2, M-3, M-5 exercise Quire against the module → `integration-testing` (Integration). | NFR-001, TC-060, TC-061, TC-062, TC-063, TC-064 | wrong-requirement |
| FND-410 | low | StR-001-VC-1 is authored `Inspection`; TC-005 is typed `Manual`; and both are discharged by `test_every_declared_contribution_is_readable_from_the_registry_endpoints`, an automated pytest that also carries TC-004/FR-001-AC-4 and is gated on `FILAMENT_CORE_URL`. `Inspection` is for `judgement-required, no-executable-oracle` and this has an oracle; `Manual` is a no-source-symbol type and this has a symbol. The StR's own prose says satisfaction "is judged by demonstrating all three outcomes". Recommend `demonstration` (Demonstration → Manual) if the witnessed-run reading is kept — which is what the sibling settled on for its TC-005 — or, more honestly, drop TC-005 and let TC-004 carry both ids as `integration-testing`. | StR-001-VC-1, TC-005, TC-004 | wrong-requirement |
| FND-411 | low | StR-001-VC-3 is authored `Demonstration` but TC-007 is typed `Unit` and is `✅`: `test_an_api_endpoint_and_a_rate_limit_record_are_distinguishable_by_schema_alone` runs four schema validations over two in-memory records. That is `unit-testing` (Unit), not a demonstration, and the criterion is the one StR-001 criterion this repo can fully discharge on its own. Author `Test` in the VC table. | StR-001-VC-3, TC-007 | wrong-requirement |
| FND-412 | low | FR-006-CON-2 is authored `Test` while TC-086 is typed `Static`, and the test is an AST walk over `tests/test_architecture_lowerings.py` asserting the only engine attributes reached are `extract_semantic` and `extract`. The catalog method for that is `sast` (Analysis → Static): source examined without executing the subject. The authored class and the matrix `Type` disagree, and `Static` is the correct half. The same reading applies to TC-017 (FND-406). | FR-006-CON-2, TC-086 | wrong-requirement |
| FND-413 | low | Advisor residue, recorded as judgement and not as verdict (ADR-0010). Misfires not to follow: `property-based-testing (universal)` on 24 criteria — the catch-all, and quire reports `catch-all-universal` for 8 of 8 documents, so it advises nothing; `dast`/`iast`/`negative-abuse-testing (security)` on FR-005-AC-7 (a skeleton having no placeholder token) and FR-006-AC-5 (an unresolved-type finding); `demonstration (stakeholder-acceptance)` on FR-004-AC-13; `fuzzing (parser)` on FR-003-AC-7 and FR-006-AC-1..3; `model-checking`/`runtime-monitoring (temporal)` on FR-002-AC-8, which is a build procedure, not a temporal property. Refinements worth taking: `golden-approval-testing` (Snapshot) for FR-003-AC-7, FR-006-AC-6, NFR-001-AC-4 and FR-002-CON-3 — all four are byte-identity against a checked-in baseline; and `metamorphic-testing` (Property) for FR-006-AC-1..AC-3, which assert a relation between two derivations of one artifact and have no independent oracle, and for FR-001-AC-3, which is idempotence. | FR-002-AC-8, FR-003-AC-7, FR-004-AC-13, FR-005-AC-7, FR-006-AC-1, FR-006-AC-2, FR-006-AC-3, FR-006-AC-5, FR-006-AC-6, NFR-001-AC-4, FR-002-CON-3, FR-001-AC-3 | wrong-requirement |
| FND-414 | low | `tests.md` Coverage Gaps describes the plan as authored, not the tree as landed: it names TC-005, TC-006, TC-017, TC-018, TC-027, TC-058, TC-070 and TC-086 as `Static`/`Manual` rows that "no `Inspections` document exists to discharge", but all eight now carry tagged pytest symbols and four of them (TC-017, TC-018, TC-058, TC-086) are `✅` on that basis. The paragraph should say which rows still need the registry after implementation — on this review's reading, only FR-005-CON-1/TC-058 (FND-402) and StR-001-VC-2/TC-006 (FND-401) genuinely do. | TM-001, TC-017, TC-018, TC-058, TC-086 | correct-requirement-no-evidence |
| FND-415 | low | Binding hygiene: `marker-form-mismatch` — `test_the_020_lexicon_block_is_byte_identical_at_030` (`tests/test_manifest_semantic.py:116`) carries an id in its own declaration name that no declared name form read, and `coverage.self_named_binding.python` therefore published a `hollow-denominator` (1 walked, 0 read). The symbol is separately bound by its `mark.trace("TC-028", "FR-003-AC-7")`, so no row is unbacked; the name is the noise. Rename it so it does not look like a self-named tag. | TM-001, TC-028 | correct-requirement-no-evidence |

## Method recommendations per obligation

Only obligations whose authored method should change or be sharpened are
listed. The 46 acceptance criteria authored `Test` whose advisor
recommendation is a `Test`-class method match at class level and need no edit;
`Test` is what `quire coverage` reads.

| Obligation | Authored | Advisor | Recommended | Basis |
|---|---|---|---|---|
| FR-001-AC-1 | Schema Test (uncatalogued) | unit-testing, bdd-spec-by-example | `unit-testing` | rule + judgement; `contract-testing` if the FR-035 schema is fetched rather than vendored |
| FR-001-AC-2 | Integration Test (uncatalogued) | unit-testing, bdd-spec-by-example | `integration-testing` | judgement: real HTTP boundary into filament-core |
| FR-001-AC-3 | Integration Test (uncatalogued) | unit-testing, bdd-spec-by-example | `integration-testing`, `metamorphic-testing` noted | judgement: idempotence relation over two POSTs |
| FR-001-AC-4 | Integration Test (uncatalogued) | property-based-testing (catch-all) | `integration-testing` | judgement: registry reads after activation |
| FR-003-AC-5 | Demonstration | unit-testing, bdd-spec-by-example (**mismatch**) | `integration-testing` | rule + judgement: exit-code oracle; `--config-root` isolates the store the Demonstration was chosen to protect |
| FR-003-AC-7 | Test | fuzzing (misfire), golden-approval-testing | `golden-approval-testing` | rule: `stable-output`, byte-identical lexicon vs baseline |
| FR-006-AC-1..AC-3 | Test | fuzzing (misfire), bdd-spec-by-example | `metamorphic-testing` | judgement: relation between two derivations of one artifact, no independent oracle |
| FR-006-AC-6 | Test | golden-approval-testing, unit-testing | `golden-approval-testing` | rule: byte-identical locator definitions |
| FR-002-CON-1 | Inspection | not an obligation (constraint) | `sast` / `architecture-conformance` | judgement: TC-017 reads source and re-runs the drift gate |
| FR-002-CON-2, CON-4 | Inspection | not an obligation (constraint) | `unit-testing` | judgement: executable oracle over `package.json` / `package-lock.json` |
| FR-002-CON-3 | Test | not an obligation (constraint) | `golden-approval-testing` | judgement: two runs byte-identical |
| FR-005-CON-1 | Inspection | not an obligation (constraint) | `inspection`, via an Inspections registry | judgement: subject is other repositories; TC-058 cannot falsify it (FND-402) |
| FR-006-CON-2 | Test | not an obligation (constraint) | `sast` | judgement: AST scan, matrix already types it `Static` |
| NFR-001-M-1, M-4 | Test | performance-benchmarking (misfire) | `golden-approval-testing` | judgement: baseline diff, `stable-output` |
| NFR-001-M-2, M-3, M-5 | Test | performance-benchmarking (misfire) | `integration-testing` | judgement: Quire validates the 0.2.0 skeleton set under 0.3.0 |
| StR-001-VC-1 | Inspection | not an obligation (VC table) | `demonstration`, or fold into TC-004 as `integration-testing` | StR prose: "judged by demonstrating"; the row has an executable oracle |
| StR-001-VC-2 | Demonstration | not an obligation (VC table) | `demonstration`, via an Inspections registry | judgement: no generator is exercised anywhere in the tree (FND-401) |
| StR-001-VC-3 | Demonstration | not an obligation (VC table) | `unit-testing` | judgement: four schema validations over two records |

## Suite plan implied

The methods above imply these evidence kinds. No `SuiteRegistry` declares a
producer for any of them and no `Inspections` document exists
(`archetype-matches-nothing` × 2), which is a gap in the plan, not in the
spec — but three of the four kinds now have a de facto producer in `tests/`.

- `Unit` (pytest over `spec_objects_architecture/`, `schemas/`, `manifest.yaml`, `package.json`): FR-001-AC-1, FR-002-AC-1..3, FR-002-CON-2, FR-002-CON-4, FR-003-AC-1..3, FR-003-AC-7, FR-004-AC-1, FR-004-CON-1, FR-005-AC-6..8, NFR-001-AC-1, NFR-001-AC-5, StR-001-VC-3.
- `Integration` (pytest with the Quire 0.46.0 wheel from `make dev-quire`; for FR-001/IT-001 a running filament-core; for IT-002 a quoin with an isolated `--config-root`): FR-001-AC-2..4, FR-002-AC-4..9, FR-003-AC-4..6, FR-004-AC-2..14, FR-005-AC-1..5, FR-005-AC-9, FR-005-CON-2, FR-006-AC-1..5, NFR-001-AC-2..4, IT-001, IT-002.
- `Static` (source/AST analysis, no subject execution): FR-002-CON-1, FR-006-CON-2.
- `Snapshot` (checked-in 0.2.0 baseline, byte comparison): FR-002-CON-3, FR-003-AC-7, FR-006-AC-6, NFR-001-AC-4.
- `Manual`, via an Inspections registry that does not exist: StR-001-VC-2, FR-005-CON-1 — and StR-001-VC-1 / FR-003-AC-5 only if their authored methods are kept rather than retyped.

## Diagnostics consulted

From `quoin advise` and `quire coverage --scope . --json` (quire 0.31.0, engine
0.46.0@ca7362d4; quoin 0.23.1-2-g3e842ce): `uncatalogued-verification-method`
× 2 (`Integration Test` 3 rows, `Schema Test` 1 row);
`untracked-id-has-minted-children` × 3 (`FR-005-CON-3`, `FR-003-AC-8` × 2, all
in `tests/test_consumer_boundaries.py`); 10 × "traces to … which matches no
declared row" (`TC-090`, `TC-091`, `FR-003-AC-8`, `FR-005-CON-3`,
`IT-002-SC-02..SC-05`); `status-column-matches-nothing` (functional-coverage);
`archetype-matches-nothing` × 2 (`Inspections`, `SuiteRegistry`);
`marker-form-mismatch` × 1; `hollow-denominator`
(`coverage.self_named_binding.python`); `catch-all-universal` (8 of 8
documents). Headline census: `Coverage: 126/126 rows backed (100%)`,
`python: 77/77/91 bound/tagged/candidates`, `authoring.tag_rate 91/91`.
Suite run: `152 passed, 7 skipped, 4 xfailed`. `DuplicateArchetype` /
`DuplicateInverseEdge` module-load noise ignored.
