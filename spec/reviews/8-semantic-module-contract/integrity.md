---
id: SR-002
title: "Integrity review of the #8 semantic module contract spec"
type: SpecReview
analysis: integrity
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-declare-architecture-objects-against-semantic-core.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-emitted-json-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-005-executable-skeletons.md, spec/functional/FR-006-architecture-lowerings.md, spec/non-functional/NFR-001-additive-compatibility.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-quoin-module-install.md, spec/tests.md"
review_set: all
---
# SR-002: Integrity review of the #8 semantic module contract spec

## Summary

Integrity gate (completeness, consistency, atomicity/testability) over the
thirteen artifacts that deliver `agent-ix/spec-objects-architecture#8`,
grounded against the upstream contract: `semantic-core` `main.tsp`
(filament-core-data), quoin FR-070..FR-075, quire-rs FR-069..FR-072, the
filament-core-data target registry (`schema/semantic/v1/common.schema.json`),
this repo's `spec_objects_architecture/manifest.yaml` and `skeletons/`, and
the sibling module `agent-ix/spec-objects-business#4` with its own review set.

The spec is strong where the sibling was weak: every acceptance criterion,
named constraint and NFR metric has a Test Matrix row (verified row by row);
FR-004 states the emitter decorator recipe so the sibling's FND-121
expressibility gap does not recur; the item rules need no double-`contains`,
so no `@extension("allOf", …)` escape is required; NFR-001 carries a
`constrains` relationship to FR-004; the fail-not-skip rule replaces the
sibling's skip escape; skeleton `title`s are pinned as unique `Identifier`s,
which is also the tie-break for quire-rs `semantic.ambiguous-type`; and the
spec is honest about `semantic.record-invalid` having no upstream acceptance
criterion.

The gate does not pass. Three highs: FR-004's `relations` rule contradicts its
own table (the shipped schemas follow the table); NFR-001's Verification
paragraph makes NFR-001-AC-3 unachievable and NFR-001-AC-2 vacuous; and the
FR-001/IT-001 pair was never carried forward from the sibling's remediation,
so `spec.md` cites two criteria that do not say what it claims. Six mediums
(two uncovered ticket acceptance criteria, an unowned duplicate authority on
three skeletons, an unowned NFR baseline artifact, FR-002/FR-005 Behavior
obligations with no criterion, and a `make lint`/CON-4 contradiction) and
seven lows follow.

## Verdict

**Not ready for `spec-to-plan`.** FND-120 and FND-121 are one-requirement
edits but they change what the schemas and the NFR fixture must be, so resolve
both before tasking FR-004 and NFR-001. FND-122 is a carry-forward the sibling
already worked out; apply its text. The remaining mediums are new AC/TC rows
or one-paragraph additions. Once FND-120..FND-131 are dispositioned the matrix
can be regenerated and the plan started.

## Traceability Matrix

Completeness deliverable: US -> FR -> StR -> verification. "StR (via US)" means
the only StR link is transitive through US-001.

| US | FR | StR | Verification (AC/CON -> TC) | Gap |
|---|---|---|---|---|
| — | FR-001 | none in frontmatter; `tests.md` asserts StR-001 | AC-1..4 -> TC-001..004; IT-001-SC-01..03 -> TC-002, TC-004, TC-003 | FND-122 |
| US-001 | FR-002 | StR-001 (via US) | AC-1..9 -> TC-010..015, TC-071..073; CON-1..5 -> TC-017, TC-018, TC-016, TC-019, TC-072/074 | FND-127, FND-128 |
| US-001 | FR-003 | StR-001 (via US) | AC-1..7 -> TC-020..028; CON-1 -> TC-020; CON-2 -> TC-023; IT-002-SC-01..06 -> TC-070 | FND-132 |
| US-001 | FR-004 | StR-001 (via US) | AC-1..14 -> TC-030..043; CON-1..3 -> TC-044, TC-041, TC-043 | FND-120, FND-123, FND-124 |
| US-001 | FR-005 | StR-001 (via US) | AC-1..9 -> TC-050..056, TC-059, TC-065; CON-1 -> TC-058; CON-2 -> TC-051, TC-057 | FND-125, FND-127 |
| US-001 | FR-006 | StR-001 (via US) | AC-1..6 -> TC-080..085; CON-1 -> TC-085; CON-2 -> TC-086 | — |
| — | NFR-001 (constrains FR-003, FR-004, FR-005, FR-006) | — | AC-1..5 -> TC-060..064 | FND-121, FND-126 |
| StR-001-VC-1 | — | — | TC-005 | FND-131 |
| StR-001-VC-2 | — | — | TC-006 | FND-130 |
| StR-001-VC-3 | — | — | TC-007 | FND-131 |

