---
id: SR-006
title: "Failure-domain review of the #8 semantic module contract spec"
type: SpecReview
analysis: failure-domain
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-declare-architecture-objects-against-semantic-core.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-emitted-json-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-005-executable-skeletons.md, spec/functional/FR-006-architecture-lowerings.md, spec/non-functional/NFR-001-additive-compatibility.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-quoin-module-install.md, spec/tests.md"
review_set: all
---
# SR-006: Failure-domain review of the #8 semantic module contract spec

## Summary

Failure-domain analysis (extension-point failure policy, entity identity,
evaluation purity, topological robustness) of the issue #8 spec set, grounded
against the artifacts the requirements describe rather than against their
prose: the 31 emitted schemas and `toolchain.json` under
`spec_objects_architecture/schemas/`, `manifest.yaml` at version 0.3.0, the
thirteen skeletons and the ten `tests/fixtures/baseline-0.2.0/skeletons`,
`@agent-ix/semantic-core` `main.tsp` 0.1.0, the sibling module
`spec-objects-business`, and the engine the spec names as its validator
(quire-rs `src/semantic/contract.rs`, `resolver.rs`, `properties.rs`,
`context.rs`, `validate_document.rs`, `filament.rs`).

Sixteen findings: four high, seven medium, five low. The high findings are all
cases where the specification's own grounding is wrong about the engine or
about its measured population: NFR-001-AC-3 asks for a warning the engine
cannot emit on the population NFR-001 defines; the additive-compatibility
claim is measured over a path that never exercises the one consumer FR-001
exists for; the three alternate skeletons ship duplicate bundle identities
that make every `Type` cell naming them ambiguous under the engine's own
index; and FR-003 grants an expected-failure exemption for two refusals the
loader in fact reports by name.

## Verdict

