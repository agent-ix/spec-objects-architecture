---
id: SR-001
title: "Base review of the issue #8 semantic module contract specification"
type: SpecReview
analysis: base
scope: "spec/spec.md, spec/stakeholder/StR-001-module-activation.md, spec/usecase/US-001-declare-architecture-objects-against-semantic-core.md, spec/functional/FR-001-module-manifest-activates.md, spec/functional/FR-002-emitted-json-schemas.md, spec/functional/FR-003-semantic-manifest-contract.md, spec/functional/FR-004-role-schemas.md, spec/functional/FR-005-executable-skeletons.md, spec/functional/FR-006-architecture-lowerings.md, spec/non-functional/NFR-001-additive-compatibility.md, spec/integration/IT-001-manifest-activation-roundtrip.md, spec/integration/IT-002-quoin-module-install.md, spec/tests.md"
review_set: base
---
# SR-001: Base review of the issue #8 semantic module contract specification

## Summary

Checklist review (id formats, story and requirement quality, cross-references,
the six coverage rules) of the thirteen artifacts that deliver
`agent-ix/spec-objects-architecture#8`, grounded against the real upstream:
the sibling module `agent-ix/spec-objects-business#4` and its eight reviews,
the `@agent-ix/semantic-core` 0.1.0 grammar (`main.tsp`), this module's
current `spec_objects_architecture/manifest.yaml` (0.2.0) with its ten object
types and its ten checked-in skeletons, and the quire 0.46.0 wheel in
`quire-rs/dist`.

Ids are well-formed and sequential per class (StR-001, US-001, FR-001..FR-006,
NFR-001, IT-001..IT-002, TM-001, TC-001..TC-086 allocated in per-FR blocks);
every FR except FR-001 carries an `implements` relationship to US-001, and
US-001 traces to StR-001. Coverage bookkeeping is complete: every AC, every
named constraint, every NFR metric and every IT success criterion has at least
one TC row, which is a real improvement over the sibling's first pass, and the
matrix is honest about what stays `🚧` and why.

Two high findings block the gate. NFR-001's second-largest evidence block
measures a population that does not exist in this repository — unlike the
business module, no 0.2.0 architecture skeleton carries a `## Properties`
section in any form, so the `semantic.legacy-properties-form` metric can never
observe its target of 1, and TC-062 is a vacuous green row. And FR-004
contradicts itself on `relations`: Behavior states the key SHALL be optional
on every type, while the Queue and ExtensionPoint rows forbid it. Eight
mediums (an unsatisfiable pairwise-distinctness AC, an unsatisfiable title
uniqueness AC, three FR-001/IT-001 staleness items, a lint/CI conflict, an
unowned 0.2.0 baseline, and the "templates" wording the sibling already
corrected) and five lows follow.

## Verdict