Completeness holds at the AC level: every FR/NFR/IT criterion and every named
constraint maps to at least one test case, and the matrix's own claim to that
effect is true — the sibling's FND-123 does not recur. Every NFR is explicitly
scoped (NFR-001 lists `manifest.yaml`, the schemas and the skeletons) and is
referenced by the four FRs it constrains. The two structural gaps are FR-001,
which reaches no StR or US through its frontmatter, and the Behavior
obligations of FND-127, which are normative statements with no criterion.

## Hidden Assumption Probes

| FR | Pattern | Result |
|---|---|---|
| FR-002 | Delegates to external CLIs (`node`, `tsp`) | Behavior pins Node 20, states detection, and states the error naming the required version or the missing binary. OK |
| FR-002 | Depends on a registry-scoped package (`@agent-ix/semantic-core` on npm.ix) | CON-4 states the resolution discipline, but places it outside the GitHub workflow while Behavior binds the check to `make lint` (FND-128) |
| FR-002 | Generation command | Build (`make schemas`) and check (`--check`) modes are both specified; no interactive mode is needed. OK |
| FR-002 | Writes into a hand-authored file | The digest rewrite is scoped to `data_schema.digest`, but nothing states it is textual; the manifest carries ten YAML anchor uses and 29 comment lines a structural rewrite would drop (FND-134) |
| FR-003 | Lookup over two consumers (Quoin install, Quire load) | No tie-break needed — both reject. CON-1 scopes Quire's refusal here and allocates Quoin's to the neighbour, evidenced only by IT-002's clean install. OK |
| FR-003 | Declares values from an upstream vocabulary | `targets: [json-schema, markdown]` are both in the filament-core-data target registry (`common.schema.json` `target` + `representationFormat`). `mappings` names have no registry (FND-133) |
| FR-004 | Depends on emitter capability under CON-1 (official emitter only) | Every rule is one `contains` predicate plus `@minItems`/`@maxItems`; `@contains(IdentityField) @minContains(0) @maxContains(0)` covers the ui-component rule. No `allOf` escape is needed. OK |
| FR-004 | Resolves tokens over a bundle index | A token matching two bundle names is quire-rs `semantic.ambiguous-type`; FR-005-AC-8's unique-title rule is the tie-break, and it is stated. OK |
| FR-005 | Depends on a package version on no committable index (Quire 0.46.0) | Pinned in Inputs, provisioned by `make dev-quire`, fail-not-skip stated, `agent-ix/quire-rs#392` named — but the rule itself has no AC (FND-127) |
| FR-005 | Depends on a diagnostic with no upstream criterion (`semantic.record-invalid`) | Declared as an unpinned neighbour contract with `agent-ix/quire-rs#391` named. Confirmed: the code appears in no quoin or quire-rs acceptance criterion. OK — the spec says so |
| FR-001 | Calls an external service with a changed payload | Unaddressed: FR-001 and IT-001 are the unchanged 0.2.0 artifacts, and no revision of the service is pinned (FND-122) |

## Failure Domain Check

