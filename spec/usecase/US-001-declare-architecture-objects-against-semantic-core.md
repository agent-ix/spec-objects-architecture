---
id: US-001
title: "Declare architecture object types against semantic-core"
type: US
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/StR-001"
    type: "traces_to"
---
# US-001: Declare architecture object types against semantic-core

## Story

**As a** maintainer of the architecture object module
**I want** every architecture object type (api endpoint, data schema, queue, action, UI component, interface, external contract, extension point, binary format, rate limit) to carry a real structural contract expressed in the shared semantic-core grammar
**So that** spec authors write one typed declaration per object, reviewers and generators read one declaration record per object, and the same record validates identically in Quire, Quoin, and the compiler.

The story is stated from the maintainer's perspective and does not prescribe
the emitter, the file layout, or the extraction engine.

## Context

Today every object type in `manifest.yaml` carries `data_schema: {type: object}`,
which types nothing: an API endpoint and a rate limit are indistinguishable to
a consumer, `## Contract` is free prose or untyped YAML, and no cross-reference
between two objects is checked — an endpoint cannot say which record it
returns. The semantic-core grammar (`agent-ix/filament-core-data#35`) and the
semantic-module contract (`agent-ix/quoin#293`, `agent-ix/quire-rs#388`) now
exist and are merged, and `agent-ix/spec-objects-business#4` has taken the
first module through the contract. This module is the second, and the one that
owns the operation-shaped and reference-shaped lowerings the downstream
frontends (`agent-ix/quire-contract-ir#52`,
`agent-ix/filament-core-data#36`) need.

## Acceptance Examples (Illustrative)

These examples clarify the maintainer's expectations. They are illustrative
only, not test cases and not verification criteria.

### US-001-EX-1: An interface contract extracts to typed operations

- **Given** the `interface` skeleton whose `## Operations` subsections declare `prepare_ip_query` and `score_ip_batch`
- **When** Quire extracts it under this module
- **Then** the record carries one `OperationDecl` per subsection with typed params and returns, and validates against the shipped `Interface.json`

### US-001-EX-2: An endpoint names the record it returns

- **Given** an `api_endpoint` artifact whose operation returns the `data_schema` titled `ArtifactRecord`
- **When** Quire resolves the artifact under a bundle index built from the module's skeletons
- **Then** the return `TypeRef` targets `ix://agent-ix/spec-objects-architecture/type/ArtifactRecord` with no unresolved-type finding

### US-001-EX-3: A rate limit with no thresholds is refused

- **Given** a `rate_limit` artifact declaring no threshold
- **When** Quire validates it
- **Then** validation fails naming the rate-limit schema, because a rate limit that limits nothing is not a declaration

## Options (Exploratory)

Approaches discussed: hand-authoring one JSON Schema per type; generating the
schemas from a TypeSpec package that imports `@agent-ix/semantic-core`;
deriving the schemas from the skeletons. Only the TypeSpec route keeps one
source for the grammar and its vocabulary; it is the route the authoring
contract on the ticket already names, and the route the sibling business
module took.

## Constraints (Contextual)

No corpus repository may be edited; existing `body_extraction` locators stay
as they are so current artifacts keep extracting; the change is advisory until
corpus promotion, and it enables no impact propagation or extraction
behaviour. This context is not binding here and is refined in the functional
and non-functional requirements.

## Dependencies (Contextual)

Upstream: semantic-core 0.1.0 on npm.ix, the module-manifest schema with the
`semantic` block, Quire 0.46.0 with `extract_semantic`. Downstream: the
frontends that read this module's skeletons as fixtures.

## Priority and Risk (Informative)

P1 on the Track A programme. The risk if unmet is that the downstream
frontends have no architecture-object fixture, and that the operation-shaped
lowering — the one the business module never exercised — has no reference.

## Notes (Informative)

Open question captured for later analysis: which sections beyond
`## Properties`, `## Invariants`, and `## Operations` the extraction engine
should read (`## Layout`, `## Thresholds`, `## Registration`, `## Stability`).
The schemas declare those keys; extraction of them is an engine concern.

## Traceability (Informative)

Traces to [StR-001](../stakeholder/StR-001-module-activation.md); implemented
by [FR-002](../functional/FR-002-emitted-json-schemas.md),
[FR-003](../functional/FR-003-semantic-manifest-contract.md),
[FR-004](../functional/FR-004-role-schemas.md),
[FR-005](../functional/FR-005-executable-skeletons.md), and
[FR-006](../functional/FR-006-architecture-lowerings.md).
