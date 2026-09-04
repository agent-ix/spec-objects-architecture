---
id: FR-004
title: "Give every architecture object type a role-distinct declaration schema"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/filament-core-data/FR-031"
    type: "depends_on"
---
# FR-004: Give every architecture object type a role-distinct declaration schema

## Description

The TypeSpec source SHALL declare one model per architecture object type whose
emitted schema validates that type's declaration record
`{ fields?, relations?, clauses?, operations?, … }` with type-specific
required keys, forbidden keys, and item rules, so that no type is a
placeholder and each architecture role refuses the records that violate its
own rules; full pairwise disjointness is not claimed, because several
operation-shaped types are separated by keys (`routes`, `registration`,
`versioning`) the extractor does not yet populate.

## Inputs

- semantic-core 0.1.0 grammar models: `FieldDecl`, `RelationDecl`,
  `OperationDecl`, `ClauseRef`, `TypeRef`, `EnumValue`, `Identifier`,
  `SemanticId`, `KernelScalar`.
- The declaration record Quire assembles per artifact: `fields` from
  `## Properties`, `clauses` from `## Invariants`, `operations` from
  `## Operations` (quire-rs FR-070/FR-071), with any key absent when its
  section is absent.

## Outputs

- Ten object-type models, each emitted as `schemas/<Model>.json`, sealed
  (`unevaluatedProperties: {not: {}}`).
- Support models emitted as sibling files: the open marker models
  `IdentityField`, `ReturningOperation` and `GuaranteedOperation`; the
  architecture value models `RouteDecl`, `DeliveryPolicy`, `VersioningPolicy`,
  `RegistrationPolicy`, `StabilityPolicy`, `RecordLayout`, `LayoutField`,
  `Threshold`, `ExceedResponse`; and the closed enums `HttpMethod`,
  `DeliverySemantics`, `OrderingScope`, `VersioningScheme`, `ConflictPolicy`,
  `CompatibilityWindow`, `LayoutType`, `Endianness`, `LimitScope`.

## Behavior

Each model SHALL enforce its row of the following table. "Identity field"
means a `FieldDecl` with `identity: true`; "returning operation" an
`OperationDecl` carrying `returns`; "guaranteed operation" an `OperationDecl`
whose `post` holds at least one `ClauseRef`. All three readings are
semantic-core 0.1.0 reader conventions (the identity flag is set only by a
bare `identity` keyword in a Constraints cell and is absent, not `false`,
otherwise), so a semantic-core release that renders `identity: false` or
changes the operation shape is a breaking change to these schemas and SHALL be
handled by a manifest version bump, not by widening a rule.

| Object type | Model | Required keys | Optional keys | Item rules |
|---|---|---|---|---|
| api_endpoint | `ApiEndpoint` | `operations` | `routes: RouteDecl[]`, `clauses`, `relations`, `requires: SemanticId[]` | `operations` has ≥ 1 item and ≥ 1 returning operation (an endpoint answers); `fields` forbidden |
| data_schema | `DataSchema` | `fields` | `clauses`, `relations` | `fields` has ≥ 1 item; `operations` forbidden — a record declares data, not behaviour |
| queue | `Queue` | `fields` | `delivery: DeliveryPolicy`, `carries: SemanticId[]`, `clauses` | `fields` has ≥ 1 item and ≥ 1 identity field (the partition key); `operations` and `relations` forbidden |
| action | `Action` | `operations` | `clauses`, `relations`, `triggers: SemanticId[]` | `operations` has exactly 1 item — an action is one invocation; `fields` forbidden |
| ui_component | `UiComponent` | `fields` | `operations`, `clauses`, `relations`, `renders: SemanticId[]` | `fields` has ≥ 1 item and 0 identity fields — props are not identified |
| interface | `Interface` | `operations` | `associated_types: TypeRef[]`, `clauses`, `relations` | `operations` has ≥ 1 item; `fields` forbidden |
| external_contract | `ExternalContract` | `operations`, `clauses` | `provider: SemanticId`, `versioning: VersioningPolicy`, `relations` | `operations` has ≥ 1 item and ≥ 1 guaranteed operation; `clauses` has ≥ 1 item; `fields` forbidden |
| extension_point | `ExtensionPoint` | `operations`, `clauses` | `exposes: SemanticId`, `registration: RegistrationPolicy`, `stability: StabilityPolicy` | `operations` has ≥ 1 item; `clauses` has ≥ 1 item (the stability guarantee); `fields` and `relations` forbidden |
| binary_format | `BinaryFormat` | `clauses` | `records: RecordLayout[]`, `endianness: Endianness`, `serializes: SemanticId[]` | `clauses` has ≥ 1 item (the layout invariants); `fields` and `operations` forbidden |
| rate_limit | `RateLimit` | `clauses` | `thresholds: Threshold[]`, `throttles: SemanticId[]` | `clauses` has ≥ 1 item; `fields` and `operations` forbidden |

