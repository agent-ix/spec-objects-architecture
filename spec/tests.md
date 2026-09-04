---
id: TM-001
title: "spec-objects-architecture Test Matrix"
type: TestMatrix
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/FR-001"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/FR-002"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/FR-003"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/FR-005"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/FR-006"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/NFR-001"
    type: covers
---
# Test Matrix

## Overview

This matrix is the verification contract for the module: the manifest
activation requirement (FR-001, issue #1 era) and the issue #8 semantic data
schemas (US-001, FR-002..FR-006, NFR-001, IT-002). Coverage is complete when
every acceptance criterion, named constraint, and NFR metric maps to at least
one test case. Rows are `🚧` until a tagged test asserts them.

What the numbers count. `quire coverage` reports **141/141 rows backed
(100%)**: 79 `TC-` rows from the Test Case Summary below plus 62 criterion
rows minted from the requirements (4 FR-001, 10 FR-002, 8 FR-003, 16 FR-004,
10 FR-005, 6 FR-006, 5 NFR-001 metrics, 3 StR-001 validation criteria). A row
is *backed* when a source symbol carries a binding trace tag for it — that is
a tagging measurement, not a run outcome. The run is separate: `make test`
reports **163 passed, 7 skipped, 4 xfailed**. The 7 skips are the
environment-gated rows (4 need a running `filament-core-service`, 3 are the
opt-in Quoin roundtrip, which was run separately and passed); the 4 xfails are
the expected failures named under Test Environment. No row is green because a
test was skipped.

## Test Matrix Rules

1. Every acceptance criterion and named constraint has at least one test case.
2. Both Properties forms (typed table, `sysml` fence) and every object type are tested.
3. Item-rule boundaries are tested at their allowed and refused edges (zero versus one identity field, one versus two operations, empty versus one-item arrays).
4. Every named refusal (digest mismatch, unknown key, both forms, dangling clause, non-Identifier token, missing return, missing post-clause) has a failing fixture.
5. Availability states (`available`, `not_applicable`, `missing`) are tested per declaration kind.
6. Legacy artifacts, the empty record, and unresolved tokens are covered as edge cases.

## Requirements Traceability

### Stakeholder Requirement Coverage

| Stakeholder Req | Trace to US/FR | Test/Validation | Coverage Status |
|---|---|---|---|
| StR-001 | US-001, FR-001..FR-006 | TC-005, TC-006, TC-007 | 🚧 VC-1 needs a running filament-core; VC-2 and VC-3 pass |

### User Story Coverage

| User Story | Acceptance Criteria | Test Cases | Coverage Status |
|---|---|---|---|
| US-001 | US-001-EX-1..3 (illustrative) implemented by FR-002..FR-006 | TC-050, TC-070, TC-080 | ✅ |

### Functional Requirement Coverage

| Functional Req | Acceptance Criteria | Test Cases | Coverage Status |
|---|---|---|---|
| FR-001 | FR-001-AC-1..4 | TC-001..TC-004 | 🚧 AC-1 is an expected failure on filament-core-service#25; AC-2..AC-4 need a running filament-core |
| FR-002 | FR-002-AC-1..10, FR-002-CON-1..5 | TC-010..TC-019, TC-071..TC-079, TC-087 | ✅ |
| FR-003 | FR-003-AC-1..8, FR-003-CON-1..2 | TC-020..TC-028, TC-090 | ✅ AC-6's naming half is an expected failure |
| FR-004 | FR-004-AC-1..16, FR-004-CON-1..3 | TC-030..TC-046 | ✅ |
| FR-005 | FR-005-AC-1..10, FR-005-CON-1..3 | TC-050..TC-059, TC-065, TC-091 | ✅ AC-10's per-file half is an expected failure |
| FR-006 | FR-006-AC-1..6, FR-006-CON-1..2 | TC-080..TC-086 | ✅ |

### Non-Functional Requirement Coverage

| Non-Functional Req | Verification Method | Evidence/Test Cases | Status |
|---|---|---|---|
| NFR-001 | Test (NFR-001-AC-1..5: locator baseline diff, legacy skeleton validation, edge-vocabulary diff) | TC-060..TC-064 | ✅ |

### Integration Test Coverage

| Integration Test | Success Criteria | Test Cases | Coverage Status |
|---|---|---|---|
| IT-001 | IT-001-SC-01..03 | TC-002..TC-004 | 🚧 needs a running filament-core |
| IT-002 | IT-002-SC-01..06 | TC-070 | ✅ opt-in behind `QUOIN_INSTALL_ROUNDTRIP=1` |

## Test Case Summary

| Test ID | Title | Type | Priority | Traces To | Status |
|---|---|---|---|---|---|
| TC-001 | Manifest validates against the vendored FR-035 module-manifest schema through `quire.validate_manifest` | Unit | P0 | FR-001-AC-1 | 🚧 the schema-revision and only-violation halves pass; the criterion itself is an expected failure on filament-core-service#25 (the `lexicon` key) |
| TC-002 | Activation against a clean filament-core returns 200 | Integration | P1 | FR-001-AC-2, IT-001-SC-01 | 🚧 needs a running filament-core |
| TC-003 | Re-activation is a content-hash no-op | Integration | P1 | FR-001-AC-3, IT-001-SC-03 | 🚧 needs a running filament-core |
| TC-004 | Every declared contribution appears in the registry tables | Integration | P1 | FR-001-AC-4, IT-001-SC-02 | 🚧 needs a running filament-core |
| TC-005 | Module activation registers the declared contents | Manual | P2 | StR-001-VC-1 | 🚧 needs a running filament-core |
| TC-006 | `minijinja-cli` renders every shipped skeleton and each rendered artifact validates against this module | Integration | P2 | StR-001-VC-2 | ✅ |
| TC-007 | Every object type ships a typed schema a fixture reader can consume; an api-endpoint and a rate-limit record are distinguishable by schema alone | Unit | P2 | StR-001-VC-3 | ✅ |
| TC-010 | Emitted set equals the ten object-type models plus the declared support models; `toolchain.json` records compiler and emitter 1.15.0 | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-011 | Every shipped schema declares the 2020-12 `$schema` and the `$id` matching its file name under the manifest-version base | Unit | P0 | FR-002-AC-2 | ✅ |
| TC-012 | Every `$ref` resolves to a shipped sibling or semantic-core 0.1.0 | Unit | P0 | FR-002-AC-3 | ✅ |
| TC-013 | `make schemas-check` exits zero on the committed tree and non-zero naming a mutated schema or digest | Integration | P1 | FR-002-AC-4 | ✅ |
| TC-014 | A `@jsonSchema` base version differing from the manifest version fails the generator naming both | Integration | P1 | FR-002-AC-5 | ✅ |
| TC-015 | The built wheel contains every emitted schema file | Integration | P1 | FR-002-AC-6 | ✅ |
| TC-016 | Two generator runs over one source are byte-identical | Integration | P1 | FR-002-CON-3 | ✅ |
| TC-017 | The build uses the official `@typespec/json-schema` emitter only and no emitted file is hand-edited | Static | P2 | FR-002-CON-1 | ✅ |
| TC-018 | No `.npmrc`, no `file:`/`link:` dependency, exact toolchain pins in `package.json` | Static | P2 | FR-002-CON-2 | ✅ |
| TC-019 | `package-lock.json` resolves every package from npmjs except `@agent-ix/semantic-core` (npm.ix) | Unit | P2 | FR-002-CON-4 | ✅ |
| TC-020 | The `semantic` block equals the nine admitted keys and `exports` equals the ten types | Unit | P0 | FR-003-AC-1, FR-003-CON-1 | ✅ |
| TC-021 | Every exported type's `data_schema` is the reference form whose file hashes to the recorded digest | Unit | P0 | FR-003-AC-2 | ✅ |
| TC-022 | Every 0.2.0 locator is unchanged against the checked-in baseline | Unit | P0 | FR-003-AC-3 | ✅ |
| TC-023 | Every added locator is `required: false` | Unit | P1 | FR-003-AC-3, FR-003-CON-2 | ✅ |
| TC-024 | `quire.Registry.load_from` lists all ten archetypes | Integration | P0 | FR-003-AC-4 | ✅ |
| TC-025 | `validate_document` on every skeleton reports no `semantic.*` load failure | Integration | P0 | FR-003-AC-4 | ✅ |
| TC-026 | An unknown `semantic` key and an altered digest are each refused by the loader; the refusal names the key or path | Integration | P1 | FR-003-AC-6 | ✅ refusal verified; the naming half is an expected failure blocked on quire-rs#221 and quire-rs#394 |
| TC-027 | `quoin module install path:` succeeds, lists the module, and the prior entry is restored | Integration | P1 | FR-003-AC-5 | ✅ run against quoin `0.23.1-2-g3e842ce`; opt-in behind `QUOIN_INSTALL_ROUNDTRIP=1` because it writes the operator's global module store |
| TC-028 | The 0.2.0 `lexicon` block is byte-identical at 0.3.0 | Unit | P1 | FR-003-AC-7 | ✅ |
| TC-030 | Each of the ten schemas differs from every other in a required, forbidden, or item rule; none is `type: object` only | Unit | P0 | FR-004-AC-1 | ✅ |
| TC-031 | Api endpoint: a returning operation validates; the return removed fails; `fields` fails | Integration | P0 | FR-004-AC-2 | ✅ |
| TC-032 | Data schema: one field validates; empty `fields` fails; `operations` fails | Integration | P0 | FR-004-AC-3 | ✅ |
| TC-033 | Queue: an identity row validates with `delivery` and `carries`; identity removed fails; `operations` fails | Integration | P0 | FR-004-AC-4 | ✅ |
| TC-034 | Action: exactly one operation validates; two operations fail; `fields` fails | Integration | P0 | FR-004-AC-5 | ✅ |
| TC-035 | Ui component: a non-identity field validates with `operations`; an identity field fails | Integration | P0 | FR-004-AC-6 | ✅ |
| TC-036 | Interface: one operation validates with `associated_types`; empty `operations` fails; `routes` fails | Integration | P0 | FR-004-AC-7 | ✅ |
| TC-037 | External contract: a clause plus a post-carrying operation validates; no `clauses` fails; no `post` fails | Integration | P0 | FR-004-AC-8 | ✅ |
| TC-038 | Extension point: an operation and a clause validate with `registration` and `stability`; no `clauses` fails; `fields` fails | Integration | P1 | FR-004-AC-9 | ✅ |
| TC-039 | Binary format: one clause validates with `records` and `endianness`; an empty `RecordLayout.fields` fails; `operations` fails | Integration | P1 | FR-004-AC-10 | ✅ |
| TC-040 | Rate limit: one clause validates with `thresholds`; a `scope` outside `LimitScope` fails; `fields` fails | Integration | P1 | FR-004-AC-11 | ✅ |
| TC-041 | The empty record `{}` fails all ten object-type schemas | Integration | P0 | FR-004-AC-12, FR-004-CON-2 | ✅ |
| TC-042 | Placeholder `unresolved` target is accepted by the schema and reported by the extractor; a bare token is refused | Integration | P1 | FR-004-AC-13 | ✅ |
| TC-043 | Every optional profile key can be removed without invalidating the record, and no profile key is required anywhere | Integration | P1 | FR-004-AC-14, FR-004-CON-3 | ✅ |
| TC-044 | No module schema redeclares a semantic-core model; every grammar item is a `$ref` to semantic-core | Unit | P1 | FR-004-CON-1 | ✅ |
| TC-045 | No shipped schema declares an observation key, so a declaration record cannot be read as an extraction from running code | Unit | P0 | FR-004-AC-15 | ✅ |
| TC-046 | `relations` is admitted by six object types and refused by four, both halves asserted | Integration | P1 | FR-004-AC-16 | ✅ |
| TC-050 | Every skeleton (ten plus three alternates) validates with no error | Integration | P0 | FR-005-AC-1 | ✅ |
| TC-051 | Table and `sysml` skeletons extract to identical normalized fields with the recorded forms | Integration | P0 | FR-005-AC-2, FR-005-CON-2 | ✅ |
| TC-052 | Under the skeleton bundle index every skeleton extracts with zero errors and zero unresolved tokens | Integration | P0 | FR-005-AC-3 | ✅ |
| TC-053 | Availability states per skeleton (fields, clauses, operations) match the type's declared set | Integration | P1 | FR-005-AC-4 | ✅ |
| TC-054 | Every negative fixture fails with its `expect:` code and the ten named cases exist | Integration | P0 | FR-005-AC-5 | ✅ |
| TC-055 | Every skeleton's H2 set is asserted by the manifest and includes every required heading | Unit | P1 | FR-005-AC-6 | ✅ |
| TC-056 | Every skeleton is placeholder-free with non-empty asserted sections | Unit | P2 | FR-005-AC-7 | ✅ |
| TC-057 | A Properties section holding both a table and a fence is refused at the second form | Integration | P1 | FR-005-CON-2 | ✅ |
| TC-058 | The repository carries no corpus path, no vendored neighbour fixture, no `/vendor/` path and no submodule, and every tracked path is part of the module's own surface (tree assertion over `git ls-files`, not a diff against a moving ref) | Unit | P2 | FR-005-CON-1 | ✅ falsified three ways and restored: a `corpus/` probe, a `fixtures/semantic-module` probe and a `.gitmodules` each turn it red |
| TC-059 | Skeleton titles are distinct `Identifier`s outside `KernelScalar`, and `object` equals `type` in every skeleton frontmatter | Unit | P1 | FR-005-AC-8 | ✅ |
| TC-060 | Zero 0.2.0 locators changed | Unit | P0 | NFR-001-AC-1 | ✅ |
| TC-061 | Every checked-in 0.2.0 skeleton validates under 0.3.0 with zero errors; a legacy form that declares `object:` is not an error | Integration | P0 | NFR-001-AC-2 | ✅ the criterion passes; the `object:`-declaring case is an expected failure on quire-rs#391 |
| TC-062 | No 0.2.0 skeleton carries a `## Properties` section in any form, so the `semantic.legacy-properties-form` count over the ten of them is 0 | Integration | P1 | NFR-001-AC-3 | ✅ the measured population is empty, and the row asserts the emptiness rather than a warning the module cannot produce |
| TC-063 | Each 0.2.0 locator's yield is identical under 0.2.0 and 0.3.0 | Integration | P1 | NFR-001-AC-4 | ✅ |
| TC-064 | Every object type's `allowed_links` and `roles` sets are identical at 0.2.0 and 0.3.0 | Unit | P1 | NFR-001-AC-5 | ✅ |
| TC-065 | The action skeleton extracts one operation, the api endpoint at least one returning operation, the external contract at least one post-carrying operation | Integration | P1 | FR-005-AC-9 | ✅ |
| TC-070 | Quoin install roundtrip with state restore | Integration | P1 | IT-002-SC-01, IT-002-SC-02, IT-002-SC-03, IT-002-SC-04, IT-002-SC-05, IT-002-SC-06, FR-003-AC-5 | ✅ run against quoin `0.23.1-2-g3e842ce`; opt-in behind `QUOIN_INSTALL_ROUNDTRIP=1` |
| TC-071 | The packed npm tarball contains `manifest.yaml` and a sibling `schemas/<Model>.json` per export | Integration | P1 | FR-002-AC-7 | ✅ |
| TC-072 | A coordinated version bump re-emits every `$id`/`$ref` at the new version with matching digests; bumping one half of the pair fails the check | Integration | P1 | FR-002-AC-8, FR-002-CON-5 | ✅ |
| TC-073 | `make schemas-check` names a stale committed schema with no emitted counterpart and writes nothing | Integration | P1 | FR-002-AC-9 | ✅ |
| TC-074 | No acceptance test hard-codes the `$id` version segment; each reads it from the manifest `version` | Unit | P2 | FR-002-CON-5 | ✅ |
| TC-075 | A Node older than 20 fails the generator naming the required version | Integration | P2 | FR-002-AC-4 | ✅ |
| TC-076 | An unresolvable `@typespec/compiler` fails the generator naming the missing binary | Integration | P2 | FR-002-AC-4 | ✅ |
| TC-077 | A `tsp compile` failure exits non-zero and leaves the committed schemas and manifest byte-identical | Integration | P1 | FR-002-AC-4 | ✅ |
| TC-078 | A source emitting no module model exits non-zero naming the base it found nothing under | Integration | P1 | FR-002-AC-4 | ✅ |
| TC-079 | A manifest `schema:` path with no emitted counterpart, and one with no digest line, are each named | Integration | P1 | FR-002-AC-4 | ✅ |
| TC-080 | The interface `## Contract` YAML and its extracted `OperationDecl[]` agree on names, params, and returns | Integration | P0 | FR-006-AC-1 | ✅ |
| TC-081 | The data-schema `## Schema` fence and its `## Properties` table agree on property names and the required set | Integration | P0 | FR-006-AC-2 | ✅ |
| TC-082 | The queue `## Message Format` fence and its `## Properties` table agree on the key set | Integration | P1 | FR-006-AC-3 | ✅ |
| TC-083 | Every non-kernel `type.target` of the api-endpoint record resolves to a shipped data_schema title with zero unresolved findings | Integration | P0 | FR-006-AC-4 | ✅ |
| TC-084 | An api-endpoint fixture returning an undeclared token yields exactly one `semantic.unresolved-type` finding and the `unresolved` placeholder target | Integration | P1 | FR-006-AC-5 | ✅ |
| TC-085 | The `contract_yaml`, `schema_json`, and `message_schema` locators are byte-identical to 0.2.0 and still yield their fence text | Integration | P1 | FR-006-AC-6, FR-006-CON-1 | ✅ |
| TC-086 | Every FR-006 agreement assertion reads two sections of one authored artifact and no engine lowering | Static | P2 | FR-006-CON-2 | ✅ |
| TC-087 | An unrecognised generator argument exits non-zero and writes nothing | Integration | P2 | FR-002-AC-10 | ✅ |
| TC-090 | The Filament snapshot path refuses all ten reference-form `data_schema` values and accepts the same schemas resolved | Integration | P1 | FR-003-AC-8 | ✅ |
| TC-091 | The bundle index holds one entry per declaration id; a per-file index makes an alternate-bearing declaration ambiguous with itself | Integration | P1 | FR-005-AC-10, FR-005-CON-3 | ✅ the per-file half is an expected failure on quire-rs#398 |

## Test Environment

Every `Integration` row that names Quire runs against the Quire wheel FR-005
Inputs pins, provisioned by `make dev-quire`. That wheel is not on any index
this repository may commit a dependency against (`internal-pypi` serves 0.33.0
at most); `agent-ix/quire-rs#392` is the blocking issue. The suite **fails**
rather than skips when `extract_semantic` is absent, so no row here can be
reported green without the engine under test.

Four rows carry an explicit expected failure, each naming the issue that owns
it and none of them skipped: TC-001 (`agent-ix/filament-core-service#25`, the
FR-035 schema refuses the `lexicon` block), TC-026 (`agent-ix/quire-rs#221`
and `#394`, the refusal names nothing), TC-061 (`agent-ix/quire-rs#391`, a
legacy form declaring `object:` validates as `{}`), and TC-091
(`agent-ix/quire-rs#398`, a per-file bundle index makes a declaration
ambiguous with itself).

Two rows are opt-in rather than gated on an absent environment. TC-027 and
TC-070 write the operator's global `quoin module` store, so they run only
under `QUOIN_INSTALL_ROUNDTRIP=1`. Both were run against quoin
`0.23.1-2-g3e842ce` on 2026-09-04 and passed, restoring the prior entry's
source, ref and sha.

Rows over the record keys the extractor does not populate (`routes`,
`requires`, `carries`, `delivery`, `renders`, `triggers`, `associated_types`,
`provider`, `versioning`, `exposes`, `registration`, `stability`, `records`,
`endianness`, `serializes`, `thresholds`, `throttles`, `relations`) are
verified against hand-built records, not extracted ones — TC-033, TC-036,
TC-038, TC-039, TC-040, TC-043 in particular — and their tests say so; they are
schema evidence, not extraction evidence.

## Coverage Gaps

Every criterion, constraint, and metric above has a row backed by a tagged
test. Two evidence-plan artifacts are absent and are carried by the plan, not
by this matrix: no `SuiteRegistry` document declares a producer for the `Unit`,
`Integration`, `Static`, and `Manual` evidence kinds, and no `Inspections`
document exists to discharge the `Static` rows (TC-017, TC-018, TC-058,
TC-086). `quire coverage` reports every declared row backed.

One check the coverage engine performs is **disabled** on this matrix and is
not claimed: `quire coverage` reports `status-column-matches-nothing`, because
the `TestMatrix` archetype asserts a `Coverage Status` column on the
requirement-level tables while `traceability.status.column` is configured as
`Status`. The two cannot both be satisfied — renaming the column to match the
config fails `quire validate` structurally — so status classification is
skipped and complete-but-unbacked rows are not machine-checked here.
`agent-ix/spec-artifacts-process#83` owns reconciling them. The backed
figure is unaffected: it counts trace-tag binding, which is measured
independently of the status column.

Five rows stay `🚧` and none of them is a coverage claim: TC-001 (the expected
failure above), and TC-002, TC-003, TC-004 and TC-005, which need a running
`filament-core-service` at revision `a77f31e` — no release tag contains it, so
this repository cannot provision one. That is issue #1's debt, carried
forward.