Not ready for `spec-to-plan` until FND-200..FND-203 are dispositioned. Each
has a concrete disposition: correct NFR-001's population or its metric,
measure (or scope out by an owned upstream dependency) the Filament snapshot
path, state the bundle-index identity rule for the alternates, and withdraw
the FR-003-AC-6 exemption. FND-204..FND-210 are medium and each has a
one-paragraph fix. The low findings are proposed additions, not blockers.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-200 | high | NFR-001-AC-3 is unsatisfiable on the population NFR-001 defines: `validate_document.rs` runs `semantic_findings` only for a document whose frontmatter `object:` resolves to an archetype, and NFR-001's own Verification asserts no 0.2.0 skeleton carries `object:`. All ten `tests/fixtures/baseline-0.2.0/skeletons` confirm it (`grep -c '^object:'` is 0 for each), so the semantic layer never runs and the `semantic.legacy-properties-form` count is 0, not 1. Only `ui_component.md` even carries a Props section, so "each legacy-form skeleton" is at most one file. | NFR-001 Verification, NFR-001-AC-2, NFR-001-AC-3, Measurement row 3, TC-062 | wrong-requirement |
| FND-201 | high | The additive-compatibility claim is measured over a path that never exercises the consumer FR-001 exists for. Moving `data_schema` from inline `{type: object}` to the reference form makes quire's Filament snapshot path refuse every object type: `compile_object_type_snapshots` emits `semantic.data-schema-unresolved-reference` at error severity for a non-inline `data_schema` and inserts the type into `refused`, after which an artifact of that type produces "no node". Until `filament-core-service#23` lands, activating 0.3.0 empties the architecture graph of all ten types — the resource-identity change the ticket's gate says needs controlled-corpus evidence. NFR-001's population is skeletons validated through the Registry path, which never reaches this code. | NFR-001 Statement/Scope, spec.md Out of Scope (filament-core-service#23), FR-001-AC-4, IT-001-SC-02 | missing-requirement |
| FND-202 | high | The three alternate skeletons ship duplicate bundle identities by intent, and the engine's index does not dedupe. `data_schema.sysml.md`, `queue.sysml.md` and `ui_component.sysml.md` carry the same `id` and `title` as their table counterparts (FR-005: "two files under one id by intent"). `BundleIndex::from_documents` pushes one entry per `object:`-carrying document with no dedupe, and `properties.rs` step 3 fails a name matched by more than one object with `semantic.ambiguous-type` at error severity, returning no `TypeRef`. So the api_endpoint skeleton's `Returns: ArtifactRecord` is ambiguous, not resolved — breaking FR-005-AC-3 ("zero error diagnostics"), FR-006-AC-4 and US-001-EX-2. The repository's own evidence hides this: `tests/conftest.py::bundle_index` skips a document whose `id` was already seen, so the green run uses an index the engine would never build. | FR-005 Behavior (alternate-skeleton bullet), FR-005-AC-2, FR-005-AC-3, FR-006 Behavior (bundle index bullet), FR-006-AC-4, US-001-EX-2, TC-052, TC-083 | missing-requirement |
| FND-203 | high | FR-003 exempts the naming half of FR-003-AC-6 as blocked on `quire-rs#221`/`#394`, but the loader path FR-003-AC-4 uses reports both refusals by name. `contract.rs::read_semantic_block` validates the block against the vendored manifest schema (`additionalProperties: false`) and maps the violation to `semantic.unknown-key` with the message "unknown key(s) foo"; `resolver.rs` emits `semantic.data-schema-digest-mismatch` naming the file and both digests. The silent behaviour is the Filament snapshot path, a different consumer. Under FR-005's own rule that only a criterion the spec names as blocked may be exempt, an exemption granted where evidence exists suppresses a test that would pass. | FR-003 Behavior (measured-against bullet), FR-003-AC-6, FR-005 Behavior (last bullet), spec.md Out of Scope (quire-rs#221, #394) | wrong-requirement |
| FND-204 | medium | The ten role schemas do not partition records, and FR-004's disclaimer names the wrong separators. `{operations: [one op with returns]}` validates against `ApiEndpoint`, `Action` and `Interface` alike; `{clauses: [one]}` validates against both `BinaryFormat` and `RateLimit`; `{operations: [op with post], clauses: [one]}` validates against both `ExternalContract` and `ExtensionPoint`. FR-004 attributes the non-disjointness to `routes`, `registration` and `versioning`, which explains none of these three overlaps (they turn on `triggers`, `associated_types`, `records`/`endianness` and `thresholds`). Nothing in the spec states that the schema is selected by the artifact's frontmatter `object:` and never inferred from the record, which is the only thing that makes the roles distinguishable. | FR-004 Description, FR-004-AC-1, StR-001-VC-3, US-001 Context | wrong-requirement |
| FND-205 | medium | The `interface` skeleton's two sections already disagree, and FR-006-AC-1 is written not to see it. `## Contract` declares `output: PreparedQuery`, `output: score`, `output: scores`; `## Operations` declares `Returns: Bytes[1..1]`, `Decimal(18,9)[1..1]`, `Decimal(18,9)[1..* ordered]`. AC-1 compares operation names, param names, and which operations declare a return — never the return type or target — so the shipped disagreement passes. Two further gaps in the same lowering: `associated_types: [PreparedQuery]` is a list of bare strings while `Interface.associated_types` items are `TypeRef` objects and `PreparedQuery` is no shipped title, so the FR-006 mapping is type-incorrect; and the fence's `invariants:` has an obvious counterpart in the optional `Interface.clauses` key, yet FR-005 forbids `## Invariants` on `interface`, making `clauses` unreachable for that type and dropping the declared invariants with no diagnostic. | FR-006 Behavior (contract_yaml mapping, unmapped-key bullet), FR-006-AC-1, FR-005 Behavior (no-Invariants bullet), skeletons/interface.md, Interface.json | missing-requirement |
| FND-206 | medium | The digest chain stops at the ten exported schemas. `manifest.yaml` carries a `data_schema.digest` for `ApiEndpoint`..`RateLimit` only; the 21 support schemas that decide what those types refuse — `ReturningOperation`, `GuaranteedOperation`, `IdentityField`, `RouteDecl`, `Threshold`, `ExceedResponse`, `RecordLayout`, `LayoutField`, the five policy models and the nine enums — are `$ref` targets with no digest anywhere the installer reads. `toolchain.json` hashes all 31 but is not referenced from the manifest and no requirement makes Quoin or Quire verify it, so a drifted or edited support schema installs clean while silently changing every exported type's rules; `make schemas-check` is a local, same-tree guard only. IT-002's Objective nonetheless claims Quoin verifies "every digest and `$ref`". | FR-002 Outputs, FR-003 Behavior (reference-form bullet), FR-003-AC-2, IT-002 Objective, IT-002-SC-02 | missing-requirement |
| FND-207 | medium | The `$id` immutability claim is only version-gated, so it does not hold. FR-002 justifies embedding the manifest `version` in the `$id` base on the ground that "one schema URL names exactly one immutable byte sequence", but nothing requires a `version` bump when a TypeSpec edit changes the emitted bytes at the same version — a new support model, a tightened `Threshold`, an edited `description`. `make schemas-check` only compares the tree against itself, so two published 0.3.0 trees can serve different bytes under one `$id`. The same edit rewrites `data_schema.digest` values in `manifest.yaml`, so a same-name, same-version manifest activates with a different SHA-256 content hash and FR-001 defines idempotency only for an identical re-activation: whether filament-core overwrites, errors, or duplicates is unstated. | FR-002 Behavior ($id base bullet, bump procedure), FR-002-CON-5, FR-002-AC-8, FR-001 Behavior, FR-001-AC-3 | missing-requirement |
| FND-208 | medium | Three independent copies of semantic-core 0.1.0 decide every `$ref`ed rule, with no cross-check. The emitter compiles against the npm package pinned in `package-lock.json`; quire validates against `schemas/vendored/semantic-core/0.1.0/` compiled into the binary; Quoin vendors its own. `contract.rs` matches `semantic_core` by string (`"0.1.0" => Some(SEMANTIC_CORE_0_1_0)`), never by digest, so a divergent vendored bundle validates differently with no diagnostic and no `$id` change. FR-003 Inputs makes exactly this argument for the module-manifest schema — naming revision `a77f31e` and asserting Quoin and Quire vendor it byte-identically — and makes none for semantic-core, whose bytes matter more. | FR-002 Inputs, FR-002-AC-3, FR-003 Inputs, FR-004 Behavior ($ref bullet) | missing-requirement |
| FND-209 | medium | The Quire dependency has a version range where its contract has a pin, and `make dev-quire` has no failure policy. FR-005 Inputs says "0.46.0 or later", FR-003 measures behaviour "against quire 0.46.0", and FR-005 Dependencies concedes that `semantic.record-invalid` — the diagnostic FR-005 Outputs and FR-005-AC-1 rest on — exists in quire-rs source but in no quire-rs acceptance criterion. FR-005-AC-5 then asserts ten diagnostic-code strings against that open range: a later wheel that renames a code turns the negatives red for the wrong reason, and because the assertion is "the message contains the `expect:` code", a fixture failing for a different rule passes. Nothing says what `make dev-quire` does when the download fails or installs a different version. | FR-005 Inputs, FR-005 Behavior (dev-quire and negative-fixture bullets), FR-005-AC-5, FR-005 Dependencies (unpinned neighbour contract), FR-003 Behavior | missing-requirement |
| FND-210 | medium | The evidence base for the criteria this analysis turns on is claimed but absent. `spec/tests.md` marks TC-030..TC-065 and TC-080..TC-086 ✅, but `tests/` carries assertions tagged only for FR-002-AC-1..9, FR-003-AC-1..4/6/7 and FR-005-AC-3; no test bears FR-004-AC-1..14, FR-005-AC-1/2/4..9, FR-006-AC-1..6 or NFR-001-AC-1..5. Every finding above that a test would have caught (FND-200, FND-202, FND-205) sits behind a row marked green. | tests.md rows TC-030..TC-065, TC-080..TC-086; tests/test_manifest_semantic.py, tests/test_schema_emission.py, tests/test_skeletons_and_validate.py | correct-requirement-no-evidence |
| FND-211 | medium | Both integration tests mutate shared state and only one restores it. IT-002 restores the operator's global `quoin module` store at step 5, but a kill between steps 2 and 5 leaves every other repository on the machine resolving this branch's module, and no criterion covers a restore that itself fails (SC-06 asserts only that the step runs). IT-001 has no cleanup step at all while requiring an empty `modules` registry as a precondition, so two runs against the same cluster are not independent and the second cannot satisfy its own precondition. | IT-001 Preconditions, IT-001 Test Procedure, IT-002 Test Procedure step 5, IT-002-SC-05, IT-002-SC-06 | missing-requirement |
| FND-212 | low | Uniqueness keys inside a record are semantic-core reader rules the module never restates or tests: `FieldDecl` is "unique by name" and `OperationDecl` "params unique by name" (main.tsp), neither expressible in the emitted schemas. FR-006-AC-1/AC-2/AC-3 compare a fence's key set — inherently unique — against an extracted list, so a duplicated field, param or operation name passes every agreement test the module ships. | FR-004 Inputs, FR-006-AC-1, FR-006-AC-2, FR-006-AC-3, semantic-core main.tsp FieldDecl/OperationDecl | missing-requirement |
| FND-213 | low | Two intra-record cross-references are stated as reader rules with no well-formedness constraint. `RouteDecl.operation` must name an `operations[].name` of the same record, and `LayoutField.size` may name a sibling field carrying the length — the latter can cycle (field `a` sized by `b`, `b` sized by `a`) and nothing bounds a reader that follows it. `RecordLayout` likewise places no rule on overlapping offsets or on `size` versus the extent of its fields, so a layout can be internally contradictory and still validate. | FR-004 Behavior (`RouteDecl`, `RecordLayout`/`LayoutField` bullets), LayoutField.json, RecordLayout.json | missing-requirement |
| FND-214 | low | The `data_schema` record carries two titles with no agreement rule, and kernel shadowing is fixed for skeletons only. FR-006 registers the record under `type/<title>` without saying whether that is the frontmatter `title` or the `## Schema` fence's `"title"` (they agree in `data_schema.md` by accident, and FR-006-AC-2 compares property names and the required set, never the title). Separately, `properties.rs` resolves kernel scalars before bundle objects, so an authored `data_schema` titled `String`, `Bytes` or `Timestamp` is silently reclassified as a kernel scalar; FR-005-AC-8 bars that only for the shipped skeletons, and FR-006-AC-4 ("every non-kernel target resolves") passes vacuously because the collision makes the token kernel. | FR-006 Behavior (bundle index bullet), FR-006-AC-2, FR-006-AC-4, FR-005-AC-8, skeletons/data_schema.md | missing-requirement |
| FND-215 | low | `OperationDecl.params` is required in semantic-core, but FR-005 authors the param table as "optional" and FR-006's mapping is silent on an operation with no inputs. Whether a param-less operation lowers to `params: []` or omits the key is the difference between a valid record and `semantic.record-invalid`, and the module ships no param-less operation to settle it. | FR-005 Behavior (Operations bullet), FR-006 Behavior (contract_yaml mapping), semantic-core main.tsp OperationDecl | missing-requirement |
| FND-216 | low | Three smaller mismatches between the requirements and the shipped bytes. FR-002-AC-1 says `schemas/` "holds exactly the files `toolchain.json` lists"; `toolchain.json` lists 31 files and does not list itself, so the directory holds 32 and a test written to the criterion fails on `toolchain.json`. FR-002 requires the generator to write "under `spec_objects_architecture/schemas/` only" and `--check` to "write no file", with no carve-out for the directory `tsp compile` must emit into. And FR-004 says every cross-reference "SHALL be a `SemanticId` or `KernelScalar`", while in the shipped schemas only `TypeRef.target` admits a `KernelScalar` — `requires`, `carries`, `renders`, `throttles`, `serializes`, `triggers`, `exposes`, `provider` and `RelationDecl.target` are `SemanticId` alone. | FR-002-AC-1, FR-002 Behavior (write-scope and `--check` bullets), FR-004 Behavior (cross-reference bullet), toolchain.json, ApiEndpoint.json | wrong-requirement |