**Not ready for `spec-to-plan`.** FND-001 and FND-002 change what the
implementation must build (an evidence population and a schema rule
respectively) and must be dispositioned first. FND-003..FND-010 are one- to
three-line spec edits; the lows are recorded.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | NFR-001's `semantic.legacy-properties-form` metric (target 1, threshold 1, per skeleton) has an empty population: none of the ten checked-in 0.2.0 architecture skeletons carries a `## Properties` section in any form (`grep '## '` over `spec_objects_architecture/skeletons/*.md` yields `## Endpoint`, `## 2. API Contract`, `## Schema`, `## Message Format`, `## Inputs`, `## Props`, `## Contract`, `## Endpoints`, `## Behavior`, `## Registration`, `## Stability`, `## Layout`, `## Thresholds` only). The metric is carried over from `spec-objects-business`, whose 0.2.0 skeletons do carry bullet-list `## Properties`. NFR-001-AC-3 is conditionally worded so it passes vacuously, but the Measurement row is not, and TC-062 is marked `✅` for evidence it cannot produce. | NFR-001 Measurement row 3, NFR-001-AC-3, spec/tests.md TC-062 | wrong-requirement |
| FND-002 | high | FR-004 Behavior states that `relations` "SHALL be optional" on every type ("and likewise `relations`"), so that a future extractor can populate it without a schema change; the Queue row forbids `operations` **and `relations`**, and the ExtensionPoint row forbids `fields` **and `relations`**. Both readings cannot hold, and the manifest declares `allowed_links` for both types (`queue: carries, references`; `extension_point: extends, references`), so the forbidden form seals two schemas against the edge vocabulary the module itself ships. | FR-004 Behavior table rows `queue`, `extension_point`; FR-004 Behavior bullet on unpopulated keys; `manifest.yaml` `allowed_links` | wrong-requirement |
| FND-003 | medium | FR-004-AC-1 requires each of the ten schemas to differ from every other "in at least one required, forbidden, or item rule listed in the table". `BinaryFormat` and `RateLimit` are identical on all three axes (required `clauses`; `fields` and `operations` forbidden; `clauses` has ≥ 1 item) and differ only in optional keys (`records`/`endianness`/`serializes` versus `thresholds`/`throttles`), which the criterion does not admit as a difference. As written the AC fails on that pair. | FR-004-AC-1, FR-004 Behavior table, spec/tests.md TC-030 | wrong-requirement |
| FND-004 | medium | FR-005 requires every skeleton `title` to be "distinct across all skeletons" and FR-005-AC-8 tests uniqueness across the skeletons, while FR-005 Behavior requires each alternate skeleton (`data_schema.sysml.md`, `queue.sysml.md`, `ui_component.sysml.md`) to be authored "under that skeleton's frontmatter `id` and `title`". Thirteen files cannot carry thirteen distinct titles when three are mandated duplicates, so AC-8 is unsatisfiable as worded. Inherited verbatim from `spec-objects-business` FR-005; fixing it here should be mirrored there. | FR-005 Behavior (alternate skeletons, title rule), FR-005-AC-8 | wrong-requirement |
| FND-005 | medium | FR-001 and IT-001 are unchanged from the 0.2.0 era, yet three other documents cite them as carrying #8 obligations: FR-003 Inputs says the manifest schema revision `a77f31e` (CR-003) is "the same revision FR-001 names" — FR-001 names no revision, only "FR-035 v1.0.0"; and `spec.md` Out of Scope says the service "stores the reference verbatim, which is what FR-001-AC-4 and IT-001-SC-03 assert" — FR-001-AC-4 asserts that declared contributions appear in the registry tables and IT-001-SC-03 asserts idempotent re-activation; neither mentions `data_schema` or the reference form. The reference-form activation obligation is therefore stated nowhere it can be tested. | FR-003 Inputs, spec.md Out of Scope, FR-001-AC-4, IT-001-SC-03 | missing-requirement |
| FND-006 | medium | FR-001's Verification cells read `Schema Test` and `Integration Test`, which are neither catalog ids nor verification classes; `quire coverage` reports `uncatalogued-verification-method` for exactly this form and the declared class value is `Test`. The sibling module found and fixed the identical defect (`spec-objects-business` SR-001 FND-003); it was not carried across. | FR-001-AC-1..AC-4 | wrong-requirement |
| FND-007 | medium | FR-001 carries no `traces_to`/`implements` relationship to StR-001 or US-001 in its frontmatter (only `implements` filament-core-service FR-035), while `tests.md` asserts the trace `StR-001 → US-001, FR-001..FR-006`. The matrix claims a lineage the artifacts do not carry, so a coverage tool reading frontmatter and a reader reading the matrix disagree. | FR-001 frontmatter, spec/tests.md Stakeholder Requirement Coverage | missing-requirement |
| FND-008 | medium | FR-002 Behavior requires `make lint` to run `make schemas-check` "so a `typespec/` edit that was never regenerated fails before push", while FR-002-CON-4 requires that `make schemas`/`make schemas-check` run only "on a machine whose user-level npm config routes `@agent-ix` to npm.ix, not in the GitHub workflow". `.github/workflows/ci.yml` delegates its `ci` job to the shared `agent-ix/python-service-actions/.github/workflows/lib-ci.yml`, which is this repo's lint/test gate; if that gate runs `make lint` the check runs in the workflow the constraint excludes, and if it does not, the "fails before push" rationale holds only for local runs. Neither the exclusion mechanism nor the CI target is specified. | FR-002 Behavior (`make lint`), FR-002-CON-4, `.github/workflows/ci.yml` | missing-requirement |
| FND-009 | medium | Five criteria depend on a checked-in 0.2.0 baseline — FR-003-AC-3 ("compared against the checked-in 0.2.0 baseline"), NFR-001-AC-1..AC-5 and NFR-001 Verification ("a checked-in copy of the 0.2.0 `body_extraction` and of all ten 0.2.0 skeletons") — but no requirement obliges the module to create that copy, names its path, or fixes what it contains. FR-005-CON-1 scopes skeleton edits to this repo and says nothing about a baseline. The single most-cited evidence artifact of the change is unowned. | FR-003-AC-3, NFR-001 Verification, NFR-001-AC-1..AC-5, FR-005-CON-1 | missing-requirement |
| FND-010 | medium | StR-001 Rationale and StR-001-VC-2 speak of "the templates and schemas this module ships"; the module ships skeletons and (at 0.3.0) schemas, and no requirement produces a template. VC-2 is a `Demonstration` criterion over an artifact class that does not exist, and TC-006 inherits the wording. The sibling corrected this to "skeletons and schemas" (`spec-objects-business` SR-003 FND-130). | StR-001 Rationale, StR-001-VC-2, spec/tests.md TC-006 | wrong-requirement |
| FND-011 | low | FR-002-AC-1 fixes the emitted set as "the ten object-type models of FR-004 plus every support model that requirement declares", deferring the count to prose elsewhere; FR-004 Outputs names 21 support models (3 markers, 9 value models, 9 enums), so the emitted set is 31 files plus `toolchain.json`. The sibling replaced the same indirection with an explicit file list (SR-003 FND-133). | FR-002-AC-1, FR-004 Outputs | wrong-requirement |
| FND-012 | low | FR-004's decorator recipe covers the `@contains` rules but not the cardinality bounds it also asserts: "exactly 1 item" for `Action` is given only `@maxItems(1)` (no `@minItems(1)`), and the eight "has ≥ 1 item" rules name no `@minItems`. An implementer following the recipe literally emits `Action` schemas that accept an empty `operations` array, contradicting FR-004-CON-2 and FR-004-AC-12. | FR-004 Behavior (decorator recipe), FR-004-AC-5, FR-004-CON-2 | missing-requirement |
| FND-013 | low | FR-005 Behavior enumerates the four skeletons that require `## Invariants` and the five that carry none; `api_endpoint` appears in neither list, and FR-005-AC-4 silently decides it (`clauses` `not_applicable`). Add it to the clause-free enumeration. | FR-005 Behavior, FR-005-AC-4 | missing-requirement |
| FND-014 | low | Test Matrix rule 5 claims availability states "`available`, `not_applicable`, `missing`" are tested per declaration kind, but FR-005-AC-4 enumerates only `available` and `not_applicable`, and no skeleton or negative fixture produces `missing`. Either drop `missing` from the rule or add a fixture that yields it. | spec/tests.md rule 5, FR-005-AC-4, TC-053 | correct-requirement-no-evidence |
| FND-015 | low | `package.json` and `pyproject.toml` both describe the module as shipping `integration`, `dto`, `middleware` — types the manifest retired (see the `integration` RETIRED comment) — and omit `interface`, `external_contract`, `extension_point`, `binary_format`, `rate_limit`. FR-002 already touches `package.json` (staging, dependencies) but no criterion covers the package descriptions. | FR-002 Inputs/Outputs, `package.json`, `pyproject.toml` | missing-requirement |

