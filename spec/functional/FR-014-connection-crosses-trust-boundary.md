---
id: FR-014
title: "A connection states the trust boundaries it crosses"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: depends_on
  - target: "ix://agent-ix/spec-objects-architecture/FR-013"
    type: depends_on
  - target: "ix://agent-ix/spec-objects-security/FR-024"
    type: depends_on
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-058"
    type: depends_on
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-084"
    type: depends_on
---
# FR-014: A connection states the trust boundaries it crosses

## Description

A connection states which trust boundaries it crosses. This edge is independent of the `carries` edge: `carries` states what data flows, and `crosses` states where the connection goes. A connection may cross zero or more boundaries. The trust boundary's `trust_level` is authored by the security module as frontmatter and is read from the typed record. Neither edge implies the other.

## Behavior

- The architecture module SHALL declare `crosses` as a `dataflow` edge verb and allow `connection` to link through `crosses` to `trust_boundary`.
- A `crosses` edge from a connection to a trust boundary SHALL validate. A target of any other kind SHALL yield `disallowed-edge-target` naming `crosses`, the target id, and target kind. A missing target SHALL yield a dangling-reference diagnostic naming the target id.
- The architecture manifest SHALL represent `crosses` as a relationship edge, never as a `Connection` or `TrustBoundary` record key.
- `quire relations --json` SHALL report each connection's crossing targets and include the target boundary's selected `trust_level` record key, alongside the `carries` relation and its selected `regulatedCategories` key.
- A connection without a `crosses` edge SHALL validate without a crossing finding at default severities.
- The crossing relation report SHALL not require any connection to cross a boundary; its check is off by default.
- The connection skeleton SHALL show a `type: crosses` relationship whose target is a `trust_boundary`.
- A combined fixture with connection `CONN-PORTAL-LAB`, a `carries` edge to `CLASS-PHI` with `regulated_categories: [health]`, and a `crosses` edge to `BOUND-INTERNET` with `trust_level: untrusted` SHALL report both targets.
- The combined fixture's report SHALL contain no rule finding or denial.
- No classification, crossing, or trust level is inferred.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-014-AC-1 | The manifest declares `crosses` as a `dataflow` edge verb and allows `connection` to target `trust_boundary`; it does not add a `crosses` record key to `Connection.json`. | Test |
| FR-014-AC-2 | A connection crossing to a `trust_boundary` validates. | Test |
| FR-014-AC-3 | A connection crossing to an `asset` fails with `disallowed-edge-target` naming `crosses`, the target id and `asset`; a missing target fails as dangling and names the target id. | Test |
| FR-014-AC-4 | A connection with no crossing validates with no `connection-crosses-trust-boundary` finding at default severities. | Test |
| FR-014-AC-5 | `quire relations --json` reports a connection's `crosses` target with its `trust_level` record key. | Test |
| FR-014-AC-6 | The connection skeleton uses a `crosses` relationship targeting a `trust_boundary`. | Test |
| FR-014-AC-7 | The combined `CONN-PORTAL-LAB` fixture reports `carries → CLASS-PHI` with `regulatedCategories: [health]` and `crosses → BOUND-INTERNET` with `trust_level: untrusted`, with no finding or denial. | Test |

## Dependencies

- FR-007 defines the `connection` kind.
- FR-013 defines the independent `carries` classification edge.
- spec-objects-security FR-024 defines the authored `trust_level` value on `trust_boundary`.
- Quire-rs FR-058 and FR-084 provide required-relation and JSON-report projection behavior.

## Licensing

Use generic terms only. Do not name or quote paywalled standards.