## Finding Detail

### FND-200 (high): NFR-001-AC-3 asks for a warning the engine cannot emit here

`validate_document.rs` reaches the semantic layer only through one gate:

```
if let Some(arch) = object_archetype {
    if let Some(module) = registry.semantic_module(&arch.module) {
        semantic_findings(...)
```

`object_archetype` is `Some` only when frontmatter carries `object:` and the
name resolves. `semantic.legacy-properties-form` is raised inside
`properties.rs`, which runs only under `extract_semantic`, which runs only
inside `semantic_findings`. NFR-001's own Verification section states the
premise that makes AC-2 hold — "no 0.2.0 skeleton carries a frontmatter
`object:` key, so Quire runs headings-only validation on it" — and the
checked-in baseline confirms it: none of the ten files in
`tests/fixtures/baseline-0.2.0/skeletons` carries `object:`. The same premise
makes AC-3 unreachable: zero semantic diagnostics of any code, so the metric
"exactly 1 `semantic.legacy-properties-form` warning" cannot be met.

A second, independent problem sits behind it: of the ten baseline files, only
`ui_component.md` carries a Properties-shaped section at all (`## Props`), so
"each legacy-form skeleton" quantifies over at most one file even if `object:`
were added.

Disposition: either drop AC-3 and its metric row (the honest statement is that
0.3.0 is additive because the 0.2.0 population never enters the semantic
layer), or move the warning claim onto a fixture that does declare `object:`
and carries a legacy Properties block — in which case FND-201 and the
`quire-rs#391` expected failure both apply to it.

