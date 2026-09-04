---
id: SR-008
title: "Risk & complexity review of the #8 semantic module contract spec"
type: SpecReview
analysis: risk-complexity
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-declare-architecture-objects-against-semantic-core.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-emitted-json-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-005-executable-skeletons.md, spec/functional/FR-006-architecture-lowerings.md, spec/non-functional/NFR-001-additive-compatibility.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-quoin-module-install.md, spec/tests.md"
review_set: all
---
# SR-008: Risk & complexity review of the #8 semantic module contract spec

## Summary

Scored every requirement of the issue #8 set (StR-001, US-001, FR-001..FR-006,
NFR-001, IT-001, IT-002) on technical risk and volatility, grounded against the
implementation that has landed on this branch at commit `92d8355`
(`typespec/main.tsp`, the 31 files plus `toolchain.json` under
`spec_objects_architecture/schemas/`, `manifest.yaml` at 0.3.0, the thirteen
skeletons, the ten negative fixtures and the eleven test modules), against the
engine the spec names as its validator (`quire-rs/src/semantic/properties.rs`,
`contract.rs`, `filament.rs`), against the FR-035 module-manifest schema as it
stands on `agent-ix/filament-core-service` `origin/main`, and against the
sibling module `spec-objects-business`, which is the only other module through
this contract.

The dominant risk in this set is not schema design — the ten role schemas are
real and the emission chain is deterministic and gated. It is that **four of
the module's five external boundaries are, today, either refused or
unreproducible**: the manifest is refused by the FR-035 schema it claims to
conform to (`lexicon`, `filament-core-service#25`); every one of the ten object
types is refused on quire's Filament snapshot path (`filament-core-service#23`);
the engine the semantic evidence runs on exists on no index a repository may
commit against (`quire-rs#392`) and its extraction surface is pinned to no
version; and the only boundary that is green — the Quoin install — is a manual
Demonstration against a binary built from a branch. The schemas themselves are
the low-risk part of this change; the contract around them is the volatile
part.

Two measurements this review adds. **Corpus population:** a census of `~/dev`
(all `*.md` with a frontmatter `type:` of one of the ten, excluding
`node_modules`, `.git` and this repository) finds 24 artifacts, in three types
only — `api_endpoint` 10, `external_contract` 9, `interface` 5 — and *zero* in
the other seven. None of the 24 carries a frontmatter `object:` key, none
carries a `## Operations` section, and no `external_contract` carries
`## Invariants`. Under the required-key design every one of the 24 fails
`semantic.record-invalid` the day the promotion sweep adds `object:`.
**Vendored-schema skew:** the FR-003 Inputs claim was checked and holds —
`filament-core-service` `origin/main`, `quire-rs/schemas/vendored/` and
`quoin/src/semantic/schemas/` carry byte-identical copies
(`sha256:69cf9738600e7d8daa45ed5cd7231b17ca8dc58d068bd36af9b0d2c9b69dcbbc`).

## Verdict

**Plannable, with two blockers to disposition first.** FND-400 and FND-401 are
not spec defects to argue about — they are the two upstream tickets
(`filament-core-service#25`, `#23`) that stand between this module and both of
its named consumers, and the plan must sequence them rather than inherit them
as scope-outs. FND-402 (engine provisioning) governs whether any semantic row
can be re-run by anyone but the author, and should be the first task in the
plan, not a precondition assumed. FND-403 is the one finding that changes a
requirement: NFR-001's additive claim is measured on a population of ten
checked-in skeletons while the population the promotion gate cares about is 24
corpus artifacts, none of which can satisfy the schemas.