- `RouteDecl` SHALL be `{ method: HttpMethod, path: string (minLength 1), operation: Identifier }` with `HttpMethod` the closed set `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`.
- `DeliveryPolicy` SHALL be `{ semantics: DeliverySemantics, ordering?: OrderingScope, retention?: string }` with `DeliverySemantics` the closed set `at_most_once`, `at_least_once`, `exactly_once` and `OrderingScope` the closed set `none`, `partition`, `global`.
- `VersioningPolicy` SHALL be `{ scheme: VersioningScheme, breaking_change_signal?: string }` with `VersioningScheme` the closed set `semver`, `date`, `header`, `none`.
- `RegistrationPolicy` SHALL be `{ mechanism: Identifier, conflict: ConflictPolicy, discovery?: string }` with `ConflictPolicy` the closed set `last_wins`, `first_wins`, `error`.
- `StabilityPolicy` SHALL be `{ compatibility: CompatibilityWindow, deprecation_window?: string }` with `CompatibilityWindow` the closed set `major`, `minor`, `none`.
- `RecordLayout` SHALL be `{ name: Identifier, tag?: string, size?: int32 (min 0), fields: LayoutField[] (minItems 1) }`, and `LayoutField` `{ name: Identifier, offset: int32 (min 0), size: uint32 | Identifier, type: LayoutType }` with `LayoutType` the closed set `u8`, `u16`, `u32`, `u64`, `i8`, `i16`, `i32`, `i64`, `f32`, `f64`, `bytes`, `item_pointer`. A `LayoutField.size` naming an `Identifier` names a sibling field of the same record whose value carries the length; `Endianness` is the closed set `little`, `big`.
- `Threshold` SHALL be `{ scope: LimitScope, metric: Identifier, limit: float64 (min 0), window: string (minLength 1), on_exceeded: ExceedResponse }` with `LimitScope` the closed set `per_token`, `per_tenant`, `per_ip`, `global` and `ExceedResponse` `{ status: int32 (min 100, max 599), retry_after?: boolean, behavior?: string }`.
- Every `fields`, `params`, `clauses`, `operations`, `relations`, and `associated_types` item SHALL be validated by `$ref` to the semantic-core 0.1.0 model, never by a copied definition.
- The TypeSpec source SHALL express the item rules through the official emitter's decorators over open marker models: `@contains(IdentityField)` for "≥ 1 identity field", `@contains(IdentityField) @minContains(0) @maxContains(0)` for "0 identity fields", `@contains(ReturningOperation)` for "≥ 1 returning operation", and `@contains(GuaranteedOperation)` for "≥ 1 guaranteed operation"; `@maxItems(1)` expresses the action rule.
- Every cross-reference a declaration makes (`type.target`, `RelationDecl.target`, `carries`, `requires`, `renders`, `throttles`, `serializes`, `triggers`, `exposes`, `provider`) SHALL be a `SemanticId` or `KernelScalar` per semantic-core, so a bare token is rejected by the schema; resolution against the bundle, and the placeholder `ix://<org>/<repo>/unresolved/<Token>` with its `semantic.unresolved-type` finding, exist today for `type.target` only (quire-rs FR-070) and for the other keys once `agent-ix/quoin#335` publishes their mapping.
- Each schema SHALL describe the declared shape only, never a runtime occurrence (an HTTP request, an enqueued message, a rendered component instance), which is why `Queue` declares the message envelope's fields and no delivery timestamp of a particular message.
- Where a type admits a key the current extractor does not populate (`routes`, `requires`, `carries`, `delivery`, `renders`, `triggers`, `associated_types`, `provider`, `versioning`, `exposes`, `registration`, `stability`, `records`, `endianness`, `serializes`, `thresholds`, `throttles`, `relations`), that key SHALL be optional on that type, so a record produced by today's extractor validates and a future extractor can fill it without a schema change.
- The previous rule SHALL NOT be read as admitting a key on a type whose row forbids it. `relations` in particular is optional on `api_endpoint`, `data_schema`, `action`, `ui_component`, `interface` and `external_contract`, and forbidden on `queue`, `extension_point`, `binary_format` and `rate_limit` — those four are reached through what they carry, expose, serialize or throttle, and the `allowed_links` the manifest declares for them stay the module's edge vocabulary, which is a different surface from the declaration record.
- The test suite SHALL verify every criterion over a key the extractor does not populate against a hand-built JSON record rather than an extracted one, naming that limitation in the test itself, so that no row claims extraction evidence it does not have; the extraction path for those keys is `agent-ix/quoin#335` (mapping) and its quire-rs successor.
- A `RouteDecl.operation` SHALL name an `operations[].name` of the same record. JSON Schema cannot express that rule, so it is a reader rule stated here for the extractor that first populates `routes`; it is not claimed as a schema refusal.
- The schemas SHALL keep definition objects distinct from observed routes, calls, queues, and runtime resources: no model carries an observation key (a measured call count, a discovered route, a live resource id), so a declaration record can never be confused with an extraction from running code.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-004-CON-1 | No model SHALL redeclare a semantic-core model or scalar; the module namespace contributes archetype shapes only (semantic-core NFR-014 kernel discipline). | Architecture | Test |
| FR-004-CON-2 | The empty record `{}` SHALL fail every one of the ten types, because every type requires at least one extractable key. | Integrity | Test |
| FR-004-CON-3 | Protocol-specific detail SHALL live in an optional profile key (`delivery`, `versioning`, `registration`, `stability`, `endianness`), never weakening a required key or an item rule of the common contract. | Compatibility | Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-004-AC-1 | Each of the ten shipped object-type schemas differs from every other in the fingerprint (required key set, admitted key set, item rules) the table fixes; `BinaryFormat` and `RateLimit` share a required set and are separated by their admitted keys alone, which the fingerprint counts. A schema with only `type: object` is absent, and every schema is sealed. | Test |
| FR-004-AC-2 | An api-endpoint record whose `operations` holds one operation with `returns` validates against `ApiEndpoint.json`; the same record with `returns` removed fails; a record carrying `fields` fails. | Test |
| FR-004-AC-3 | A data-schema record with one field validates against `DataSchema.json`; an empty `fields` array fails; a record carrying `operations` fails. | Test |
| FR-004-AC-4 | A queue record with an identity field validates against `Queue.json`, with `delivery` and `carries` accepted when present; the same record with the identity flag removed fails; a record carrying `operations` fails. | Test |
| FR-004-AC-5 | An action record with exactly one operation validates against `Action.json`; a record with two operations fails; a record carrying `fields` fails. | Test |
| FR-004-AC-6 | A ui-component record with one non-identity field validates against `UiComponent.json`, with `operations` accepted when present; a record with an identity field fails. | Test |
| FR-004-AC-7 | An interface record with one operation validates against `Interface.json`, with `associated_types` accepted when present; a record with an empty `operations` array fails; a record carrying `routes` fails. | Test |
| FR-004-AC-8 | An external-contract record with one clause and one operation carrying a `post` clause validates; the same record without `clauses` fails; the same record whose only operation carries no `post` fails. | Test |
| FR-004-AC-9 | An extension-point record with one operation and one clause validates, with `registration` and `stability` accepted when present; a record without `clauses` fails; a record carrying `fields` fails. | Test |
| FR-004-AC-10 | A binary-format record with one clause validates, with `records` and `endianness` accepted when present; a `RecordLayout` whose `fields` array is empty fails; a record carrying `operations` fails. | Test |
| FR-004-AC-11 | A rate-limit record with one clause validates, with `thresholds` accepted when present; a `Threshold` whose `scope` is outside `LimitScope` fails; a record carrying `fields` fails. | Test |
| FR-004-AC-12 | The empty record `{}` fails all ten object-type schemas. | Test |
| FR-004-AC-13 | A `type.target` of `ix://agent-ix/spec-objects-architecture/unresolved/Mystery` is accepted by the schema (it is a `SemanticId`) and reported by the extractor as `semantic.unresolved-type`; a bare `Mystery` string is rejected by the schema. | Test |
| FR-004-AC-14 | Removing an optional profile key (`delivery`, `versioning`, `registration`, `stability`, `endianness`) from an otherwise valid record leaves it valid, and no profile key appears in any model's required list. | Test |
| FR-004-AC-15 | No shipped schema declares an observation key — a measured call count, a discovered route, a live resource id, a timestamp of an observation, or any key whose name marks it as extracted from running code — so a declaration record cannot be read as an observation. This is the ticket's "definition objects remain distinct from observed routes, calls, queues and runtime resources" and the Project 17 resource-vocabulary alignment, expressed as a rule a test can check. | Test |
| FR-004-AC-16 | `relations` is admitted by `ApiEndpoint`, `DataSchema`, `Action`, `UiComponent`, `Interface` and `ExternalContract`, and refused by `Queue`, `ExtensionPoint`, `BinaryFormat` and `RateLimit`. | Test |

## Dependencies

- **Upstream**: semantic-core FR-031 (`ix://agent-ix/filament-core-data/FR-031`)
- **Build**: [FR-002](./FR-002-emitted-json-schemas.md) emits these models
- **Downstream**: [FR-005](./FR-005-executable-skeletons.md), [FR-006](./FR-006-architecture-lowerings.md); `agent-ix/quire-contract-ir#52` and `agent-ix/filament-core-data#36` read these schemas as fixtures