### FND-201 (high): additive compatibility is not measured on the Filament path

`filament.rs::compile_object_type_snapshots` is the code filament-core reaches
through when it extracts artifacts against an activated module. Its first act
per snapshot is:

- if `data_schema` is not `DataSchemaForm::Inline`, push
  `semantic.data-schema-unresolved-reference` at error severity, insert the
  type into `refused`, and `continue`;
- a refused type then produces no node at extraction time
  ("FR-069: a refused snapshot was diagnosed at compile; no node").

At 0.2.0 every object type carries inline `data_schema: {type: object}` and
compiles. At 0.3.0 every one of the ten carries the reference form, so on this
path all ten are refused and every architecture artifact in the corpus stops
producing a node. `spec.md` records the dependency
(`filament-core-service#23`, "until it lands the service stores the reference
verbatim") but reads it as a deferral with no consequence, and NFR-001 measures
only skeletons validated through `Registry`/`validate_document`, which resolves
the reference from disk and never reaches this branch.

Disposition: either state the Filament-path regression in NFR-001's Scope and
carry it as a named expected failure against `filament-core-service#23`, or
make that issue a blocking upstream dependency of FR-003 rather than an
out-of-scope note.

### FND-202 (high): one id, two documents, an ambiguous bundle

The three alternate skeletons are deliberate duplicates:

- `data_schema.md` and `data_schema.sysml.md`: `id: data-schema-001`, `title: ArtifactRecord`
- `queue.md` and `queue.sysml.md`: `id: queue-001`, `title: ArtifactIngestQueue`
- `ui_component.md` and `ui_component.sysml.md`: `id: ui-component-001`, `title: ArtifactTable`

`context.rs::BundleIndex::from_documents` appends one `BundleEntry` per
document carrying `object:` and applies no dedupe by `id`. `properties.rs`
resolves a `Type` token by kernel scalar, then object id, then object name; the
name step collects every matching object and, when more than one matches,
raises `semantic.ambiguous-type` at error severity and returns no `TypeRef`.
`skeletons/api_endpoint.md` declares `Returns: ArtifactRecord[1..1]` twice, so
under an index built from all thirteen skeletons the api_endpoint record
carries an error and no resolved target.

The repository's green evidence comes from a different index.
`tests/conftest.py::bundle_index`, whose docstring is "A bundle index built
from the skeleton frontmatter (FR-005-AC-3)", skips any document whose `id` was
already seen. The engine does not.

Disposition: state the rule the spec relies on — either the alternates are
excluded from any bundle index the module builds (and FR-005-AC-3/FR-006-AC-4
say so), or they take distinct `id`s and `title`s, which FR-005-AC-2's
identical-fields obligation would then have to name explicitly rather than
inherit from a shared id.

### FND-203 (high): the exemption is granted on the wrong path

FR-003 Behavior states that at quire 0.46.0 "Both refusals are silent — no
diagnostic names the offending key, path, or digest". On the loader path
FR-003-AC-4 exercises, both are named:

- `contract.rs::read_semantic_block` compiles
  `module-manifest.schema.json`'s `properties.semantic` (which is
  `additionalProperties: false`) and maps an `AdditionalProperties` violation
  to `SemanticFailure::error("semantic.unknown-key", …, "unknown key(s) foo")`;
