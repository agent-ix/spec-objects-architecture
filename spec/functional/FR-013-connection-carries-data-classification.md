---
id: FR-013
title: "A connection states the data classifications it carries, and an unclassified connection is reported by an opt-in check"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-010"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-012"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-security/FR-023"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-058"
    type: "depends_on"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-084"
    type: "depends_on"
---
# FR-013: A connection states the data classifications it carries, and an unclassified connection is reported by an opt-in check

Tracked by Linear PLAT-1439.

## Description

A `connection` states its two port ends and a flow direction ([FR-007](./FR-007-systems-model-kinds.md)). Nothing says what data
travels on it. A `connection` SHALL state, through `carries` edges, the data classifications whose data flows on
it. A `data_classification` is owned by `agent-ix/spec-objects-security`; its regulated-data categories (`health`, `personal`,
`financial`) are specified in that module's FR-023, separate from its confidentiality `level`. The boundary-crossing rules of
milestone M2 need both facts as data. This requirement states the edge and the check; it does not apply any rule.

### The edge

A connection document states, in frontmatter `relationships`, `- target: <data_classification id or ix:// uri>` with
`type: carries`. The edge goes from the connection to the classification: one classification is shared by many connections, and
the connection's author knows the payload. The verb `carries` is already declared by `spec-artifacts-iso` (category
`dataflow`) and is reused, not redeclared. `classifies` (from a `data_classification` to stores and endpoints) is left as it is
and is not used for connections.

### Side by side with the crossing edge

PLAT-1532 owns the edge by which a connection crosses a trust boundary. The two edges are independent: `carries` states the
payload, the crossing edge states where the connection goes, and neither implies the other. A connection that carries a
`health` classification and crosses a boundary whose `trust_level` is `untrusted` shows both facts in one `quire relations`
report. M1 reports this and denies nothing; denial is M2.

## Inputs

- The `connection` object type of [FR-007](./FR-007-systems-model-kinds.md).
- The `data_classification` object type and its `regulated_categories` of `agent-ix/spec-objects-security` FR-023.
- quire-rs [FR-058](ix://agent-ix/quire-rs/spec/functional/FR-058) `required_relations` and the
  [FR-084](ix://agent-ix/quire-rs/spec/functional/FR-084) relation report.

## Outputs

- `carries: [data_classification]` in the `connection` `allowed_links`.
- A `traceability.required_relations` entry `connection-carries-classification`.
- `grammar_severity` key `trace:connection-without-classification` set to `off`.

## Behavior

- The `connection` `allowed_links` SHALL list `carries: [data_classification]`, beside `connects` and `realizes_requirement`.
- The module SHALL NOT redeclare `carries` in `edge_types`.
- The module SHALL leave `Connection.json` unchanged, because the edge is a relationship and not a record key.
- The `connection` construct SHALL keep `fields` forbidden.
- Quire SHALL reject a `carries` edge from a connection to anything other than a `data_classification`, reporting
  `disallowed-edge-target` naming the source, the target and its kind.
- Quire SHALL report a `carries` edge to an id no document has as `dangling-reference` naming the file and the id.
- The module SHALL declare the `required_relations` entry `{name: connection-carries-classification, from: connection,
  edges: [carries], to: [data_classification], direction: outgoing, check: connection-without-classification}`.
- The module SHALL set `grammar_severity` `trace:connection-without-classification` to `"off"`, following the
  `trace:unassigned-class` precedent of [FR-012](./FR-012-software-safety-class-assignment.md), so a corpus without data-flow
  modelling draws no finding. A project turns the check on.
- `quire relations --json` SHALL list, for each connection, its `carries` targets together with each target's
  `regulated_categories`, and a gap row for each connection with no `carries` edge.
- `quire relations --json` SHALL list, per classification, the connections that carry it.
- The report SHALL NOT include the confidentiality `level`, which is a `## Properties` table row that the engine does not
  extract.
- The module SHALL NOT derive a `carries` edge, a category or a level.
- The module SHALL issue no denial.

## Engine impact

No quire-rs change is expected. The edge uses the existing `allowed_links`, `required_relations` (FR-058) and relation
report (FR-084) mechanisms, and `ConnectionRecord` in `src/semantic/systems.rs` is unchanged. The category list is extracted
by security FR-023 without `multiple: true` and needs no engine change. If the FR-084 report cannot show a target's
`regulated_categories`, that gap is raised against quire-rs FR-084 and the work moves into PLAT-1441.

## Out of scope

- Boundary-crossing rules, denials and sinks (the LLM prompt and tool call): PLAT-1533, PLAT-1535, PLAT-1537, PLAT-1538.
- The trust-boundary crossing edge: PLAT-1532 owns it.
- Records of processing: PLAT-1657. The threat-model artifact: milestone M3.
- Any automatic derivation of category or level from field names, data schemas or code.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-013-AC-1 | A connection with a `carries` relationship to a `data_classification` validates with no `disallowed-edge-type` or `disallowed-edge-target` warning. | Test |
| FR-013-AC-2 | A connection with `carries` to a `part` fails with `disallowed-edge-target` naming the source, the target and its kind, and `carries` to an id no document has fails with `dangling-reference` naming the file and the id. | Test |
| FR-013-AC-3 | With `trace:connection-without-classification` turned on, a connection with no `carries` edge yields that finding, and a connection with a `carries` edge to a `data_classification` yields none. | Test |
| FR-013-AC-4 | With the default severity, an unclassified connection yields no `trace:connection-without-classification` finding. | Test |
| FR-013-AC-5 | `quire relations --json` over a fixture lists each connection with its carried classifications and their `regulated_categories`, lists a gap row for an unclassified connection, lists per classification the connections that carry it, and contains no `level` value. | Test |
| FR-013-AC-6 | In a fixture where a connection carries a `health` classification and, through the PLAT-1532 crossing edge, crosses a boundary whose `trust_level` is `untrusted`, one `quire relations --json` report shows both facts and the run issues no denial. | Test |
| FR-013-AC-7 | `Connection.json` is unchanged, a connection record carrying `fields` still fails, and the manifest declares `carries` neither in `edge_types` nor for any kind other than `connection`. | Test |
| FR-013-AC-8 | The `connection-carries-classification` entry has exactly the fields stated above and `grammar_severity` maps `trace:connection-without-classification` to `off`. | Test |

## Dependencies

- **Upstream**: [FR-007](./FR-007-systems-model-kinds.md), [FR-010](./FR-010-design-realization-edge.md), [FR-012](./FR-012-software-safety-class-assignment.md); `agent-ix/spec-objects-security` FR-023; quire-rs FR-058 and FR-084
- **Sibling**: PLAT-1532 (crossing edge)
- **Downstream**: PLAT-1440, PLAT-1441, PLAT-1533
