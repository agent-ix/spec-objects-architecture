---
id: SR-036
title: "code-review review — PLAT-1532 spec-objects-architecture"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; tests/test_trust_crossings.py; tests/test_data_flow_edges.py; tests/test_systems_kinds.py"
review_set: subset
---

## Summary

The changed allowed_links adds connection -> trust_boundary, but the existing TC-104 test still requires every target other than carries to be a declared role. Running that test fails at tests/test_systems_kinds.py:262 with AssertionError (connection, trust_boundary). Update the assertion to admit the declared trust_boundary object kind for crosses and include crosses in the verb contract. This is a high finding because the changed FR-007-AC-5 evidence fails. In addition, the new test module duplicates _validate, _relations, and _lines from tests/test_data_flow_edges.py; the repeated helpers can drift and should be shared/generalized.

## Verdict

**FAIL** — a high-severity defect is present.

## Scope

- Examined: tests/test_trust_crossings.py; tests/test_data_flow_edges.py; tests/test_systems_kinds.py.
- Ticket: PLAT-1532; PR #54; reviewed head `8dc54d1e40761e196beeb6d1b4bc471e0368196b`.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | The changed allowed_links adds connection -> trust_boundary, but the existing TC-104 test still requires every target other than carries to be a declared role | tests/test_systems_kinds.py:262 |
| FND-002 | high | New crossing tests duplicate the validation, relation-report, and diagnostic-line helpers already present in test_data_flow_edges.py | tests/test_trust_crossings.py:26-49 |

## Evidence

The `connection` object type SHALL admit `carries: [data_classification]` and `crosses: [trust_boundary]` in `allowed_links`, beside `connects` and `realizes_requirement`; [FR-013](./FR-013-connection-carries-data-classification.md) and [FR-014](./FR-014-connection-crosses-trust-boundary.md) specify the edges. Both are relationships and not record keys, so `fields` stays forbidden and `Connection.json` is unchanged.

Observed finding: The changed allowed_links adds connection -> trust_boundary, but the existing TC-104 test still requires every target other than carries to be a declared role. Running that test fails at tests/test_systems_kinds.py:262 with AssertionError (connection, trust_boundary). Update the assertion to admit the declared trust_boundary object kind for crosses and include crosses in the verb contract. This is a high finding because the changed FR-007-AC-5 evidence fails. In addition, the new test module duplicates _validate, _relations, and _lines from tests/test_data_flow_edges.py; the repeated helpers can drift and should be shared/generalized.

## Examined Units

- `FR-007-AC-5` (examined): “The declared systems edge verbs and three roles are present, interface carries systems-interface, and the systems kinds allowed_links use those verbs plus realizes_requirement; connection additionally admits carries and crosses. The verbs take declared roles or *, and realizes_requirement takes only FR and NFR.”
- `tests/test_trust_crossings.py` (examined): “The new crossing test module defines _validate, _relations, and _lines helpers.”
- `tests/test_data_flow_edges.py` (context_only): “Existing data-flow test module already defines _validate, _relations, and _lines helpers.”
