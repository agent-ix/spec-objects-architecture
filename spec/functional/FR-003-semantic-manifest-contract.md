---
id: FR-003
title: "Declare the semantic-module contract in the manifest"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-001"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-070"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-073"
    type: "depends_on"
---
# FR-003: Declare the semantic-module contract in the manifest

## Description

`spec_objects_architecture/manifest.yaml` SHALL carry the quoin FR-070
`semantic` block and reference every exported object type's emitted schema by
path and digest (quoin FR-073), at manifest `version` 0.3.0, so that Quoin
verifies the shipped schemas at install and Quire validates every declaration
record against them, while every existing extraction locator keeps its
meaning.

## Inputs

- The emitted schemas and digests of [FR-002](./FR-002-emitted-json-schemas.md).
- The module-manifest schema with the `semantic` block, at
  `agent-ix/filament-core-service` revision `a77f31e` (CR-003) — the revision
  [FR-001](./FR-001-module-manifest-activates.md) Inputs pins, and the
  revision Quoin and Quire each vendor byte-identically
  (`sha256:69cf9738600e7d8daa45ed5cd7231b17ca8dc58d068bd36af9b0d2c9b69dcbbc`).
  All three consumers therefore judge this manifest against one schema; a
  consumer vendoring an older copy is a skew defect on that consumer, not a
  change here.

## Outputs

- `manifest.yaml` with `version: 0.3.0`, a `semantic` block, and reference-form
  `data_schema` on every exported object type.

## Behavior

- The manifest `semantic` block SHALL carry exactly these keys and values: `contract_version: 1.0.0`, `semantic_core: 0.1.0`, `package: agent-ix/spec-objects-architecture`, `exports` listing every object type that ships a schema, `imports: {}`, `targets: [json-schema, markdown]`, `mappings: [typed-table, sysml-fence, ocl-clause]`, `compatibility_posture: additive`, `legacy_forms: warning`.
- `semantic.exports` SHALL name all ten object types: `api_endpoint`, `data_schema`, `queue`, `action`, `ui_component`, `interface`, `external_contract`, `extension_point`, `binary_format`, `rate_limit`.
- Every exported object type's `data_schema` SHALL be `{ schema: schemas/<Model>.json, digest: sha256:<hex> }` where `<hex>` is the SHA-256 of the shipped file bytes.
- No exported object type SHALL carry an inline `data_schema`.
- The manifest `version` SHALL be `0.3.0`, because the emitted `$id` embeds it and the previous version was `0.2.0`.
- Every `body_extraction` locator present at version 0.2.0 SHALL remain present with the same `from`, heading, `language`, `required`, `multiple`, and `assert` facets.
- The `schema_json` code-block locator on `data_schema`, the `message_schema` locator on `queue`, the `contract_yaml` locator on `interface`, and the `layout_yaml` locator on `binary_format` SHALL stay in place, so the untyped fence text continues to be yielded beside the semantic record ([FR-006](./FR-006-architecture-lowerings.md) states what each lowers to).
- Where an object type gains a locator after 0.2.0, that locator SHALL be `required: false`, so existing artifacts stay valid (the additions themselves are specified by [FR-005](./FR-005-executable-skeletons.md)).
- The module SHALL carry the manifest `lexicon` block forward unchanged, because it serves the FR-043 EARS vague-response check and is unrelated to the semantic contract.
- The manifest SHALL load through Quire's registry loader with no `ArchetypeLoadFailure` for any object type and with the recorded schema digest equal to the manifest digest.
- Measured against quire 0.46.0 on this module: a refused schema drops that object type alone (the other nine still load), while a manifest key the loader cannot parse (an unknown `semantic` key) drops every object type, so a consumer sees the module as absent. `agent-ix/quire-rs#394` reports a module-wide emptying for the digest case on another module; this specification records what this module measured rather than what the report says, and the test says so too.
- Both refusals are silent: no diagnostic names the offending key, path, or digest. `agent-ix/quire-rs#221` and `agent-ix/quire-rs#394` record that; the naming half of FR-003-AC-6 is blocked on them and is verified as an explicit expected failure rather than dropped.
- Handed the ten reference-form `data_schema` values verbatim, the Filament snapshot path SHALL refuse each one with `semantic.data-schema-unresolved-reference` at error severity and emit no object-type node, because quire-rs FR-069 leaves resolution to the registry owner (`agent-ix/filament-core-service#23`). The same schemas resolved into the snapshot are accepted. Both halves are measured by FR-003-AC-8 so the day #23 lands the row turns red.
- The manifest SHALL install through `quoin module install path:<module dir>` with no `semantic.*` error diagnostic.
- When the install has completed, `quoin module` SHALL list `spec-objects-architecture`.
- If Quoin or Quire rejects the manifest, then this module SHALL correct its own manifest or schemas rather than relax the contract keys, the digests, or the `$id` rules to make a consumer accept them.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-003-CON-1 | The `semantic` block SHALL contain no key outside the admitted list. Quire's loader refusal of an unknown key is verified here (FR-003-AC-6); Quoin's refusal is the neighbour's own obligation (quoin FR-070) and is assumed, evidenced only by the clean install of [IT-002](../integration/IT-002-quoin-module-install.md). | Compatibility | Test |
| FR-003-CON-2 | The manifest SHALL mark every locator added after 0.2.0 `required: false`. | Compatibility | Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-003-AC-1 | The loaded `semantic` block equals the nine admitted keys with the values above, and `exports` equals the ten object-type names. | Test |
| FR-003-AC-2 | For every exported type, `data_schema` is the reference form, the referenced file exists, and its SHA-256 equals the recorded digest. | Test |
| FR-003-AC-3 | Every 0.2.0 locator, compared against the checked-in 0.2.0 baseline, is present unchanged; every added locator is `required: false`. | Test |
| FR-003-AC-4 | `quire.Registry.load_from([module dir])` lists all ten archetypes and `validate_document` on each skeleton reports no `semantic.*` load failure. | Test |
| FR-003-AC-5 | `quoin module install path:<module dir>` exits zero and `quoin module` lists `spec-objects-architecture`; the previously installed entry is restored afterwards. | Demonstration |
| FR-003-AC-6 | A manifest copy whose `semantic` block gains a key `foo` is refused by Quire's loader naming `foo`; a copy whose digest is altered is refused naming the path. | Test |
| FR-003-AC-7 | The 0.2.0 `lexicon` block is byte-identical at 0.3.0, including the eight definitions this repo's issue #7 records as truncated. | Test |
| FR-003-AC-8 | Handed this manifest's ten reference-form `data_schema` values verbatim, `extract_filament_core` answers one `semantic.data-schema-unresolved-reference` at error severity per exported object type; handed the same schemas resolved into the snapshot, it answers none. | Test |

## Dependencies

- **Upstream**: [FR-001](./FR-001-module-manifest-activates.md), [FR-002](./FR-002-emitted-json-schemas.md); quoin FR-070/FR-073 (`ix://agent-ix/quoin/FR-070`, `ix://agent-ix/quoin/FR-073`); quire-rs FR-069 (`ix://agent-ix/quire-rs/FR-069`)
- **Downstream**: [FR-005](./FR-005-executable-skeletons.md), [FR-006](./FR-006-architecture-lowerings.md), [IT-002](../integration/IT-002-quoin-module-install.md)
