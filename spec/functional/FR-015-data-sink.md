---
id: FR-015
title: "A data_sink declares where data lands, with a closed kind and a stated processor agreement, fed by delivers_to edges"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-002"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-005"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-009"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-013"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-security/FR-023"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-058"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-096"
    type: "depends_on"
  - target: "ix://agent-ix/quire-cli/spec/functional/FR-026"
    type: "depends_on"
---
# FR-015: A data_sink declares where data lands, with a closed kind and a stated processor agreement, fed by delivers_to edges

Tracked by Linear PLAT-1533 (implemented by PLAT-1535).

## Description

[FR-013](./FR-013-connection-carries-data-classification.md) lets a connection state the data classifications it carries. It
says nothing about where that data lands: a screen, a log, a file, an analytics event, a prompt sent to a model provider, the
arguments of a tool call, an outbound message, a datastore. The module SHALL let an author declare that place as a `data_sink`
and feed it through `delivers_to` edges, so the boundary-crossing rules of milestone M2 can read the sink as data. A rule is
module data evaluated by the generic `flow_rules` kind of quire-rs FR-096; this requirement declares the sink and its edges and
applies no rule. `flow_rules` is the only new engine kind: the `data_sink` type, the `delivers_to` verb, and every rule and
remediation that reads them are module data.

### The object type

A `data_sink` document states these top-level frontmatter fields. Rules read the values as authored frontmatter, so each is
frontmatter and not a body section.

| Key | Required | Values |
|----|----|----|
| `kind` | yes | the closed enum `SinkKind`: `ui_screen`, `log`, `export_file`, `analytics_event`, `llm_prompt`, `tool_call`, `outbound_message`, `datastore` |
| `processor_agreement` | yes | the closed enum `covered`, `not_covered`, `not_applicable`, `unknown` |
| `processor` | no | the id of the `part` (with an external role) or `external_contract` that receives the data |
| `region` | no | a list of region codes: ISO 3166-1 alpha-2, or `eu`, or `eea`; where the data is processed or stored |
| `purpose` | no | a list of purpose names, free tokens a project uses consistently |
| `audience_roles` | no | a list of `role` ids (`agent-ix/spec-objects-security` `role`) who see the sink's content |

`llm_prompt` covers the prompt and the context window sent to a model provider. `tool_call` covers the arguments passed to a
tool or function an agent invokes. `SinkKind` and the `processor_agreement` enum are closed: any value outside them is
refused. `processor_agreement` is stated by a person; nothing derives it, and `unknown` is a stated value and not a default.

The values are declared once as TypeSpec enums, so the emitted schemas carry them and a rule's `any_of` is checked against them
at module load (quire-rs FR-096). The module declares them on a self-contained **open** frontmatter schema,
`DataSinkFrontmatter`, referenced by the `data_sink` object type through `frontmatter_schema_ref` in the way
[FR-012](./FR-012-software-safety-class-assignment.md) references `PartFrontmatter` (additional keys admitted, no `$ref`).
The same keys are extracted by `frontmatter_field` locators into the declaration record `DataSink` (`kind`,
`processorAgreement` required; `processor`, `region`, `purpose`, `audienceRoles` optional per
[FR-009](./FR-009-optional-sections-optional-keys.md)), emitted as `DataSink.json` per [FR-002](./FR-002-emitted-json-schemas.md).
The `data_sink` type is not a systems-model kind: it has no `construct` and no table; its body is prose.

### The edges

- `connection --delivers_to--> data_sink`. The connection's `carries` set ([FR-013](./FR-013-connection-carries-data-classification.md))
  is the data reaching the sink.
- `part --delivers_to--> data_sink`, for a part that writes the sink directly. A part carries no classification, so the sink
  states its own `carries` edges: `data_sink.allowed_links` includes `carries: [data_classification]`.

The data a sink reaches is therefore the union of the classifications its feeding connections carry and its own `carries`
edges. The module declares both sets of edges and never merges them; a rule states the union with two paths (quire-rs FR-096).

`delivers_to` is a new verb of this module's `edge_types`, `category: dataflow`, and is declared by this module only. `carries`
is already declared (`spec-artifacts-iso`, category `dataflow`) and is reused, not redeclared. A person states the edges; the
module derives none. A connection that carries nothing and delivers to a sink is a valid statement of an unclassified flow.

## Inputs

- The `part`, `connection` and `external_contract` object types of [FR-007](./FR-007-systems-model-kinds.md) and
  [FR-004](./FR-004-role-schemas.md), and the `carries` edge of [FR-013](./FR-013-connection-carries-data-classification.md).