- **Extension failures.** The schemas are sealed (`unevaluatedProperties: {not: {}}`, confirmed in the shipped files), so any key FR-004 does not list fails every record. FR-004 lists the forward-compatible optional keys explicitly and requires them optional — except `relations`, where the Behavior rule and the table disagree (FND-120), and the `references` edge, which has no record representation on any type (FND-123).
- **Identity keys.** `identity: true` on `FieldDecl` is the only identity marker; FR-004 defines its reading once and states that a semantic-core release rendering `identity: false` is a breaking change requiring a version bump. Skeleton `title` as the resolution key is pinned by FR-005-AC-8 (`Identifier`, unique, not a `KernelScalar` name); the sibling's FND-132 does not recur.
- **Evaluation purity.** FR-002-CON-3 (deterministic emission), `--check` writing nothing, and the version-bump atomicity of CON-5 cover the build. The textual-versus-structural mode of the manifest digest rewrite is not stated (FND-134).
- **Topological robustness.** The unresolved-token edge is covered twice (FR-004-AC-13 schema-side, FR-006-AC-5 extractor-side with the placeholder target asserted). The legacy-artifact edge is where the spec breaks, though not where the sibling broke: here NFR-001's own Verification paragraph removes the semantic layer from the measured population, so the legacy edge is not measured at all (FND-121).

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-120 | high | FR-004 Behavior states `relations` "SHALL be optional", while the FR-004 table forbids it on `queue` and `extension_point` and omits it from `binary_format` and `rate_limit`, where sealing forbids it; the shipped `Queue.json`, `ExtensionPoint.json`, `BinaryFormat.json`, `RateLimit.json` carry no `relations` property. One requirement, two valid readings, and no AC covers the forbidden case | FR-004 Behavior, FR-004 table, FR-004-AC-4/AC-9/AC-10/AC-11 | wrong-requirement |
| FND-121 | high | NFR-001 Verification states that no 0.2.0 skeleton carries `object:`, so Quire "runs headings-only validation on it and never assembles or checks a typed record". The `semantic.legacy-properties-form` warning is produced by the same Properties extraction (quire-rs FR-070), so NFR-001-AC-3's "exactly 1 warning" cannot be met, and NFR-001-AC-2's "0 error findings" is satisfied by the semantic layer not running rather than by the contract being additive | NFR-001 Verification, NFR-001-AC-2, NFR-001-AC-3, NFR-001 metrics 2 and 3, FR-005 Behavior (`object:` rule) | wrong-requirement |
| FND-122 | high | FR-001 and IT-001 are the unremediated 0.2.0 artifacts; the sibling's four fixes were not carried forward. `spec.md` Out of Scope asserts the service "stores the reference verbatim, which is what FR-001-AC-4 and IT-001-SC-03 assert" — FR-001-AC-4 does not mention `data_schema` and IT-001-SC-03 is the idempotency criterion. FR-001 Behavior pins no service revision (the sibling pins `a77f31e`, the revision that admits the `semantic` block), so TC-001 may validate the 0.3.0 manifest against a schema that rejects it. FR-001 also carries no `traces_to` StR-001 though `tests.md` asserts one | spec.md Out of Scope, FR-001 Behavior, FR-001-AC-1, FR-001-AC-4, IT-001-SC-03, tests.md StR row | wrong-requirement |
| FND-123 | medium | Ticket acceptance criterion 4 ("Existing graph identifiers and relationships have a compatibility mapping") has no requirement. The `allowed_links` verbs (`references`, `contains`, `contained_by`, `represents`, `implements`, `conforms_to`, `extends`, `operates_on`, `publishes`, `reads`, `writes`, `calls`, `realizes`) are never mapped onto `RelationDecl.verb`/`category` or onto the dedicated `SemanticId[]` keys; NFR-001-AC-5 only asserts the sets are unchanged. `references`, declared on six object types, has no record representation anywhere | FR-004, NFR-001-AC-5, manifest `allowed_links`, issue #8 AC 4 | missing-requirement |
| FND-124 | medium | Ticket acceptance criterion 2 ("Definition objects remain distinct from observed routes, calls, queues, and runtime resources") appears only as the last FR-004 Behavior bullet ("no model carries an observation key"). It has no acceptance criterion and no TC row; TC-030 tests pairwise distinctness among the ten types, not the declaration/observation boundary | FR-004 Behavior, tests.md, issue #8 AC 2 | correct-requirement-no-evidence |
| FND-125 | medium | The typed-section/kernel-section authority rule of FR-005 and the agreement assertions of FR-006 cover four pairs (`data_schema` `## Schema`, `queue` `## Message Format`, `interface` `## Contract`, `ui_component` `## Props`). Three required kernel sections are left as unowned second authorities: `external_contract` `## Contract` (plus `## Endpoints`, `## Behavior`) against its `## Operations`; `extension_point` `## Contract` (plus `## Registration`, `## Stability`) against its `## Operations`, `registration` and `stability`; and `action` `## Inputs` against its single operation's param table. No precedence rule, no agreement AC | FR-005 Behavior, FR-006 Behavior, manifest `body_extraction` | missing-requirement |
| FND-126 | medium | NFR-001's whole measurement reads two artifacts no requirement creates: "a checked-in copy of the 0.2.0 `body_extraction`" and "all ten 0.2.0 skeletons". No FR Output names their path or provenance, and no rule keeps them equal to what shipped at 0.2.0, yet NFR-001-AC-1..AC-5 and TC-060..064 all read them. No such copy exists on the branch | NFR-001 Verification, NFR-001-AC-1..AC-5, FR-005 Outputs, tests.md TC-060..064 | missing-requirement |
| FND-127 | medium | Normative Behavior obligations with no acceptance criterion and no TC row: FR-002's "the generator SHALL write files under `spec_objects_architecture/schemas/` only", "SHALL edit `manifest.yaml` only at `data_schema.digest` values", the `.gitattributes` `eol=lf` rule, and "`make lint` SHALL run `make schemas-check`"; and FR-005's `make dev-quire` target plus the fail-not-skip rule — the gate that makes every other Integration row honest, carried only by a paragraph in `tests.md` Test Environment | FR-002 Behavior, FR-005 Behavior, tests.md | correct-requirement-no-evidence |
| FND-128 | medium | FR-002 Behavior binds `make schemas-check` to `make lint` "so a `typespec/` edit that was never regenerated fails before push rather than at review", while FR-002-CON-4 states the same commands run "on a machine whose user-level npm config routes `@agent-ix` to npm.ix, not in the GitHub workflow". Either CI runs `make lint` and the check runs where CON-4 says it cannot, or CI does not and the pre-push claim rests on a local convention with no evidence | FR-002 Behavior, FR-002-CON-4, tests.md TC-013 | wrong-requirement |
| FND-129 | low | StR-001's Stakeholder Need names "integrations" — an object type the manifest records as RETIRED (format-walkthrough decision #8) — and omits five of the ten types this module ships (`interface`, `external_contract`, `extension_point`, `binary_format`, `rate_limit`) | StR-001, manifest | wrong-requirement |
| FND-130 | low | StR-001-VC-2 validates "the templates and schemas this module ships"; the module ships `skeletons/`, not templates. The sibling corrected the same wording to "skeletons and schemas"; the fix was not carried over | StR-001-VC-2, tests.md TC-006 | wrong-requirement |
| FND-131 | low | Validation-method drift on StR-001: VC-1 declares `Inspection` while the closing sentence says all three outcomes are demonstrated, and `tests.md` types TC-005 as `Manual` and TC-007 (VC-3, declared `Demonstration`) as `Unit` | StR-001, tests.md | wrong-requirement |
| FND-132 | low | FR-003-AC-1 says "the nine admitted keys", borrowing quoin's word for a different set: quoin FR-070 admits ten (`sweep_report` too) and requires only three. State that this module fixes nine of the ten and omits `sweep_report` deliberately, so FR-003-CON-1's "admitted list" has one reading | FR-003-AC-1, FR-003-CON-1, quoin FR-070 | wrong-requirement |
| FND-133 | low | FR-003 fixes `mappings: [typed-table, sysml-fence, ocl-clause]`; quoin FR-070 names no mapping vocabulary and admits any string, and the FR-073 digest-reference form is absent from the list. Same as the sibling's FND-131, recorded there with no change | FR-003, quoin FR-070, quoin FR-073 | missing-requirement |
| FND-134 | low | FR-002 scopes the generator's manifest writes to `data_schema.digest` but never states the rewrite is textual. This manifest carries ten YAML anchor uses (`&id001`/`*id001`) and 29 comment lines recording format-walkthrough decisions #8, #11 and #20; a structural rewrite drops both, and FR-003-AC-3/NFR-001-AC-1 compare parsed locators, which anchors expand into, so the loss passes every stated check | FR-002 Behavior, FR-003-AC-3, NFR-001-AC-1 | missing-requirement |
| FND-135 | low | `tests.md` Test Matrix Rule 5 lists the availability states `available`, `not_applicable`, `missing` and omits `unavailable`, which is the state quire-rs FR-070 assigns a legacy-form Properties section and the state NFR-001-AC-3's measurement depends on | tests.md rule 5, NFR-001-AC-3 | wrong-requirement |
| FND-136 | low | Small consistency items: `spec.md` carries `depends_on: []` beside four `depends_on` relationships (the sibling recorded this as a deliberate axis split); FR-001 cites FR-026 and FR-034 in prose without `ix://` links; FR-004 Outputs enumerates 21 support models while FR-002-AC-1 refers to them only as "every support model that requirement declares", one step short of the sibling's by-name enumeration | spec.md, FR-001, FR-002-AC-1, FR-004 Outputs | wrong-requirement |

