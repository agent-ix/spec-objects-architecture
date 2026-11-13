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
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/FR-008"
    type: covers
  - target: "ix://agent-ix/spec-objects-architecture/FR-010"
    type: covers
---
# Test Matrix

## Overview

This matrix is the verification contract for the module: the manifest
activation requirement (FR-001, issue #1 era) and the issue #8 semantic data
schemas (US-001, FR-002..FR-006, IT-002), and the issue #10 systems
kinds (FR-007). Coverage is complete when
every acceptance criterion and named constraint maps to at least
one test case. Rows are `🚧` until a tagged test asserts them.

What the numbers count. A row is *backed* when a source symbol carries a
binding trace tag for it; that is a tagging measurement, not a run outcome.
The run is separate: `make test` reports passes, skips and expected failures.
The skips are the environment-gated rows (those needing a running
`filament-core-service`, and the opt-in Quoin roundtrip); the expected failures
are those named under Test Environment. No row is green because a test was
skipped.

## Test Matrix Rules

1. Every acceptance criterion and named constraint has at least one test case.
2. Both Properties forms (typed table, `sysml` fence) and every object type are tested.
3. Item-rule boundaries are tested at their allowed and refused edges (zero versus one identity field, one versus two operations, empty versus one-item arrays).
4. Every named refusal (unknown key, both forms, dangling clause, non-Identifier token, missing return, missing post-clause) has a failing fixture.
5. Availability states (`available`, `not_applicable`, `missing`) are tested per declaration kind.
6. Legacy artifacts, the empty record, and unresolved tokens are covered as edge cases.

## Requirements Traceability

### Stakeholder Requirement Coverage

| Stakeholder Req | Trace to US/FR | Test/Validation | Coverage Status |
|---|---|---|---|
| StR-001 | US-001, FR-001..FR-006 | TC-005, TC-007 | 🚧 VC-1 needs a running filament-core; VC-3 passes |

### User Story Coverage

| User Story | Acceptance Criteria | Test Cases | Coverage Status |
|---|---|---|---|
| US-001 | US-001-EX-1..3 (illustrative) implemented by FR-002..FR-006 | TC-050, TC-070, TC-080 | ✅ |

### Functional Requirement Coverage

| Functional Req | Acceptance Criteria | Test Cases | Coverage Status |
|---|---|---|---|
| FR-001 | FR-001-AC-2..4 | TC-002..TC-004 | 🚧 AC-2..AC-4 need a running filament-core |
| FR-002 | FR-002-AC-1..4, FR-002-AC-6, FR-002-AC-7, FR-002-AC-9, FR-002-AC-10, FR-002-CON-1..4 | TC-010..TC-013, TC-015..TC-019, TC-071, TC-073, TC-075..TC-079, TC-087 | ✅ |
| FR-003 | FR-003-AC-1..9 except AC-3 and AC-7, FR-003-CON-1 | TC-020, TC-024..TC-027, TC-090, TC-111 | ✅ AC-6's naming half is an expected failure |
| FR-004 | FR-004-AC-1..16, FR-004-CON-1, FR-004-CON-3 | TC-030..TC-046 | ✅ |
| FR-005 | FR-005-AC-1..10, FR-005-CON-1..3 | TC-050..TC-059, TC-065, TC-091 | ✅ |
| FR-006 | FR-006-AC-1..6, FR-006-CON-1..2 | TC-080..TC-086 | ✅ |
| FR-007 | FR-007-AC-1..12, FR-007-CON-1 | TC-100..TC-113 | ✅ |
| FR-009 | FR-009-AC-1..3, FR-009-CON-1 | TC-130, TC-131 | ✅ |
| FR-008 | FR-008-AC-1..7 | TC-120..TC-126 | ✅ |
| FR-010 | FR-010-AC-1..10, FR-010-CON-1 | TC-140..TC-149 | 🚧 needs quire-rs FR-086 (PLAT-1418) and the manifest data (PLAT-1599) |

### Integration Test Coverage

| Integration Test | Success Criteria | Test Cases | Coverage Status |
|---|---|---|---|
| IT-001 | IT-001-SC-01..03 | TC-002..TC-004 | 🚧 needs a running filament-core |
| IT-002 | IT-002-SC-01..06 | TC-070 | ✅ opt-in behind `QUOIN_INSTALL_ROUNDTRIP=1` |

## Test Case Summary

| Test ID | Title | Type | Priority | Traces To | Status |
|---|---|---|---|---|---|
| TC-002 | Activation against a clean filament-core returns 200 | Integration | P1 | FR-001-AC-2, IT-001-SC-01 | 🚧 needs a running filament-core |
| TC-003 | Re-activation is a content-hash no-op | Integration | P1 | FR-001-AC-3, IT-001-SC-03 | 🚧 needs a running filament-core |
| TC-004 | Every declared contribution appears in the registry tables | Integration | P1 | FR-001-AC-4, IT-001-SC-02 | 🚧 needs a running filament-core |
| TC-005 | Module activation registers the declared contents | Manual | P2 | StR-001-VC-1 | 🚧 needs a running filament-core |
| TC-007 | Every object type ships a typed schema a fixture reader can consume; an api-endpoint and a rate-limit record are distinguishable by schema alone | Unit | P2 | StR-001-VC-3 | ✅ |
| TC-011 | Every shipped schema declares the 2020-12 `$schema` and the `$id` matching its file name | Unit | P0 | FR-002-AC-2 | ✅ |
| TC-012 | Every `$ref` resolves to a shipped sibling or the declared semantic-core bundle | Unit | P0 | FR-002-AC-3 | ✅ |
| TC-013 | `make schemas-check` exits zero on the committed tree and non-zero naming a mutated schema | Integration | P1 | FR-002-AC-4 | ✅ |
| TC-015 | The built wheel contains every emitted schema file | Integration | P1 | FR-002-AC-6 | ✅ |
| TC-016 | Two generator runs over one source are byte-identical | Integration | P1 | FR-002-CON-3 | ✅ |
| TC-017 | The build uses the official `@typespec/json-schema` emitter only and no emitted file is hand-edited | Static | P2 | FR-002-CON-1 | ✅ |
| TC-018 | No `.npmrc`, no `file:`/`link:` dependency | Static | P2 | FR-002-CON-2 | ✅ |
| TC-019 | `package-lock.json` resolves every package from npmjs, `@agent-ix/semantic-core` included | Unit | P2 | FR-002-CON-4 | ✅ |
| TC-020 | The `semantic` block equals the eight admitted keys and `exports` equals the fourteen types | Unit | P0 | FR-003-AC-1, FR-003-CON-1 | ✅ |
| TC-024 | `quire.Registry.load_from` lists all fourteen archetypes | Integration | P0 | FR-003-AC-4 | ✅ |
| TC-025 | `validate_document` on every skeleton reports no `semantic.*` load failure | Integration | P0 | FR-003-AC-4 | ✅ |
| TC-026 | An unknown `semantic` key is refused by the loader; the refusal names the key | Integration | P1 | FR-003-AC-6 | ✅ refusal verified; the naming half is an expected failure blocked on quire-rs#221 and quire-rs#394 |
| TC-027 | `quoin module install path:` succeeds, lists the module, and the prior entry is restored | Integration | P1 | FR-003-AC-5 | ✅ opt-in behind `QUOIN_INSTALL_ROUNDTRIP=1` because it writes the operator's global module store |
| TC-030 | Each of the ten schemas differs from every other in a required, forbidden, or item rule; none is `type: object` only | Unit | P0 | FR-004-AC-1 | ✅ |
| TC-031 | Api endpoint: a returning operation validates; the return removed fails; `fields` fails | Integration | P0 | FR-004-AC-2 | ✅ |
| TC-032 | Data schema: one field validates; empty `fields` fails; `operations` fails | Integration | P0 | FR-004-AC-3 | ✅ |
| TC-033 | Queue: an identity row validates with `delivery` and `carries`; identity removed fails; `operations` fails | Integration | P0 | FR-004-AC-4 | ✅ |
| TC-034 | Action: exactly one operation validates; two operations fail; `fields` fails | Integration | P0 | FR-004-AC-5 | ✅ |
| TC-035 | Ui component: a non-identity field validates with `operations`; an identity field fails | Integration | P0 | FR-004-AC-6 | ✅ |
| TC-036 | Interface: one operation or one field validates with its `featureOrder`, `associated_types` accepted; no `featureOrder` fails; `routes` fails | Integration | P0 | FR-004-AC-7 | ✅ |
| TC-037 | External contract: a clause plus a post-carrying operation validates; no `clauses` validates (FR-009); no `post` fails | Integration | P0 | FR-004-AC-8 | ✅ |
| TC-038 | Extension point: an operation and a clause validate with `registration` and `stability`; no `clauses` validates (FR-009); `fields` fails | Integration | P1 | FR-004-AC-9 | ✅ |
| TC-039 | Binary format: one clause validates with `records` and `endianness`; an empty `RecordLayout.fields` fails; `operations` fails | Integration | P1 | FR-004-AC-10 | ✅ |
| TC-040 | Rate limit: one clause validates with `thresholds`; a `scope` outside `LimitScope` fails; `fields` fails | Integration | P1 | FR-004-AC-11 | ✅ |
| TC-041 | The empty record `{}` fails `Interface` and validates against every other type (FR-009) | Integration | P0 | FR-004-AC-12 | ✅ |
| TC-042 | Placeholder `unresolved` target is accepted by the schema and reported by the extractor; a bare token is refused | Integration | P1 | FR-004-AC-13 | ✅ |
| TC-043 | Every optional profile key can be removed without invalidating the record, and no profile key is required anywhere | Integration | P1 | FR-004-AC-14, FR-004-CON-3 | ✅ |
| TC-044 | No module schema redeclares a semantic-core model; every grammar item is a `$ref` to semantic-core | Unit | P1 | FR-004-CON-1 | ✅ |
| TC-045 | No shipped schema declares an observation key, so a declaration record cannot be read as an extraction from running code | Unit | P0 | FR-004-AC-15 | ✅ |
| TC-046 | `relations` is admitted by six object types and refused by four, both halves asserted | Integration | P1 | FR-004-AC-16 | ✅ |
| TC-050 | Every skeleton (ten plus three alternates) validates with no error | Integration | P0 | FR-005-AC-1 | ✅ |
| TC-051 | Table and `sysml` skeletons extract to identical normalized fields with the recorded forms | Integration | P0 | FR-005-AC-2, FR-005-CON-2 | ✅ |
| TC-052 | Under the skeleton bundle index every skeleton extracts with zero errors and zero unresolved tokens | Integration | P0 | FR-005-AC-3 | ✅ |
| TC-053 | Availability states per skeleton (fields, clauses, operations) match the type's declared set | Integration | P1 | FR-005-AC-4 | ✅ |
| TC-054 | Every negative fixture fails with its `expect:` code and the named cases exist | Integration | P0 | FR-005-AC-5 | ✅ #431 conditional xfail: the dangling-post fixture only |
| TC-055 | Every skeleton's H2 set is asserted by the manifest and includes every required heading | Unit | P1 | FR-005-AC-6 | ✅ |
| TC-056 | Every skeleton is placeholder-free with non-empty asserted sections | Unit | P2 | FR-005-AC-7 | ✅ |
| TC-057 | A Properties section holding both a table and a fence is refused at the second form | Integration | P1 | FR-005-CON-2 | ✅ |
| TC-058 | The repository carries no corpus path, no vendored neighbour fixture, no `/vendor/` path and no submodule, and every tracked path is part of the module's own surface (tree assertion over `git ls-files`, not a diff against a moving ref) | Unit | P2 | FR-005-CON-1 | ✅ falsified three ways and restored: a `corpus/` probe, a `fixtures/semantic-module` probe and a `.gitmodules` each turn it red |
| TC-059 | Skeleton titles are distinct `Identifier`s outside `KernelScalar`, and `object` equals `type` in every skeleton frontmatter | Unit | P1 | FR-005-AC-8 | ✅ |
| TC-065 | The action skeleton extracts one operation, the api endpoint at least one returning operation, the external contract at least one post-carrying operation | Integration | P1 | FR-005-AC-9 | ✅ #431 conditional xfail: the external contract case only |
| TC-070 | Quoin install roundtrip with state restore | Integration | P1 | IT-002-SC-01, IT-002-SC-02, IT-002-SC-03, IT-002-SC-04, IT-002-SC-05, IT-002-SC-06, FR-003-AC-5 | ✅ opt-in behind `QUOIN_INSTALL_ROUNDTRIP=1` |
| TC-071 | The packed npm tarball contains `manifest.yaml` and a sibling `schemas/<Model>.json` per export | Integration | P1 | FR-002-AC-7 | ✅ |
| TC-073 | `make schemas-check` names a stale committed schema with no emitted counterpart and writes nothing | Integration | P1 | FR-002-AC-9 | ✅ |
| TC-075 | A Node older than 20 fails the generator naming the required version | Integration | P2 | FR-002-AC-4 | ✅ |
| TC-076 | An unresolvable `@typespec/compiler` fails the generator naming the missing binary | Integration | P2 | FR-002-AC-4 | ✅ |
| TC-077 | A `tsp compile` failure exits non-zero and leaves the committed schemas and manifest byte-identical | Integration | P1 | FR-002-AC-4 | ✅ |
| TC-078 | A source emitting no module model exits non-zero naming the base it found nothing under | Integration | P1 | FR-002-AC-4 | ✅ |
| TC-080 | The interface `## Contract` YAML and its extracted `OperationDecl[]` agree on names, params, and returns | Integration | P0 | FR-006-AC-1 | ✅ |
| TC-081 | The data-schema `## Schema` fence and its `## Properties` table agree on property names and the required set | Integration | P0 | FR-006-AC-2 | ✅ |
| TC-082 | The queue `## Message Format` fence and its `## Properties` table agree on the key set | Integration | P1 | FR-006-AC-3 | ✅ |
| TC-083 | Every non-kernel `type.target` of the api-endpoint record resolves to a shipped data_schema title with zero unresolved findings | Integration | P0 | FR-006-AC-4 | ✅ |
| TC-084 | An api-endpoint fixture returning an undeclared token yields exactly one `semantic.unresolved-type` finding and the `unresolved` placeholder target | Integration | P1 | FR-006-AC-5 | ✅ |
| TC-085 | The `contract_yaml`, `schema_json`, and `message_schema` locators are still yield their fence text | Integration | P1 | FR-006-AC-6, FR-006-CON-1 | ✅ |
| TC-086 | Every FR-006 agreement assertion reads two sections of one authored artifact and no engine lowering | Static | P2 | FR-006-CON-2 | ✅ |
| TC-087 | An unrecognised generator argument exits non-zero and writes nothing | Integration | P2 | FR-002-AC-10 | ✅ |
| TC-090 | The Filament snapshot path refuses all fourteen reference-form `data_schema` values and accepts the same schemas resolved | Integration | P1 | FR-003-AC-8 | ✅ |
| TC-091 | The bundle index holds one entry per declaration id; a per-file index raises no `semantic.ambiguous-type` for a declaration against itself | Integration | P1 | FR-005-AC-10, FR-005-CON-3 | ✅ |
| TC-100 | Each systems kind is an exported object type whose `data_schema` names its model file | Unit | P0 | FR-007-AC-1 | ✅ |
| TC-101 | Each systems schema accepts the FR-152 record, refuses a missing member, `fields`, `operations`, `identityFields` and `{}`; a connection end admits a multiplicity and refuses a missing port or unknown key; direction enums are closed | Unit | P0 | FR-007-AC-2 | ✅ |
| TC-102 | Each systems kind has one required `table_row` locator asserting its columns, first column not an FR-075 key | Unit | P0 | FR-007-AC-3 | ✅ |
| TC-103 | FR-035 violations name no `construct` path; a `*` reference and an unknown member state are refused; each construct binds its FR-208 meaning; references name declared members and roles only | Integration | P0 | FR-007-AC-4 | ✅ |
| TC-104 | The systems edge verbs and roles are declared and are exactly the ones the systems kinds use | Unit | P1 | FR-007-AC-5 | ✅ |
| TC-105 | Each systems skeleton has an underscore id and extracts one row with one cell per column, each reference cell an artifact id or `<artifact id>/<member>` | Integration | P1 | FR-007-AC-6 | ✅ |
| TC-106 | Each systems skeleton validates with zero errors, its record carrying every FR-152 member | Integration | P1 | FR-007-AC-7 | ✅ |
| TC-107 | A renamed systems H2 fails as missing; reordered columns fail as a column mismatch | Integration | P1 | FR-007-AC-8 | ✅ |
| TC-108 | No systems schema or construct, `interface` included, declares a member beyond QSpec FR-152 | Unit | P0 | FR-007-CON-1 | ✅ |
| TC-109 | An interface with only fields, only operations, or both validates with its `featureOrder`; none without it; the construct makes both features optional and has no rule | Unit | P0 | FR-007-AC-9 | ✅ |
| TC-110 | An interface declares supertypes: `specializes` equals the spec-objects-business declaration, `interface` admits it to `interface`, the construct names `supertypes` optional, every construct's `references` entry names an FCD FR-142 reference member, the edge extracts and is not disallowed, and a disallowed verb warns | Integration | P0 | FR-007-AC-10 | ✅ |
| TC-111 | `ObjectId` states the frontmatter id pattern once and every object type's `id` locator carries it as `regex`; `ObjectFrontmatter.json` requires `id`, `title` and `type`; every shipped skeleton and fixture frontmatter validates; underscore and hyphenated ids validate, while a doubled hyphen is refused because its `id` does not match the pattern | Integration | P0 | FR-003-AC-9 | ✅ |
| TC-112 | The interface `features` locator is the required `Feature \| Kind` table under `Features`; the skeleton's rows name its operations in order; removing the section is refused as missing; the skeleton validates and its record's `featureOrder` follows the rows | Integration | P0 | FR-007-AC-11 | ✅ |
| TC-113 | `semantic.mappings` declares `generalization`; an interface with a `specializes` relationship extracts the edge and draws no `feature-not-extractable` diagnostic; a manifest copy with the token dropped reproduces that diagnostic | Integration | P0 | FR-007-AC-12 | ✅ |
| TC-130 | A record lacking the optional section key validates against each schema that requires no key, and a document without the optional section validates; a present key is still checked by its item rules | Unit | P0 | FR-009-AC-1, FR-009-AC-2 | ✅ |
| TC-131 | Each schema requires a key exactly when the manifest locator that feeds it (`operations` from `## Operations`, `fields` from `## Properties`, `clauses` from `## Invariants`, `featureOrder` from `## Features`) is required | Unit | P0 | FR-009-AC-3, FR-009-CON-1 | ✅ |
| TC-120 | `semantic.mappings` names `relationships` and `record-sections` | Unit | P0 | FR-008-AC-1 | ✅ |
| TC-121 | Each skeleton that authors a record key extracts exactly that key under the manifest's mappings, `available`, valid against its model, with zero errors; the values are the ones the skeleton states | Integration | P0 | FR-008-AC-2 | ✅ |
| TC-122 | A route naming an undeclared operation is refused as `route-operation-unknown` | Integration | P1 | FR-008-AC-3 | ✅ |
| TC-123 | `associated_types` comes from the `## Associated Types` table and never from the `## Contract` fence | Integration | P1 | FR-008-AC-4 | ✅ |
| TC-124 | The `## Layout` fence lowers to `records` and `endianness`; a `size` must name exactly one field; `## Endianness` is prose | Integration | P1 | FR-008-AC-5 | ✅ |
| TC-125 | A threshold without a `Status` is refused; a 429 row extracts its `on_exceeded`; a bullet-list `## Registration` is refused | Integration | P1 | FR-008-AC-6 | ✅ |
| TC-126 | A typed relation comes from a `## Relationships` row, and a `## Requires` list is prose | Integration | P1 | FR-008-AC-7 | ✅ |
| TC-140 | `edge_types` declares `realizes_requirement` with inverse `requirement_realized_by` and no `realizes` key; merging with spec-artifacts-iso raises no `DuplicateEdgeType` | Unit | P0 | FR-010-AC-1 | 🚧 |
| TC-141 | `part` and `connection` admit `realizes_requirement`; a part authoring it toward an `FR` extracts with no `disallowed-edge-type` | Integration | P0 | FR-010-AC-2 | 🚧 |
| TC-142 | The manifest declares exactly `fr-has-design-element` and `nfr-has-design-element` with the stated fields and lists them in `design_relations`; the module loads under quire-rs | Unit | P0 | FR-010-AC-3, FR-010-CON-1 | 🚧 |
| TC-143 | `quire relations --design --json` over a fixture reports an `FR` with a realizing part `covered` with the part's id and archetype, and an `FR` with none `uncovered` | Integration | P0 | FR-010-AC-4 | 🚧 |
| TC-144 | A requirement authoring `requirement_realized_by` toward a connection is `covered` with it; a pair authored both ways yields one element | Integration | P1 | FR-010-AC-5 | 🚧 |
| TC-145 | An `NFR` realized by an `ADR` is `covered`; the same edge authored by a document outside `to` leaves the `NFR` `uncovered` with no `kind_mismatch` and no `trace:target-kind-mismatch` | Integration | P1 | FR-010-AC-6 | 🚧 |
| TC-146 | With the architecture and requirements repositories loaded through `--repo`, an `FR` is `covered` by a part in the other; with the part's repository not loaded an edge authored by the part leaves the `FR` `uncovered` with no `dangling` entry, and an `FR` authoring `requirement_realized_by` toward it has the reference dangling as authored | Integration | P1 | FR-010-AC-7 | 🚧 |
| TC-147 | The `requirement-without-design` and `nfr-without-design` findings are advisory, and mapping a key `off` drops it | Integration | P1 | FR-010-AC-8 | 🚧 |
| TC-148 | Where no loaded module declares `ADR` and no `ADR` document exists, `trace:undeclared-relation-vocabulary` is reported for each relation naming it, advisory under both postures | Integration | P1 | FR-010-AC-9 | 🚧 |
| TC-149 | With an `obligations:` source minting the criterion ids, a part edge to a criterion id makes its `FR` `covered` with `realized_criteria`; without the source the edge is dangling and the `FR` `uncovered` | Integration | P1 | FR-010-AC-10 | 🚧 |

## Test Environment

Every `Integration` row that names Quire runs against the Quire wheel FR-005
Inputs pins: `quire` is a dev dependency resolved from `internal-pypi` by
`poetry install`. The suite **fails** rather than skips when
`extract_semantic` is absent, so no row here can be reported green without
the engine under test.

One row carries an explicit expected failure, naming the issue that owns it
and not skipped: TC-026 (`agent-ix/quire-rs#221` and `#394`, the refusal
names nothing). TC-091 passes: the engine collapses bundle-index entries that
share a declaration id (`agent-ix/quire-rs#398`).

Quire carries the
lowerings and gates that used to need a conditional probe: the systems tables
into the record (`agent-ix/quire-rs#446`, TC-106), the interface
`## Features` table into `featureOrder` (`agent-ix/quire-rs#448`, 
TC-025, TC-050, TC-112), reading a `Post:` line under an operation as a `post`
clause reference (`agent-ix/quire-rs#431`; TC-025, TC-050, TC-054's
dangling-post fixture case, TC-065's external-contract case), and
`ModelFeature::Generalization` refusing a `specializes` relationship with
`semantic.feature-not-extractable` when `generalization` is absent from
`semantic.mappings` (PR #432, `agent-ix/quire-rs#463`, TC-113's removal half).
`engine_reads_post_lines` in `tests/conftest.py` still probes the installed
engine before TC-054/TC-065 mark a case `xfail` — the probe is conditional
rather than deleted because a regression to an older wheel should fail loudly
rather than pass silently — but it holds and no case is
marked.

Two rows are opt-in rather than gated on an absent environment. TC-027 and
TC-070 write the operator's global `quoin module` store, so they run only
under `QUOIN_INSTALL_ROUNDTRIP=1`; each restores the prior entry's source, ref and
sha.

Rows over the record keys that Markdown authors (TC-120..TC-126) run the
engine's `record-sections` mapping, which quoin FR-121 and FR-122 specify and
`agent-ix/quire-rs` FR-081 implements, so the `quire` dev dependency must carry
that extractor. TC-033, TC-036, TC-038, TC-039, TC-040 and TC-043 stay
verified against hand-built records and say so: they are schema evidence, not
extraction evidence.

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

Four rows stay `🚧` and none of them is a coverage claim: TC-002, TC-003, TC-004 and TC-005, which need a running
`filament-core-service`, which
this repository cannot provision one. That is issue #1's debt, carried
forward.
