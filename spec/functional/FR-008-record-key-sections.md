---
id: FR-008
title: "Author the optional record keys as Markdown sections"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-003"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-005"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-006"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-121"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-122"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-104"
    type: "depends_on"
---
# FR-008: Author the optional record keys as Markdown sections

## Description

The module SHALL name the `relationships` and `record-sections` mapping tokens
in its manifest and SHALL ship every skeleton in the authored form quoin
FR-122 publishes for the record keys that skeleton's object type declares, so
that each optional key of [FR-004](./FR-004-role-schemas.md) is filled from a
document by the extractor instead of only from a hand-built record
(PLAT-196 `agent-ix/quoin#344`, PLAT-201 `agent-ix/quoin#342`).

## Inputs

- quoin FR-121 (the record-sections mapping) and FR-122 (the architecture
  keys), implemented by `agent-ix/quire-rs` FR-081.
- The optional keys and models of [FR-004](./FR-004-role-schemas.md).
- The skeletons of [FR-005](./FR-005-executable-skeletons.md).

## Outputs

- `relationships` and `record-sections` in `semantic.mappings`.
- Optional skeleton sections and manifest `section_body` locators for each
  authored form below.
- Tests that extract each form and validate the extracted key against the
  module's own emitted schema.

## Behavior

- The manifest `semantic.mappings` SHALL name `relationships` and `record-sections`; without `relationships` the engine derives no typed relation key, and without `record-sections` it reads no record-key section.
- Each skeleton SHALL author the keys of its object type under the heading and in the form shown:

| Object type | Key | Heading | Form |
|---|---|---|---|
| `api_endpoint` | `routes` | `## Routes` | table `Method \| Path \| Operation` |
| `queue` | `delivery` | `## Delivery` | one-row table `Semantics \| Ordering \| Retention` |
| `external_contract` | `provider` | `## Provider` | one inline id |
| `external_contract` | `versioning` | `## Versioning` | one-row table `Scheme \| Breaking Change Signal` |
| `extension_point` | `exposes` | `## Exposes` | one inline id |
| `extension_point` | `registration` | `## Registration` | one-row table `Mechanism \| Conflict \| Discovery` |
| `extension_point` | `stability` | `## Stability` | one-row table `Compatibility \| Deprecation Window` |
| `rate_limit` | `thresholds` | `## Thresholds` | table `Scope \| Metric \| Limit \| Window \| Status \| Retry After \| Behavior` |
| `interface` | `associated_types` | `## Associated Types` | table `Type \| Multiplicity` |
| `binary_format` | `records`, `endianness` | `## Layout` | the existing YAML fence |

- A `routes` row's `Operation` cell SHALL name an operation the same artifact declares under `## Operations`; the engine refuses a route that names none (`route-operation-unknown`), which states the reader rule of `RouteDecl`.
- Every `## Thresholds` row SHALL carry a `Status` cell, because `ExceedResponse.status` is required.
- The `interface` `## Contract` fence SHALL NOT be a source of `associated_types`; the `## Associated Types` table is the only source (this reverses the `associated_types[]` clause that [FR-006](./FR-006-architecture-lowerings.md) used to state).
- A `## Layout` string `size` SHALL name one field of exactly one record in the fence, in the same record or another, so the skeleton's `posting_tuple.payload` is sized by `metadata_block.payload_len`.
- The `## Layout` keys `format` and `magic` SHALL stay documentation.
- A `## Endianness` or `## Records` section SHALL be prose.
- The skeletons SHALL author the typed relation keys (`requires`, `carries`, `renders`, `triggers`, `serializes`, `throttles`) and `relations` as `## Relationships` rows only; a `## Requires` or similar list is prose.
- `## Endpoint` SHALL stay the required prose anchor of an `api_endpoint`; the concrete routes move to the optional `## Routes` table, which reverses the format-walkthrough decision #20 that listed routes inside `## Endpoint`.
- Every new section SHALL be optional, so an artifact authored without it stays valid.
- This is a breaking change for artifacts that authored `## Thresholds`, `## Registration` or `## Stability` as bullet lists: the engine refuses each as `semantic.feature-not-extractable` once `record-sections` is named, and the skeletons and the negative fixtures of this module are converted.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-008-AC-1 | `semantic.mappings` names `relationships` and `record-sections`. | Test |
| FR-008-AC-2 | Extracting each of the `api_endpoint`, `queue`, `external_contract`, `extension_point`, `interface`, `binary_format` and `rate_limit` skeletons under the manifest's mappings and the module's emitted schemas yields zero errors and exactly the record keys of the table above, each `available` and each value valid against its model. | Test |
| FR-008-AC-3 | A `## Routes` row naming an operation the artifact does not declare yields one `semantic.invalid-model-cell` with `reason` `route-operation-unknown` and no `routes` key. | Test |
| FR-008-AC-4 | An `interface` with a `## Associated Types` table extracts `associated_types` from the table in row order; an `interface` whose `## Contract` fence lists `associated_types` and that has no table extracts no record key. | Test |
| FR-008-AC-5 | The `binary_format` skeleton extracts `endianness` `little` and two `RecordLayout`s the second with `tag` `"0x21"`, the `payload` size `payload_len` as an identifier resolving across records, and no `magic`; a `size` naming no field yields `size-unknown-field`, one naming a field in two records yields `size-ambiguous`, and a `## Endianness` section is prose. | Test |
| FR-008-AC-6 | A `## Thresholds` row with an empty `Status` yields `semantic.invalid-model-cell` `status-required`; a row with `429`, `true` and no `Behavior` extracts `on_exceeded` of `status` 429 and `retry_after` true; a bullet-list `## Registration` yields `semantic.feature-not-extractable`. | Test |
| FR-008-AC-7 | An `api_endpoint` whose `## Relationships` table holds a `requires` row extracts `requires` as `SemanticId[]`, and a `## Requires` bullet list beside it yields no diagnostic. | Test |

## Dependencies

- **Upstream**: [FR-003](./FR-003-semantic-manifest-contract.md), [FR-004](./FR-004-role-schemas.md), [FR-005](./FR-005-executable-skeletons.md), [FR-006](./FR-006-architecture-lowerings.md); quoin FR-104, FR-121, FR-122
- **Upstream (extraction)**: `agent-ix/quire-rs` FR-081 (record-sections extraction), `agent-ix/quire-rs` FR-076 (typed relation keys); the `quire` dev dependency must carry them
- **Blocker, extractor release**: the locked `quire` (`^0.52.0`, lock 0.52.0) has no record-sections extractor. quire-rs FR-081 ships in quire 0.55.0, so TC-121..TC-126 fail until the `quire` dev dependency is bumped to it and the lock is regenerated by tooling.