## Finding Details

### FND-120 (high) — `relations` is both optional and forbidden

Evidence. FR-004 Behavior: "Where a key is declared but the current extractor
does not populate it (`routes`, `requires`, `carries`, …) — and likewise
`relations` — the key SHALL be optional, so a record produced by today's
extractor validates and a future extractor can fill it without a schema
change." The FR-004 table says `relations` is forbidden on `queue`
("`operations` and `relations` forbidden") and on `extension_point`
("`fields` and `relations` forbidden"), and does not list it at all for
`binary_format` or `rate_limit`, which the sealing rule
(`unevaluatedProperties: {not: {}}`) turns into a refusal. The shipped schemas
follow the table: `Queue.json`, `ExtensionPoint.json`, `BinaryFormat.json` and
`RateLimit.json` declare no `relations` property. FR-004-AC-4, AC-9, AC-10 and
AC-11 test the other forbidden keys on those types and never test `relations`,
so neither reading is pinned by evidence.

Proposed fix. Decide which holds and say it once. Either (a) exclude
`relations` from the Behavior sentence and add the refusal to the four ACs
("a record carrying `relations` fails"), stating why a queue, an extension
point, a binary format and a rate limit carry no relationship declarations
while the manifest gives each of them `allowed_links`; or (b) admit
`relations` as an optional key on all ten models and drop it from the two
"forbidden" cells. Option (b) also discharges half of FND-123.

