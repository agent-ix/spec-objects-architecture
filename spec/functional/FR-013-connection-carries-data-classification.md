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

## Description

A `connection` states its two port ends and a flow direction ([FR-007](./FR-007-systems-model-kinds.md)). Nothing says what data
travels on it. The module SHALL let a `connection` state, through `carries` edges, the data classifications whose data flows on
it. Stating them is optional; a project that wants every connection classified turns the completeness check on. A `data_classification` is owned by `agent-ix/spec-objects-security`; its regulated-data categories (`health`, `personal`,
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
- A `traceability.required_relations` entry `connection-carries-classification` (the per-connection view) with
  `record_keys: [regulatedCategories]`.
- A `traceability.required_relations` entry `classification-carried-by-connection` (the per-classification view) with
  `record_keys: [regulatedCategories]`.
- `grammar_severity` keys `trace:connection-without-classification` and `trace:classification-without-connection`, both set
  to `off`.

## Behavior

- The `connection` `allowed_links` SHALL list `carries: [data_classification]`, beside `connects` and `realizes_requirement`.
- The module SHALL NOT redeclare `carries` in `edge_types`.
- The module SHALL leave `Connection.json` unchanged, because the edge is a relationship and not a record key.
- The `connection` construct SHALL keep `fields` forbidden.
- A `carries` edge from a connection to a target in the loaded bundle that is not a `data_classification` SHALL yield
  `disallowed-edge-target` naming the source, the target and its kind (quire-rs FR-040).
- A `carries` edge to a bare id, or to an `ix://` target under a loaded member's authority, that no document in the loaded
  bundle has SHALL yield `dangling-reference` naming the file and the id (quire-rs FR-026). An `ix://` target under an authority
  that no loaded member declares SHALL NOT yield `dangling-reference` when the source member declares its identity (quire-rs
  FR-085).
- The module SHALL declare the `required_relations` entry `{name: connection-carries-classification, from: connection,
  edges: [carries], to: [data_classification], direction: outgoing, check: connection-without-classification}`.
- The module SHALL declare the reverse `required_relations` entry `{name: classification-carried-by-connection, from:
  data_classification, edges: [carries], to: [connection], direction: incoming, check: classification-without-connection}`,
  so the per-classification view is a declared relation and not an engine side effect.
- Both `required_relations` entries SHALL set `record_keys: [regulatedCategories]`, the generic FR-058/FR-084 projection
  allow-list, so the module selects the key and the engine holds no category names.
- The relation report SHALL contain `regulatedCategories` on a document or linked entry if and only if a valid FR-084
  `record` for that entry contains the selected key.
- The relation report SHALL omit `regulatedCategories` from a document or linked entry when FR-084 omits `record` for it
  (unresolved schema, invalid record or empty selected projection) or the key is absent from the `record`.
- The relation report SHALL NOT expose, at any depth, a record key outside the entry's `record_keys`, including the
  confidentiality `level`.
- The module SHALL set `grammar_severity` `trace:connection-without-classification` and
  `trace:classification-without-connection` to `"off"`, following the `trace:unassigned-class` precedent of
  [FR-012](./FR-012-software-safety-class-assignment.md), so a corpus without data-flow modelling draws no finding. A project
  turns either check on.
- The no-finding claim above holds for a corpus that loads `agent-ix/spec-objects-security`, the owner of the
  `data_classification` vocabulary; with it absent and no `data_classification` document, quire-rs reports
  `trace:undeclared-relation-vocabulary`, which is separate from the `off` keys.
- With the quire-rs FR-084 change routed through PLAT-1441, `quire relations --json` SHALL list, for each connection, its
  `carries` targets together with each target's `regulatedCategories` where the report contains it, and a gap row for each
  connection with no `carries` edge.
- `quire relations --json` SHALL list, per classification, the connections that carry it, from the reverse relation.
- The module SHALL NOT derive a `carries` edge, a category or a level.
- The module SHALL issue no denial.

## Engine impact

The edge uses the existing `allowed_links`, `required_relations` (quire-rs FR-058) and relation report (quire-rs FR-084)
mechanisms, and `ConnectionRecord` in `src/semantic/systems.rs` is unchanged. The edge, the relation routing, both `off` keys
and the severities need no engine change beyond the `record_keys` projection below.

The record projection does need an engine change. quire-rs FR-058 and FR-084 add a generic `record_keys` allow-list to
`required_relations` entries, routed through PLAT-1441, which also owns the security-side change for the category key
(`agent-ix/spec-objects-security` FR-023). This module selects the camelCase record key `regulatedCategories` on both the
document and the linked entries; the engine does not know the key name and projects only the keys an entry lists. `level` is
excluded by this module's `record_keys` allow-list, not because the engine fails to extract it. FR-013-AC-5, AC-6 and AC-9
hold once that change lands.

## Out of scope

- Boundary-crossing rules, denials and sinks (the LLM prompt and tool call): PLAT-1533, PLAT-1535, PLAT-1537, PLAT-1538.
- The trust-boundary crossing edge: PLAT-1532 owns it.
- Records of processing: PLAT-1657. The threat-model artifact: milestone M3.
- Any automatic derivation of category or level from field names, data schemas or code.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-013-AC-1 | A connection with a `carries` relationship to a `data_classification` validates with no `disallowed-edge-type` or `disallowed-edge-target` finding at any severity. | Test |
| FR-013-AC-2 | In a loaded bundle, a connection with `carries` to a `part` yields `disallowed-edge-target` naming the source, the target and its kind, and `carries` to an id no document has yields `dangling-reference` naming the file and the id. | Test |
| FR-013-AC-3 | With `trace:connection-without-classification` turned on, a connection with no `carries` edge yields that finding, and a connection with a `carries` edge to a `data_classification` yields none. With `trace:classification-without-connection` turned on, a `data_classification` that no connection carries yields that finding, and one that a connection carries yields none. | Test |
| FR-013-AC-4 | With the default severities, in a corpus that loads `spec-objects-security`, an unclassified connection yields no `trace:connection-without-classification` finding and an uncarried classification yields no `trace:classification-without-connection` finding. | Test |
| FR-013-AC-5 | After the FR-084 change routed through PLAT-1441, `quire relations --json` over a fixture lists each connection with its carried classifications and their `regulatedCategories`, lists a gap row for an unclassified connection, and lists per classification the connections that carry it. Where the classification's valid record has `regulatedCategories`, that value appears in both the per-connection and per-classification views. Whether or not `regulatedCategories` is present, no record key outside `record_keys`, including `level`, appears at any depth in either view. | Test |
| FR-013-AC-6 | Integration criterion, verified once PLAT-1532 (the crossing edge) and the FR-084 change in PLAT-1441 have both landed: in a fixture where a connection carries a `health` classification and, through the PLAT-1532 crossing edge, crosses a boundary whose `trust_level` is `untrusted`, one `quire relations --json` report shows both facts and the run issues no denial. PLAT-1440 alone does not satisfy it. | Test |
| FR-013-AC-7 | `Connection.json` is unchanged, a connection record carrying `fields` still fails, and the architecture manifest does not redeclare `carries` in its own `edge_types`, and among the four systems kinds (`part`, `port`, `connection`, `allocation`) only `connection` admits `carries` to `data_classification`. This criterion does not cover the existing `queue` kind: its `carries` links to `data_schema` and `event` remain valid and unchanged. | Test |
| FR-013-AC-8 | The `connection-carries-classification` and `classification-carried-by-connection` entries have exactly the fields stated above, including `record_keys` equal to exactly `[regulatedCategories]` on both, and `grammar_severity` maps `trace:connection-without-classification` and `trace:classification-without-connection` to `off`. | Test |
| FR-013-AC-9 | After the FR-084 change routed through PLAT-1441, where FR-084 omits `record` for a classification (unresolved schema, invalid record or empty selected projection) or its `record` lacks `regulatedCategories`, the `quire relations --json` entry for that classification has no `regulatedCategories` in either view. | Test |

## Dependencies

- **Upstream**: [FR-007](./FR-007-systems-model-kinds.md), [FR-010](./FR-010-design-realization-edge.md), [FR-012](./FR-012-software-safety-class-assignment.md); `agent-ix/spec-objects-security` FR-023; quire-rs FR-058 and FR-084
- **Sibling**: PLAT-1532 (crossing edge); FR-013-AC-6 depends on it and on the PLAT-1441 FR-084 change
- **Downstream**: PLAT-1440, PLAT-1441, PLAT-1533
