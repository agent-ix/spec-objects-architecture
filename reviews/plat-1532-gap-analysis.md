---
id: SR-037
title: "gap-analysis review — PLAT-1532 spec-objects-architecture"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; FR-007-AC-5; FR-014-AC-1..7; tests/test_systems_kinds.py; tests/test_trust_crossings.py"
review_set: subset
---

## Summary

The test matrix tags all new FR-014 criteria, but changed FR-007-AC-5 is not backed by a passing test: TC-104 fails because it rejects the new connection-to-trust_boundary allowed link. The criterion therefore has no passing evidence for the declared link set.

## Verdict

**FAIL** — a high-severity defect is present.

## Scope

- Examined: FR-007-AC-5; FR-014-AC-1..7; tests/test_systems_kinds.py; tests/test_trust_crossings.py.
- Ticket: PLAT-1532; PR #54; reviewed head `8dc54d1e40761e196beeb6d1b4bc471e0368196b`.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | The test matrix tags all new FR-014 criteria, but changed FR-007-AC-5 is not backed by a passing test: TC-104 fails because it rejects the new connection-to-trust_boundary allowed link | tests/test_systems_kinds.py:262 |

## Evidence

The declared systems edge verbs and three roles are present, `interface` carries `systems-interface`, and the systems kinds' `allowed_links` use those verbs plus `realizes_requirement` ([FR-010](./FR-010-design-realization-edge.md)); `connection` additionally admits `carries` ([FR-013](./FR-013-connection-carries-data-classification.md)) and `crosses` ([FR-014](./FR-014-connection-crosses-trust-boundary.md)). The verbs take declared roles or `*`, and `realizes_requirement` takes only `FR` and `NFR`.

Observed finding: The test matrix tags all new FR-014 criteria, but changed FR-007-AC-5 is not backed by a passing test: TC-104 fails because it rejects the new connection-to-trust_boundary allowed link. The criterion therefore has no passing evidence for the declared link set.

## Examined Units

- `FR-007-AC-5` (examined): “The declared systems edge verbs and three roles are present, interface carries systems-interface, and the systems kinds allowed_links use those verbs plus realizes_requirement; connection additionally admits carries and crosses.”
- `FR-014-AC-1..7` (examined): “Valid crossing, wrong-kind and dangling links, required trust_level, typed extraction, combined relation report, and updated fixtures are tested.”