- The `data_classification` and `role` object types of `agent-ix/spec-objects-security` (FR-023 for the regulated categories).
- quire-rs [FR-096](ix://agent-ix/quire-rs/spec/functional/FR-096) `flow_rules`, which reads sink fields and edges, and the
  [FR-058](ix://agent-ix/quire-rs/spec/functional/FR-058) `where` and enum lookup it shares.
- quire-cli [FR-026](ix://agent-ix/quire-cli/spec/functional/FR-026) `quire relations --flow`.
- PLAT-1532 (FR-014), the trust-boundary crossing edge, which is a sibling and not a dependency of the sink.

## Outputs

- The object type `data_sink`, exported, with `data_schema` `schemas/DataSink.json` and `frontmatter_schema_ref`
  `schemas/DataSinkFrontmatter.json`.
- TypeSpec models `DataSink` and `DataSinkFrontmatter` and the closed enums `SinkKind` and `ProcessorAgreement`.
- The skeleton `skeletons/data_sink.md`.
- The edge verb `delivers_to` in `edge_types`.
- `delivers_to: [data_sink]` in the `allowed_links` of `connection` and `part`, and `carries: [data_classification]` on `data_sink`.

## Behavior

### Typed record and validation

- The `data_sink` object type SHALL require `kind` and `processor_agreement`, and SHALL admit `processor`, `region`, `purpose` and `audience_roles` as optional.
- `SinkKind` SHALL list exactly `ui_screen`, `log`, `export_file`, `analytics_event`, `llm_prompt`, `tool_call`, `outbound_message` and `datastore`, and SHALL admit no other value.
- The `processor_agreement` enum SHALL list exactly `covered`, `not_covered`, `not_applicable` and `unknown`, and SHALL admit no other value.
- A `data_sink` document with a `kind` outside `SinkKind`, or a `processor_agreement` outside the enum, SHALL fail validation naming the field and the value.
- A `data_sink` document with `kind` or `processor_agreement` absent SHALL fail validation naming the missing field; the module SHALL NOT supply a default.
- `region` SHALL be a list of strings, each an ISO 3166-1 alpha-2 code or `eu` or `eea`; `purpose` and `audience_roles` SHALL be lists of non-empty strings.
- The extracted `DataSink` record SHALL carry `kind` and `processorAgreement` as written, and each optional key if and only if its frontmatter field is present.
- The emitted `DataSink.json` and `DataSinkFrontmatter.json` SHALL carry the two enums as closed `enum` lists and SHALL carry no `default`.

### A sink is fed from connections and parts

- The `connection` and `part` `allowed_links` SHALL each list `delivers_to: [data_sink]`, and the `data_sink` `allowed_links` SHALL list `carries: [data_classification]`.
- A `delivers_to` edge from a connection or a part to a `data_sink` SHALL validate with no `disallowed-edge-type` or `disallowed-edge-target` finding.
- A `delivers_to` edge to a target in the loaded bundle that is not a `data_sink` SHALL yield `disallowed-edge-target` naming the source, the target and its kind (quire-rs FR-040); a `delivers_to` edge from a `port` or `allocation` SHALL yield `disallowed-edge-type`.
- A `delivers_to` edge to an id no document in the loaded bundle has SHALL yield `dangling-reference` naming the file and the id (quire-rs FR-026).
- A `carries` edge from a `data_sink` to a `data_classification` SHALL validate; one to any other kind SHALL yield `disallowed-edge-target`.
- Among `part`, `port`, `connection` and `allocation`, only `connection` and `part` SHALL admit `delivers_to`, and only `connection` SHALL admit `carries`.
- The module SHALL NOT redeclare `carries` in `edge_types`, and SHALL declare `delivers_to` once, with `category: dataflow`.
- The module SHALL leave `Connection.json` unchanged: `delivers_to` is a relationship and not a record key, and the `connection` construct keeps `fields` forbidden.

### What a rule can read: exact facts, no inference

- A `data_sink` document SHALL expose `kind`, `processor_agreement`, `processor`, `region`, `purpose` and `audience_roles` as top-level frontmatter, exactly as authored, to a quire-rs FR-096 `flow_rules` condition.
- A `flow_rules` condition `any_of` over `kind` or `processor_agreement` in this module's rules SHALL be checked at module load against these two enums; a value outside them (for example `any_of: [medical]` on a sink field) SHALL fail the module load naming the rule and the value (quire-rs FR-096).
- Over a seeded model in which a `connection` that carries a `health` classification delivers to a `data_sink` with `kind: llm_prompt` and `processor_agreement: not_covered`, `quire relations --flow --json` SHALL list that sink in `facts.sinks`, with its `kind`, `processor_agreement` and `delivers_to` edge, and SHALL list the connection and the classification it reaches.
- Over the same model with `processor_agreement` changed to `covered`, the `quire relations --flow --json` facts for the sink SHALL show `covered` and the report SHALL list no denial for it under the LLM-sink rule; with `unknown`, the sink SHALL appear unchanged apart from that value and a denial SHALL be listed.
- `unknown` SHALL be the only way to state that the agreement is not known; an absent `processor_agreement` is a validation failure.
- The module SHALL NOT derive a `kind`, a `processor_agreement`, a `region`, an edge or a classification for a sink, from a name, a body, a connection, a code symbol or a vendor; and SHALL NOT infer a sink from a connection that has no `delivers_to` edge.
- A connection with no `delivers_to` edge SHALL contribute no sink to `facts.sinks` and be reported as such, not defaulted to a sink kind.
- The module SHALL issue no denial itself; denial is the work of the `flow_rules` the security module ships and the engine evaluates.

### Skeleton, schema and manifest consistency

- The skeleton `skeletons/data_sink.md` SHALL validate with zero errors under [FR-005](./FR-005-executable-skeletons.md), SHALL state `kind` and `processor_agreement`, and SHALL name the optional fields in its contract comment without supplying a value for any of them beyond what the required fields need. The skeleton SHALL NOT state `processor_agreement: covered`.
- The `data_sink` object type SHALL be exported in `semantic.exports`, and the manifest `description` SHALL list it.
- The enums, the frontmatter schema, the record schema, the `yield_pattern` locators and the skeleton SHALL state the same keys and the same two value lists. `make schemas-check` SHALL pass.
- No file of the module SHALL list a region code, a purpose or a role id as a default.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-015-CON-1 | The module SHALL use generic terms (regulated data, processor agreement, trust boundary). | Design | Inspection |
| FR-015-CON-2 | The module SHALL name no paywalled standard in any heading, description, example, skeleton or fixture. | Design | Inspection |
| FR-015-CON-3 | No file of the module computes, fills in or rewrites a `kind`, a `processor_agreement`, a region or a `delivers_to` edge. | Design | Inspection |
| FR-015-CON-4 | `flow_rules` is the only new engine kind; the module adds no engine code, no Python rule and no hard-coded sink list. | Scope | Inspection |

## Acceptance Criteria

These criteria carry the sink-side share of the ticket's draft criteria a to j; the other shares are named after the table.

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-015-AC-1 | (Validation, typed record.) A `data_sink` document with each of the eight `SinkKind` values and each of the four `processor_agreement` values validates; a `kind` outside `SinkKind` (for example `medical`), a `processor_agreement` outside the enum, and a document missing either required field each fail validation naming the field; the emitted `DataSink.json` and `DataSinkFrontmatter.json` list exactly the eight and the four values, with no `default`, and `make schemas-check` passes. | Test |
| FR-015-AC-2 | (Typed record.) The extracted `DataSink` record carries `kind` and `processorAgreement` as written, and carries `processor`, `region`, `purpose` and `audienceRoles` if and only if their frontmatter fields are present; `region`, `purpose` and `audience_roles` that are not lists of non-empty strings fail. | Test |
| FR-015-AC-3 | (Sink from a connection.) A connection with a `delivers_to` edge to a `data_sink` validates with no `disallowed-edge-type` or `disallowed-edge-target` finding at any severity; a `delivers_to` to a non-`data_sink` target yields `disallowed-edge-target` naming source, target and kind, and one to an id no document has yields `dangling-reference` naming the file and id. | Test |
| FR-015-AC-4 | (Sink from a part.) A part with a `delivers_to` edge to a `data_sink` validates, and a `data_sink` with a `carries` edge to a `data_classification` validates; a `data_sink` `carries` to any other kind yields `disallowed-edge-target`; a `port` or `allocation` with `delivers_to` yields `disallowed-edge-type`. | Test |
| FR-015-AC-5 | (Allowed links.) `connection` and `part` list `delivers_to: [data_sink]`, `data_sink` lists `carries: [data_classification]`, and among the four systems kinds only `connection` admits `carries` and only `connection` and `part` admit `delivers_to`; `delivers_to` is declared once in `edge_types` with `category: dataflow`, `carries` is not redeclared, and `Connection.json` is unchanged. | Test |
| FR-015-AC-6 | (Exact fact, draft criterion c.) Seeded model: a connection carrying a `health` classification delivers to a `data_sink` with `kind: llm_prompt` and `processor_agreement: not_covered`. `quire relations --flow --json` lists the sink in `facts.sinks` with `kind: llm_prompt`, `processor_agreement: not_covered` and the feeding connection and classification, and, with the security module loaded, one denial under the LLM-sink rule naming that sink. | Test |
| FR-015-AC-7 | (Exact fact, draft criterion d.) The same model with `processor_agreement: covered` lists the sink with `covered` and no denial under the LLM-sink rule; with `unknown`, the sink lists `unknown` and one denial is reported; with `not_applicable`, the report lists `not_applicable` and the outcome is whatever the loaded rule states for it, never an engine default. | Test |
| FR-015-AC-8 | (Exact fact, draft criterion e.) A `flow_rules` entry whose `any_of` names a value outside the `SinkKind` or `processor_agreement` enum of this module's frontmatter schema (for example `any_of: [medical]` on `kind`) makes the module fail to load, naming the rule and the value. | Test |
| FR-015-AC-9 | (No inference, draft criterion g.) A corpus with no `delivers_to` edge, and one whose connections carry no classification, yields no denial from any starter rule; a connection with no `delivers_to` edge adds no entry to `facts.sinks`, and no sink, kind, agreement, region or edge appears in the report that no document states. | Test |
| FR-015-AC-10 | (Report determinism and exit, draft criteria h and i, sink side.) `quire relations --flow --json` over the seeded sink model gives byte-identical output across two runs, and `--strict` exits 1 when the sink model yields a denial and 0 when it yields none. | Test |
| FR-015-AC-11 | (Severity, draft criterion j, sink side.) With `--severity trace:<check>=warning` for the LLM-sink rule's check, the sink's denial is reported as a warning and `quire validate` exits 0. | Test |
| FR-015-AC-12 | (Skeleton and consistency.) `skeletons/data_sink.md` validates with zero errors, states `kind` and `processor_agreement` and no `covered` value, names the optional fields in its contract comment; the exports, manifest description, enums, both schemas, locators and skeleton state the same keys and the same two value lists; no file of the module lists a default region, purpose or role id. | Test |
| FR-015-AC-13 | (Rights.) No heading, description, example, skeleton or fixture added by this requirement names a paywalled standard, and no file computes or defaults a `kind`, `processor_agreement`, region or `delivers_to` edge. | Inspection |

Draft criteria a, b and f (the rule outcome, the protecting control and the load failures other than an out-of-enum value) are owned by quire-rs FR-096 and `agent-ix/spec-objects-security` FR-025. This requirement owns the sink-side share: c and d (AC-6, AC-7), e for sink enums (AC-8), g (AC-9), h and i (AC-10) and j (AC-11), beside the validation and typed-record criteria (AC-1 to AC-5, AC-12, AC-13).

## Out of scope

- The `flow_rules` and `remediations` manifest kinds and their evaluation: quire-rs FR-096 and PLAT-1479.
- The `control` `safeguards` field, `protects` onto `connection` and `data_sink`, and the starter rules: `agent-ix/spec-objects-security` FR-025 (PLAT-1540).
- The trust-boundary crossing edge: PLAT-1532 (FR-014).
- The report command: quire-cli FR-026. Solver lowering: PLAT-1541, which waits on QSL-1900 (the production contract-package step) and
  needs, from quire-analyze, enum sorts, records and finite-collection quantifiers (FR-020, FR-031). This module writes no QSL.
- Records of processing (PLAT-1657), threat-model artifacts (milestone M3), runtime monitors, Cedar, and any automatic derivation
  of a category, trust level, processor agreement or safeguard.

## Dependencies

- **Upstream**: [FR-002](./FR-002-emitted-json-schemas.md), [FR-004](./FR-004-role-schemas.md), [FR-005](./FR-005-executable-skeletons.md), [FR-007](./FR-007-systems-model-kinds.md), [FR-009](./FR-009-optional-sections-optional-keys.md), [FR-013](./FR-013-connection-carries-data-classification.md); `agent-ix/spec-objects-security` FR-023; quire-rs FR-058 and FR-096; quire-cli FR-026
- **Sibling**: PLAT-1532 (FR-014, the crossing edge); `agent-ix/spec-objects-security` FR-025
- **Downstream**: PLAT-1535, PLAT-1537, PLAT-1538, PLAT-1540, PLAT-1541 (waits on QSL-1900), PLAT-1479