## Checklist Notes (no change requested)

TC ids are allocated in per-FR blocks with deliberate gaps (TC-008..009,
TC-029, TC-045..049, TC-066..069, TC-075..079); recorded so a later audit does
not read them as lost rows. US-001 carries illustrative examples
(US-001-EX-1..3) rather than Given/When/Then acceptance criteria, which is the
`spec-artifacts-iso` US skeleton's form and is satisfied by the FR criteria
those examples lead to.

## Coverage Rules

Verified against the matrix and the requirement documents (rule 1 by
enumeration, rules 2–6 by locating the rows that discharge them):

1. **Coverage.** Every AC, named constraint, NFR metric and IT success
   criterion has ≥ 1 TC: FR-001 AC-1..4 → TC-001..004; FR-002 AC-1..9 →
   TC-010..015, TC-071..073 and CON-1..5 → TC-016..019, TC-072, TC-074;
   FR-003 AC-1..7 → TC-020..028 and CON-1..2 → TC-020, TC-023; FR-004
   AC-1..14 → TC-030..043 and CON-1..3 → TC-041, TC-043, TC-044; FR-005
   AC-1..9 → TC-050..056, TC-059, TC-065 and CON-1..2 → TC-057, TC-058;
   FR-006 AC-1..6 → TC-080..085 and CON-1..2 → TC-085, TC-086; NFR-001
   AC-1..5 → TC-060..064; StR-001 VC-1..3 → TC-005..007; IT-001 SC-01..03 →
   TC-002..004; IT-002 SC-01..06 → TC-070. No orphan TC. Subject to FND-001
   (TC-062 has no population) and FND-014.