The remaining eight findings are plannable as slices, spikes and added
assertions; FND-404 in particular should be checked before `quire-rs#397` is
carried into the plan as a blocking dependency, because the engine source
suggests the defect is an authoring-form misunderstanding rather than a missing
keyword. Counts: 4 high, 6 medium, 2 low.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|----|----------|---------|------|--------------|
| FND-400 | high | The module cannot activate. FR-001-AC-1 is a `strict=True` xfail: FR-035's module-manifest schema is `additionalProperties: false` and its root `properties` are `archetypes, artifact_types, depends_on, description, doc_kinds, edge_types, grammars, lint_rules, manifest_version, name, nav, object_types, roles, semantic, state_schemas, version` — no `lexicon`, which this manifest has carried at line 338 since 0.2.0. So IT-001-SC-01, IT-001-SC-02, IT-001-SC-03, FR-001-AC-2..AC-4 and StR-001-VC-1 all rest on a POST that returns 422 today, and the module's oldest requirement — the reason the package exists — is the one with no path to green. The sibling `spec-objects-business` ships no `lexicon`, which is why the first module through this contract never met this and why nothing in the campaign's shared plan covers it. `agent-ix/filament-core-service#25` owns the fix. | FR-001-AC-1, FR-001-AC-2..4, IT-001 (all SC), StR-001-VC-1, FR-003 Behavior (lexicon bullet), FR-003-AC-7 | missing-requirement |
| FND-401 | high | Every one of the ten object types is refused on the Filament extraction path, and the spec records the dark state as correct rather than as a risk. `quire-rs/src/filament.rs::compile_object_type_snapshots` (line 409ff) tests each snapshot's `data_schema` for `DataSchemaForm::Inline`, and on anything else pushes `semantic.data-schema-unresolved-reference` at `error`, inserts the name into `refused` and `continue`s — emitting **no** compiled type. FR-003 makes the reference form mandatory for all ten (`No exported object type SHALL carry an inline data_schema`), so activation succeeds and the architecture graph is simultaneously emptied of all ten types. FR-001-AC-4 asserts the service stores the reference verbatim, i.e. the specification asserts the precondition of its own blackout. `filament-core-service#23` is scoped out in spec.md with no requirement stating what the module is unable to do until it lands, and no criterion that turns red when it does. | FR-001-AC-4, FR-003 Behavior (reference-form bullets), NFR-001 Statement, IT-001-SC-02, spec.md Out of Scope | missing-requirement |
| FND-402 | high | The evidence base is unreproducible and the surface it runs against is unpinned. Eight of the eleven test modules take the `quire_engine` fixture; `tests/conftest.py::require_quire` correctly fails rather than skips, but the wheel exists only on the dev-only `pypi.ix` (`quire-rs#392`) and `pyproject.toml` deliberately does not declare it, so no CI run and no second machine can produce a green semantic row. Compounding it: FR-005 Inputs says "0.46.0 **or later**" while FR-003 measures behaviour "against quire 0.46.0"; the four surface functions the tests bind to (`extract_semantic`, `extract`, `validate_document`, `validate_manifest`) and the record shape they read (`record["operations"][…]["params"][…]["type"]["target"]`, `["multiplicity"]["lower"]`, `record["diagnostics"]`) appear in no quire-rs acceptance criterion, so any later wheel may reshape them without breaking a quire-rs row. `tests/conftest.py::schema_registry` adds a second unprovisioned input — `node_modules/@agent-ix/semantic-core/generated/json-schema/`, resolvable only through a user-level npm config routing `@agent-ix` to npm.ix (FR-002-CON-4). | FR-005 Inputs, FR-005 Behavior (dev-quire and fail-not-skip bullets), FR-005 Dependencies, FR-003 Behavior (measured-against bullet), FR-002-CON-4, tests/conftest.py | correct-requirement-no-evidence |
| FND-403 | high | The required-key design makes corpus promotion a rewrite, and NFR-001 measures a population that hides it. Four types now require `clauses` (`external_contract`, `extension_point`, `binary_format`, `rate_limit`), three require `operations` and three require `fields` — every one of the ten requires at least one key (FR-004-CON-2). Census of `~/dev` (`*.md` with frontmatter `type:` in the ten, excluding `node_modules`, `.git`, this repo): 24 artifacts in three types — `api_endpoint` 10, `external_contract` 9, `interface` 5 — and none in the other seven. 0/24 carry `object:`; 0/10 `api_endpoint` artifacts carry `## Operations`; the `external_contract` artifacts author a prose `## Contract` and no `## Invariants`. So 24/24 fail `semantic.record-invalid` on the day `quoin#291` adds `object:` — the promotion is an authoring rewrite of every architecture artifact in the ecosystem, not an annotation. NFR-001's population is the ten checked-in 0.2.0 skeletons, which are additive precisely because they carry no `object:` either; the requirement is true and the number it produces is not the number the gate needs. | NFR-001 Statement, NFR-001 Scope, NFR-001-AC-2, FR-004 Behavior (required-key table), FR-004-CON-2, FR-005 Behavior (Invariants bullets), spec.md Out of Scope (quoin#291) | missing-requirement |
| FND-404 | medium | `quire-rs#397` should be re-verified before the plan treats it as a block, and the workaround it justified weakens two shipped fixtures. `properties.rs` (constraint parser, ~line 771) accepts `pattern` — but only slash-delimited, `pattern: /^[0-9a-f]{64}$/`, dialect `ecma-262`; the `semantic.unknown-constraint-keyword` arm is what a bare `pattern: ^[0-9a-f]{64}$` falls into, and `split_constraints` has explicit machinery (line 669ff) to keep commas inside `/…/` from splitting the cell. If that reading is right, `#397` is an authoring-form defect, not a missing keyword, and the digest field can express hex-ness. As shipped, `skeletons/data_schema.md`, `data_schema.sysml.md` and `queue.md` express a SHA-256 digest as `minLength: 64, maxLength: 64` — any 64 characters — and those files are the fixture contract `quire-contract-ir#52` and `filament-core-data#36` read, so the weaker constraint propagates to both frontends. | FR-005 Behavior (typed Properties bullet), FR-006-AC-2, skeletons/data_schema.md, skeletons/queue.md, quire-rs#397 | correct-requirement-no-evidence |
| FND-405 | medium | The `#398` ambiguity is worked around inside the test scaffolding, so the risk lands on the consumers rather than on this repo. FR-005 ships three alternates under their table skeleton's `id` and `title` by intent; `tests/conftest.py::bundle_index` skips a document whose `id` was already seen, so the suite validates against an index no engine builds. Every downstream fixture reader named in FR-004 and FR-006 Dependencies builds its own index — one entry per document is the obvious construction — and gets `semantic.ambiguous-type` on `ArtifactRecord`, the very token US-001-EX-2 uses as its worked example. The spec states the two-files-one-id decision but no rule a consumer's index must follow. | FR-005 Behavior (alternate-skeleton bullet), FR-005-AC-2, FR-005-AC-3, FR-006-AC-4, US-001-EX-2, tests/conftest.py::bundle_index, quire-rs#398 | missing-requirement |
| FND-406 | medium | Twenty-one of the thirty-one shipped schemas are outside every digest a consumer checks. `manifest.yaml` carries ten `data_schema.digest` values, one per export. The 21 support files — `IdentityField`, `ReturningOperation`, `GuaranteedOperation`, `RouteDecl`, `Threshold`, `ExceedResponse`, `RecordLayout`, `LayoutField`, five policy models and nine closed enums — are `$ref` targets that decide what the exported types refuse, and no digest reaches them. `toolchain.json` does hash all 31 (`sha256:d56db468…`), but nothing references it from the manifest and no requirement makes Quoin or Quire read it, so it is a same-tree guard for `make schemas-check` only: an edited `ReturningOperation.json` changes what every `ApiEndpoint` accepts and installs clean. The complexity is unique to this module — the sibling ships 7 support models to this one's 21. | FR-002 Outputs, FR-003 Behavior (digest bullet), FR-003-AC-2, FR-004 Outputs, IT-002 Objective ("verify every digest and `$ref`") | missing-requirement |
| FND-407 | medium | FR-006's agreement assertions and the manifest's locators are two independent parsers of the same fence, and nothing compares them. The lowering tests are right to hand-parse the kernel side (FR-006-CON-2 requires it, and TC-086 statically enforces that only `extract_semantic` and `extract` are reached), but `tests/test_architecture_lowerings.py::fence` is a repo-local regex — strip HTML comments, find `^## <heading>$`, take the *first* fence of the named language — while the manifest's `contract_yaml`, `schema_json`, `message_schema` and `layout_yaml` locators are what a consumer actually reads. TC-085 exercises the locators but asserts only `records[0][key].strip()` is non-empty. So the fence the agreement is proved over is never shown to be the fence the manifest yields; a heading rename, a second fence in a section, or a locator whose `language` facet differs would leave every FR-006 row green and every consumer reading different bytes. One assertion closes it: equality between the locator yield and the parsed fence. | FR-006-AC-1, FR-006-AC-2, FR-006-AC-3, FR-006-AC-6, FR-006-CON-2, TC-085, tests/test_architecture_lowerings.py | correct-requirement-no-evidence |
| FND-408 | medium | Two thirds of the schema surface is a guess at an extractor that does not exist, and the guess is versioned as if it were a contract. FR-004 declares sixteen keys the current extractor never populates plus `relations`; the 21 support models and nine closed enums exist to type those keys. FR-004's own Behavior concedes the point and requires those criteria to be tested against hand-built JSON — correctly — but the consequence is unstated: `agent-ix/quoin#335` publishes the mapping, and if it names `throttles` differently, nests `Threshold` differently, or renders `endianness` per-record rather than per-type, this module's `$id`s all move (FND-409) and both downstream frontends re-key. Sizing: 21 of 31 shipped files, versus 7 of 17 in the sibling. | FR-004 Behavior (unpopulated-key bullet, test-against-hand-built bullet), FR-004 Outputs, FR-004-AC-13, FR-004-AC-14, spec.md Out of Scope (quoin#335) | correct-requirement-no-evidence |
| FND-409 | medium | The version-embedded `$id` couples every schema edit to a manifest content hash whose behaviour FR-001 does not define. FR-002 accepts the churn cost of the versioned base and discharges it with a bump procedure, but the reverse case is unstated: an edit that changes emitted bytes *without* a version bump — a new support model, a tightened `Threshold`, an edited `description` — rewrites `data_schema.digest` values, changes the manifest's SHA-256, and re-activates a same-name, same-version module against filament-core. FR-001-AC-3 defines idempotency only for an identical re-activation; whether the service overwrites, 409s, or duplicates is nowhere. With 31 files and a `make lint` that runs `schemas-check`, this is the highest-frequency change in the repo's life, so it is the release risk most likely to be met. | FR-002 Behavior ($id base and bump bullets), FR-002-CON-5, FR-002-AC-8, FR-001-AC-3, FR-003-AC-2 | missing-requirement |
| FND-410 | low | FR-003's revision pin is the tip of a moving branch, not a frozen point. The claim was verified and holds today: `filament-core-service` `origin/main` *is* `a77f31e`, and its `module-manifest.schema.json`, `quire-rs/schemas/vendored/module-manifest.schema.json` and `quoin/src/semantic/schemas/module-manifest.schema.json` are byte-identical (`sha256:69cf9738600e7d8daa45ed5cd7231b17ca8dc58d068bd36af9b0d2c9b69dcbbc`). TC-001 asserts the digest of this repo's own vendored copy, which is the right guard for this side. What no row covers is the other two: the next `filament-core-service` commit — `#25`'s `lexicon` fix among them — moves the schema out from under a pin the spec words as if it were immutable, and re-skews Quoin and Quire until each re-vendors. | FR-003 Inputs, FR-001-AC-1, TC-001 | correct-requirement-no-evidence |
| FND-411 | low | Two of the three external boundaries have no automatable evidence, and both mutate state they share with the developer's machine. IT-001 needs a live `filament-core-service` with an empty `modules` registry and has no cleanup step, so a second run cannot meet its own precondition. FR-003-AC-5 and IT-002 are a `Demonstration` against a Quoin built from `agent-ix/quoin` main `3e842ce` — no release tag carries the semantic module — and they install into the operator's global module store, restoring it at step 5 with no criterion covering a restore that itself fails. The residual risk is not the tests' design but that the module's two consumer-facing claims are both attested by a human running commands. | IT-001 Preconditions, IT-001 Test Procedure, IT-002 Preconditions, IT-002-SC-05, IT-002-SC-06, FR-003-AC-5 | correct-requirement-no-evidence |

## Risk Register

| Req | Tech Risk | Volatility | Drivers | Mitigation |
|-----|-----------|------------|---------|------------|
| StR-001 | Low | Low | Consumer-stated need; VC-1 inherits FR-001's activation blocker, VC-3 is satisfied by the shipped schemas | Leave as written; VC-1 turns green with FND-400 |
| US-001 | Low | Medium | Maintainer story; the downstream frontends (`quire-contract-ir#52`, `filament-core-data#36`) may reshape what a declaration record carries, and EX-2's worked example is the token FND-405 makes ambiguous | Keep the story free of layout; let FR-004/FR-006 absorb the change; restate EX-2 once the bundle-index rule exists |
| FR-001 | Medium | Low | Live `filament-core-service`, content-hash idempotency, and a manifest the pinned FR-035 schema refuses over `lexicon` | Sequence `filament-core-service#25` as a plan task, not a scope-out (FND-400); define re-activation of a same-version manifest whose bytes changed (FND-409) |
| FR-002 | Medium | Medium | Pinned TypeSpec toolchain, npm.ix-only `@agent-ix/semantic-core`, version-embedded `$id`, byte-determinism gate over 31 files | Landed and gated (`make lint` → `schemas-check`, `toolchain.json`, `.gitattributes eol=lf`); add the no-bump-but-bytes-changed rule (FND-409) and a digest reachable by consumers over the 21 support files (FND-406) |
| FR-003 | Medium | High | Exact nine-key `semantic` block judged by three vendored copies of a schema that lives on a moving branch; ten digests that churn on every schema edit; the reference form that empties the Filament path | Verify and re-pin the vendored triple on every upstream bump (FND-410); state the Filament blackout and its exit criterion (FND-401); keep FND-406's digest gap on the ticket rather than in IT-002's Objective |
| FR-004 | Medium | High | 10 role schemas over 21 support models and 9 closed enums, 16 keys no extractor fills, `contains`/`unevaluatedProperties` encodings, semantic-core reader conventions (`identity` bare keyword) | Schemas are landed and testable; the volatility is `quoin#335`'s mapping — mark the unpopulated keys reserved in the spec, keep their tests labelled synthetic (FR-004 already requires this), and re-cut them as one slice when the mapping publishes (FND-408) |
| FR-005 | High | High | The whole semantic evidence base runs on a wheel on no committable index, against an unpinned extraction surface; three alternates share bundle identities; ten diagnostic-code string assertions | First plan task: `quire-rs#392`, then pin `quire` as a dev dependency and drop `make dev-quire` (FND-402); state the bundle-index identity rule for the alternates (FND-405); re-verify `#397` before carrying it (FND-404) |
| FR-006 | Medium | Medium | Two independent parsers of the same fence; the `contract_yaml` mapping is authored here but implemented in `quoin#335`; `TypeRef` resolution depends on the bundle index of FND-405 | Add the locator-yield-equals-parsed-fence assertion to TC-085 (FND-407); keep the mapping tables as the frontend's fixture contract and re-test them when the engine implements the lowering |
| NFR-001 | Medium | Low | Additive claim measured over ten checked-in skeletons that carry no `object:`; the population that matters is 24 corpus artifacts, 24 of which the schemas refuse | Restate the population, or add a second measured population (the corpus census) with its own metric; do not relax a schema (FND-403) |
| IT-001 | Medium | Low | Live cluster, empty-registry precondition, no cleanup, and an activation refused today | Add a teardown step so runs are independent; keep environment-gated until FND-400 (FND-411) |
| IT-002 | Medium | Medium | Manual Demonstration, Quoin built from an untagged main commit, global module-store mutation | Parameterise the Quoin binary and run under a temporary `QUOIN_HOME`; keep as Demonstration until then (FND-411) |

## Top hazards

1. **FND-400 — the module does not activate.** `lexicon` is refused by the
   FR-035 schema all three consumers vendor, so FR-001, IT-001 and StR-001-VC-1
   have no green path. It is one upstream key
   (`filament-core-service#25`), and it is the module's whole reason to exist.
2. **FND-401 — the Filament path is dark for all ten types.**
   `compile_object_type_snapshots` refuses every non-inline `data_schema` and
   emits no node, and FR-003 makes the reference form mandatory. Until
   `filament-core-service#23` lands, a successful activation and an empty
   architecture graph are the same state.
3. **FND-402 — no one but the author can run the semantic evidence.** Quire
   0.46.0 is on `pypi.ix` only (`quire-rs#392`), the surface is pinned to
   "0.46.0 or later", and `@agent-ix/semantic-core` needs an npm.ix route. The
   `fail-not-skip` policy is right and makes the gap loud instead of silent.
4. **FND-403 — promotion is a rewrite of 24 artifacts, not an annotation.**
   Four types require `clauses`, three require `operations`; the local corpus
   carries none of either, in any of its 24 artifacts.
5. **FND-406 — 21 of 31 schemas ship outside any digest a consumer checks**,
   while IT-002's Objective claims Quoin verifies "every digest and `$ref`".

## Mitigation order

1. Disposition FND-400 and FND-401 as sequenced upstream tasks
   (`filament-core-service#25`, `#23`), each with a criterion in this spec that
   turns red the day it lands.
2. Land `quire-rs#392` and convert `make dev-quire` into a committed dev
   dependency (FND-402); at the same time pin the extraction surface to an
   exact version, or record the surface functions and record shape as this
   module's own contract test.
3. Re-verify `quire-rs#397` against `properties.rs` (FND-404) before the plan
   inherits it; if `pattern: /…/` works, restore the hex constraint on the
   three digest fixtures.
4. Restate NFR-001's population, or add the corpus census as a second measured
   population with its own metric (FND-403).
5. Add the two cheap assertions: locator yield equals parsed fence (FND-407),
   and a consumer-reachable digest over the support schemas (FND-406).
6. State the bundle-index identity rule for the three alternates (FND-405) and
   the no-bump-but-bytes-changed re-activation rule (FND-409); defer FND-408 to
   the `quoin#335` slice.

## Failure-domain gaps

Cross-referenced against [SR-006](./failure-domain.md), which is current for
this branch and this commit. Its four highs remain open and this analysis
concurs with all four; two overlap directly (FND-401 here restates FND-201 with
the risk framing and the exit criterion; FND-405 restates FND-202 as a
consumer-borne rather than repo-borne risk). FND-406 and FND-409 sharpen
FND-206 and FND-207 respectively. FND-200 (NFR-001-AC-3 unsatisfiable) and
FND-203 (an exemption granted on the wrong path) are outside this analysis's
axes and are not restated here; they remain open on SR-006. FND-404, FND-407,
FND-410 and the corpus census in FND-403 are new to this review.

## Dispositions

| Finding | Disposition |
|---------|-------------|
| FND-400 | Sequence `filament-core-service#25`; keep the strict xfail until it lands |
| FND-401 | State the blackout and its exit criterion in FR-003 or NFR-001; sequence `filament-core-service#23` |
| FND-402 | First plan task: `quire-rs#392`; then pin the surface exactly |
| FND-403 | Restate NFR-001's population or add the corpus census as a second metric |
| FND-404 | Re-verify `quire-rs#397`; restore the hex constraint if it holds |
| FND-405 | Add a bundle-index identity rule for the alternates to FR-005 or FR-006 |
| FND-406 | Give consumers a digest over the support schemas, or correct IT-002's Objective |
| FND-407 | Add the locator-yield equality assertion to TC-085 |
| FND-408 | Defer to the `quoin#335` slice; keep the reserved-key labelling FR-004 already requires |
| FND-409 | Define re-activation of a same-version manifest whose bytes changed |
| FND-410 | Add a skew check when either consumer re-vendors the FR-035 schema |
| FND-411 | Add an IT-001 teardown; parameterise IT-002's Quoin binary and `QUOIN_HOME` |