- `resolver.rs` compares the file's SHA-256 to the manifest digest and, on
  mismatch, raises `semantic.data-schema-digest-mismatch` with "schema file
  `<rel>` hashes to `<actual>`, manifest records `<recorded>`".

`Registry::load_from` reaches both through `loader/mod.rs`, which calls
`read_semantic_block` directly. The silence FR-003 describes belongs to
`filament.rs`'s snapshot path, which is a different consumer with a different
issue (`quire-rs#221`). Carrying FR-003-AC-6 as an expected failure therefore
records a defect where the module has evidence, and FR-005's exemption rule —
"Only a criterion this specification names as blocked SHALL be exempt" — makes
that a suppressed test rather than a bookkeeping error.

### FND-204 (medium): the ten roles are not a partition

Reading the shipped `required`, `contains` and seal keywords rather than the
table prose, three minimal records each satisfy more than one type:

- `{"operations": [{"name":"f","params":[],"returns":{"target":"String"}}]}`
  validates against `ApiEndpoint` (≥1 operation, one returning), `Action`
  (exactly one) and `Interface` (≥1 operation).
- `{"clauses": [{"language":"ocl","clauseId":"c1"}]}` validates against both
  `BinaryFormat` and `RateLimit`, whose required sets are identical and whose
  optional keys are disjoint.