### FND-121 (high) — NFR-001 measures a population the semantic layer never touches

Evidence. FR-005 Behavior: "Each skeleton's frontmatter SHALL carry
`object: <type name>` … because Quire runs the semantic layer (extraction and
record validation) on the `object:` archetype of a document; a skeleton
without it validates its headings only." NFR-001 Verification: "no 0.2.0
skeleton carries a frontmatter `object:` key, so Quire runs headings-only
validation on it and never assembles or checks a typed record. That is what
makes 0.3.0 additive for the artifacts that exist today." The
`semantic.legacy-properties-form` warning is emitted by the typed-Properties
extraction (quire-rs FR-070, quoin FR-074), which is part of that same
semantic layer. If the layer does not run, the warning count is 0, not 1, and
NFR-001-AC-3 and the third metric row ("target 1, threshold 1") cannot pass.
The same reasoning makes NFR-001-AC-2 vacuously true: zero errors because
nothing was validated, not because the contract is additive.

Proposed fix. Split the population. Keep NFR-001-AC-1, AC-4 and AC-5 (locator
and edge-vocabulary diffs) on the checked-in 0.2.0 set, where they are
meaningful without the semantic layer. Restate AC-2 and AC-3 over a fixture
set that does carry `object:` — the legacy authoring forms with the archetype
declared — which is the only population where "additive under
`legacy_forms: warning`" is an observable claim, and which is exactly the case
`agent-ix/quire-rs#391` blocks. Alternatively drop AC-3 and the warning metric
and state plainly that no artifact in the measured population reaches the
semantic layer, so the additivity claim is scoped to headings-only validation.