2. **Option permutation.** Both Properties forms across the three
   alternate-form types (TC-051) and all ten object types (TC-030..040,
   TC-050).
3. **Constraint boundary.** Zero versus one identity field (TC-033, TC-035),
   one versus two operations (TC-034), empty versus one-item arrays (TC-032,
   TC-036, TC-039), a `Threshold.scope` inside and outside `LimitScope`
   (TC-040).
4. **Error path.** Digest mismatch and unknown `semantic` key (TC-026), both
   Properties forms in one artifact (TC-057), dangling clause ref and
   non-Identifier type token (TC-054), missing return and missing post-clause
   (TC-031, TC-037), stale committed schema (TC-073).
5. **State transition.** Availability per declaration kind (TC-053) — see
   FND-014 for the `missing` state.
6. **Edge case.** Empty record (TC-041), legacy 0.2.0 artifacts (TC-061..063),
   unresolved token (TC-042, TC-084).

## Grounding Notes

Facts checked against the real upstream rather than the spec's own claims:

- `@agent-ix/semantic-core` 0.1.0 `main.tsp` carries every model FR-002 Inputs
  and FR-004 Inputs name — `FieldDecl` (with `identity?: boolean`, so "absent,
  not `false`" is correct), `RelationDecl`, `OperationDecl` (`returns?`,
  `pre?`, `post?`), `ClauseRef`, `TypeRef`, `EnumValue`, `Multiplicity`,
  `ConstraintDecl` (a union), `Identifier`, `SemanticId`, `KernelScalar`. No
  named model is missing.
- The manifest at 0.2.0 declares exactly the ten object types FR-003 lists;
  `spec.md`, FR-003 and FR-004 agree on ten throughout (the nine-versus-ten
  contradiction that the sibling carried is absent here).
- The required 0.2.0 headings FR-005 must preserve match the manifest's
  `required: true` locators exactly (`Endpoint`, `Schema`, `Message Format`,
  `Inputs`, `Props`, `Contract` ×3, `Layout`, `Thresholds`).
- No 0.2.0 skeleton carries a frontmatter `object:` key, so NFR-001's
  reasoning about headings-only validation holds — and it is the same fact
  that empties FND-001's population.
- Nine of the ten skeleton titles are not `Identifier`s ("Verify artifact
  checksum", "Artifact record", "QuantCodec scoring contract", …); only
  `ArtifactTable` is. FR-005's title rule therefore mandates nine renames,
  which is stated work, not a defect — but see FND-004.
- A `quire-0.46.0-cp39-abi3-manylinux_2_34_x86_64.whl` exists in
  `quire-rs/dist`, so FR-005's pin names a real artifact and the
  `make dev-quire` provisioning mirrors the sibling's (`pypi.ix` dev index).
  The fail-not-skip rule and the two named expected failures
  (`quire-rs#391`, `quire-rs#221`/`#394`) are correctly carried.

## Dispositions

| Finding | Disposition |
|---|---|
| FND-001..FND-015 | Open — returned to the author. FND-001 and FND-002 require a decision (which population NFR-001 measures for legacy forms, and whether `relations` is optional or forbidden on `queue`/`extension_point`) before the plan is written; the rest are spec edits. |