- `{"operations": [op with a `post`], "clauses": [one]}` validates against both
  `ExternalContract` and `ExtensionPoint`.

`{}` is refused by all ten, as FR-004-CON-2 claims — every model has a
non-empty `required` — so that criterion is sound. What is not sound is
FR-004's account of why disjointness fails: it names `routes`, `registration`
and `versioning`, none of which separates any of the three overlaps above. The
missing statement is the one that makes the design work: the schema is chosen
by the artifact's frontmatter `object:`, and no consumer may infer an object
type from a record. Without it, StR-001-VC-3's "distinguishable by schema
alone" is true only for the one pair it names.

### FND-205 (medium): the interface lowering disagrees today

`skeletons/interface.md` `## Contract` declares `output: PreparedQuery` for
`prepare_ip_query`, while `## Operations` declares `Returns: Bytes[1..1]` for
the same operation; `score_ip_candidate` and `score_ip_batch` disagree the same
way (`score`/`scores` versus `Decimal(18,9)`). FR-006-AC-1 compares operation
names, param names per operation, and "the same set of operations that declare
a return" — three predicates all of which hold — so the module's flagship
lowering ships with its two views disagreeing on every return type and its own
agreement test green by construction.

Two adjacent gaps in the same fence: `associated_types: [PreparedQuery]` is a
list of bare strings, while `Interface.associated_types` items are
`$ref`erenced `TypeRef` objects and `PreparedQuery` is not a shipped skeleton
title, so FR-006's "`associated_types[]` to the record's `associated_types`
key" is not a well-typed mapping; and the fence's two `invariants:` entries
have a real counterpart in `Interface.clauses` (optional in the shipped
schema), yet FR-005 requires the `interface` skeleton to carry no
`## Invariants`, so nothing an interface author writes can ever reach that key.

### FND-206 (medium): the digest chain covers ten of thirty-one files

`manifest.yaml` records a digest for `ApiEndpoint.json`, `DataSchema.json`,
`Queue.json`, `Action.json`, `UiComponent.json`, `Interface.json`,
`ExternalContract.json`, `ExtensionPoint.json`, `BinaryFormat.json` and
`RateLimit.json`. The other 21 shipped files carry none, yet they hold the
rules the ten enforce: `ReturningOperation.json` is what makes an endpoint
answer, `GuaranteedOperation.json` what makes an external contract guarantee,
`IdentityField.json` what makes a queue partitionable, and the nine enums what
close each policy vocabulary. `resolver.rs` reads them through the sibling
resolver and never hashes them.

`toolchain.json` does hash all 31 (`sha256:d56db468…`), but no requirement
makes any installer read it and the manifest does not reference it, so the only
thing that checks a support schema is `make schemas-check` inside a checkout —
which compares the tree against a fresh emission, not against what shipped.
IT-002's Objective ("verify every digest and `$ref`") overstates what Quoin can
verify from the manifest alone.

### FND-207 (medium): "$id names one byte sequence" is not enforced