### FND-122 (high) — the FR-001/IT-001 remediation was not carried forward

Evidence. `spec.md` Out of Scope: "Until it lands the service stores the
reference verbatim, which is what FR-001-AC-4 and IT-001-SC-03 assert."
FR-001-AC-4 reads "Each declared archetype/object_type/artifact_type appears
in the corresponding filament-core table after activation" — no mention of
`data_schema`. IT-001-SC-03 reads "the response is an idempotent no-op" — the
re-activation criterion. The sibling module made all four changes this spec
omits: a `traces_to` StR-001 relationship on FR-001; a Behavior bullet pinning
`module-manifest.schema.json` v1.0.0 "at filament-core-service revision
`a77f31e` or later (CR-003, the revision that admits the `semantic` block and
the reference-form `data_schema`)"; a Behavior bullet stating that while
`agent-ix/filament-core-service#23` is open the registered `data_schema` is
the reference object as posted; and an FR-001-AC-4 that reads against that
value. IT-001 there also gained a readiness step, renumbering its success
criteria. Without the revision pin, FR-001-AC-1 and TC-001 may run against a
vendored schema that predates the `semantic` block, in which case the 0.3.0
manifest fails a criterion the matrix marks green.

Proposed fix. Port the sibling's FR-001 Behavior bullets and AC-4 text
verbatim (substituting this module's package name), add the `traces_to`
StR-001 relationship, decide whether IT-001 gains the readiness step, and then
correct the `spec.md` sentence to name whatever criteria actually carry the
obligation.

### FND-123 (medium) — the edge vocabulary has no record mapping

The ticket's fourth acceptance criterion asks for a compatibility mapping for
"existing graph identifiers and relationships". The spec delivers the identity
half — FR-005-AC-3 and FR-006-AC-4 pin every non-kernel target to
`ix://agent-ix/spec-objects-architecture/type/<Title>` — and asserts
non-regression of the edge half (NFR-001-AC-5: `allowed_links` and `roles`
unchanged). It never states how a manifest edge becomes a declaration-record
key. Some verbs have a dedicated key (`carries`, `requires`, `renders`,
`throttles`, `serializes`, `triggers`, `exposes`); some would have to travel
as `RelationDecl` with a `verb` and an `EdgeCategory` this spec never assigns;
and `references` — declared on `data_schema`, `queue`, `interface`,
`external_contract`, `extension_point` and `binary_format` — has no key on any
model and, on four of those six, no `relations` array either (FND-120). Add a
mapping table to FR-004 Behavior assigning each `allowed_links` verb either a
dedicated key or a `RelationDecl` `verb`/`category` pair, plus an AC that
every verb in the manifest has exactly one landing place.

### FND-124 (medium) — the declaration/observation boundary is unevidenced

FR-004's closing Behavior bullet is the whole of the ticket's second
acceptance criterion, and it is the criterion the safety gate leans on
("Do not enable impact propagation or extraction behavior in this schema
ticket"). Add an acceptance criterion in the shape the rule is written — no
shipped schema declares a property naming a measured call count, a discovered
route, a live resource id, or a per-occurrence timestamp — and a TC row of
type `Static` or `Unit` over the emitted schema properties.

### FND-125 (medium) — three unowned second authorities

FR-005 fixes precedence for four typed/kernel pairs and FR-006 asserts
agreement for three of them. `external_contract` and `extension_point` each
carry a `required: true` `## Contract` section describing the same operations
their schemas require from `## Operations`, plus optional `## Endpoints`,
`## Behavior`, `## Registration` and `## Stability` sections describing the
same policies the record carries as `versioning`, `registration` and
`stability`. `action` carries a `required: true` `## Inputs` section
describing the params of its single operation. Nothing says which wins, and
FR-005-AC-7's "every asserted section body is non-empty" is satisfied by two
sections that disagree. Either extend the FR-005 authority rule and add
FR-006 agreement criteria for the three, or state that these kernel sections
are prose commentary with no declaration content and that no agreement is
claimed.

### FND-126 (medium) — the NFR baseline is an artifact nothing owns

Every NFR-001 criterion is a diff against a 0.2.0 baseline: the locator
definitions, the ten skeletons, the `allowed_links`/`roles` sets, and the
locator yields under both manifests. FR-005 rewrites the live skeletons in
place, so the baseline has to be a separate checked-in copy — named only in
NFR-001's Verification prose, present in no FR's Outputs, at no stated path,
with no rule tying it to the 0.2.0 release bytes. Nothing stops it from being
regenerated from the 0.3.0 tree, at which point TC-060..064 pass by
construction. Give it an owner: add it to FR-005 Outputs (or a new FR) with a
path, a provenance rule (the bytes at the `0.2.0` tag), and an AC that the
copy's digest matches that tag.

### FND-127 (medium) — Behavior obligations with no criterion

Six normative bullets carry no AC and no matrix row. Four are FR-002's
(write-scope to `schemas/`, edit-scope to `data_schema.digest`, `.gitattributes`
`eol=lf`, `make lint` runs `make schemas-check`); two are FR-005's (the
`make dev-quire` target and the fail-not-skip rule). The last is the most
consequential: `tests.md` Test Environment states that the suite fails rather
than skips when `extract_semantic` is absent, and the honesty of every green
`Integration` row in the matrix depends on it, but no criterion asserts it.
Add an AC to FR-005 ("with the Quire wheel absent, the semantic suite exits
non-zero and the message names `extract_semantic`, `make dev-quire`, and
`agent-ix/quire-rs#392`") and a TC row, and add ACs or fold the FR-002 bullets
into FR-002-AC-4/AC-9.

### FND-128 (medium) — `make lint` versus CON-4

FR-002-CON-4's parenthetical is doing two jobs: it records the npm.ix
resolution discipline and it excludes the schema check from CI. The Behavior
bullet binding `schemas-check` to `make lint` assumes the opposite. Decide:
either state that `make lint` runs the check locally only and name the
mechanism that catches an unregenerated `typespec/` edit in CI (a review
gate, or a CI job with npm.ix reachable), or drop the CI exclusion from CON-4
and state how the workflow reaches npm.ix. As written the two cannot both be
satisfied, and TC-013 does not distinguish them.

### Lows

- FND-129: rewrite the StR-001 need over the ten types this module ships and drop `integrations`.
- FND-130: StR-001-VC-2 "templates" -> "skeletons".
- FND-131: make StR-001's three Validation cells agree with the closing sentence and with the `tests.md` types.
- FND-132: say "nine of quoin FR-070's ten admitted keys; `sweep_report` is omitted because no sweep report is produced here" and scope FR-003-CON-1 to that list.
- FND-133: cite the source of the mapping names or define them in FR-003; no change expected, matching the sibling's disposition.
- FND-134: state that the digest rewrite is textual so anchors and comments survive, and add an AC that the 0.3.0 manifest's anchors and comment lines are byte-identical to 0.2.0's outside the digest values.
- FND-135: add `unavailable` to Test Matrix Rule 5.
- FND-136: drop or populate `spec.md` `depends_on`; link FR-026/FR-034; have FR-002-AC-1 name the 31 emitted files or cite FR-004 Outputs by count.

## Grounding Notes

Checks run against the upstream sources rather than restated from the spec, so
a later reviewer need not repeat them:

- `targets: [json-schema, markdown]` are both admitted by
  `filament-core-data/schema/semantic/v1/common.schema.json` (`target` enum
  and `representationFormat` enum). No finding.
- `OperationDecl.params` is required by semantic-core, and FR-005 calls the
  param table optional; quire-rs FR-071-AC-4 settles it upstream ("an
  operation without a table yields `params: []`"). No finding.
- `semantic.record-invalid` appears in no quoin or quire-rs acceptance
  criterion, which is exactly what FR-005 Dependencies says. No finding.
- The emitted set matches FR-004 Outputs exactly: ten object-type models, three
  marker models, nine value models and nine enums, 31 files plus
  `toolchain.json`.
- The branch ships ten skeletons; FR-005 Inputs names three additional
  `*.sysml.md` alternates and FR-005-AC-1 counts thirteen files. That is
  implementation state, not a spec defect, and belongs to the gap analysis.