FR-002 spends a paragraph justifying the version-embedded `$id` base by the
property it buys — "it makes one schema URL name exactly one immutable byte
sequence, so a downstream fixture reader that pinned a version can never
silently read a later version's bytes under the same URL" — and then requires a
coordinated rewrite only when the manifest `version` changes. Nothing requires
the version to change when the bytes do. Adding a support model, tightening
`Threshold.limit`, or editing a `description` re-emits files under the same
`https://…/0.3.0/` base, and `make schemas-check` passes because it only asks
whether the committed tree equals a fresh emission of the current source.

The same edit propagates into `manifest.yaml`, whose `data_schema.digest`
values FR-002 rewrites. FR-001 defines idempotent re-activation as "same
content hash"; a same-name, same-version manifest with different digests is a
different content hash, and no requirement says what filament-core does with
it — overwrite, refuse, or create a second row. FR-001-AC-3 tests only the
identical case.

### FND-208 (medium): three copies of the grammar, matched by string

Every rule the ten schemas enforce over `fields`, `params`, `clauses`,
`operations`, `relations` and `associated_types` is a `$ref` into
`https://schemas.agent-ix.org/semantic-core/0.1.0/`. Three separate byte
sequences answer to that URL in this system: the npm package
`@agent-ix/semantic-core@0.1.0` the emitter compiles against and the tests
resolve `$ref`s from; `quire-rs/schemas/vendored/semantic-core/0.1.0/`,
compiled into the engine binary via `include_str!`; and Quoin's own vendored
copy. `contract.rs` accepts the manifest's `semantic_core` value by exact
string match against a table of vendored versions, and `resolver.rs` resolves
every core `$ref` out of that bundle. No digest crosses the boundary.

FR-003 Inputs already makes this argument well for the manifest schema —
naming the revision `a77f31e` and asserting Quoin and Quire vendor it
byte-identically, so "a consumer vendoring an older copy is a skew defect on
that consumer". The same sentence is missing for semantic-core, where the
consequence is not a rejected manifest but a record that validates against
different rules than the ones the module tested.

### FND-209 (medium): an open version range under a pinned contract

FR-005 Inputs admits "the Quire wheel 0.46.0 or later"; FR-003 Behavior
measures loader behaviour "against quire 0.46.0"; FR-005 Dependencies concedes
that `semantic.record-invalid` — named in FR-005 Outputs, FR-005-AC-1 and eight
of the ten negative fixtures — "exists in quire-rs source but in no quire-rs
acceptance criterion". FR-005-AC-5 then asserts ten literal diagnostic codes
against that open range, with the weakest possible predicate: the error message
"contains its `expect:` code". A fixture that fails for a different schema rule
still passes, and a later wheel that renames or re-severities a code fails the
suite for a reason unrelated to this module.

`make dev-quire` is specified as existing, not as behaving: nothing says what
it does when the wheel is unavailable on `pypi.ix`, when it installs a version
outside the range, or when a previously installed wheel already satisfies the
import but not the contract. FR-005's fail-don't-skip rule covers only the case
where `extract_semantic` is absent.

### FND-210 (medium): green rows with no test behind them

`spec/tests.md` marks 68 rows ✅ and 15 🚧. Tagged assertions in `tests/`
cover FR-002-AC-1..9, FR-003-AC-1..4, FR-003-AC-6, FR-003-AC-7 and
FR-005-AC-3. No test bears FR-004-AC-1..14, FR-005-AC-1, FR-005-AC-2,
FR-005-AC-4..9, FR-006-AC-1..6, or NFR-001-AC-1..5, yet TC-030..TC-065 and
TC-080..TC-086 are all marked ✅. FND-200 (TC-062), FND-202 (TC-052, TC-083)
and FND-205 (TC-080) each sit behind such a row: the failure-domain problems
this review names are precisely the ones a run of those rows would have
surfaced.

### FND-211 (medium): shared-state tests with one-sided cleanup

IT-002 installs into the operator's global Quoin module store and restores it
at step 5, with SC-06 asserting only that the restore step runs. Nothing covers
a restore that fails, and nothing isolates the store: between steps 2 and 5 —
or permanently, after an interrupted run — every other repository on the
machine resolves `spec-objects-architecture` from this branch. A scratch module
root for the duration of the test would remove the hazard and the restore step
together.

IT-001 has the same shape without the mitigation: it requires "an empty
`modules` registry so the presence of newly created rows is meaningful" and
never removes what it activates, so the test can satisfy its own precondition
at most once per cluster.
