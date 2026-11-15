---
id: SR-029
title: "Dependency analysis - PLAT-1439 FR-013 connection carries data_classification (PR #49)"
type: SpecReview
analysis: dependency
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
---
# SR-029: Dependency analysis - FR-013 (PR #49)

## Summary

Ticket: PLAT-1439. Examined the seven FR-013 `relationships` edges, the
Dependencies section, and the cross-module kinds the new manifest data names.

Clean:

- `implements US-001`, and `depends_on` FR-007, FR-010 and FR-012 (FR-012 is
  the `grammar_severity: off` precedent). All resolve in this repo.
- `spec-objects-security/FR-023` exists on the sibling PR branch
  (spec-objects-security PR #60). It is the regulated-categories requirement
  FR-013 reads.
- quire-rs FR-058 and FR-084 exist and use the same URI form as FR-010.
- Downstream PLAT-1440, PLAT-1441 and PLAT-1533 match the ticket's blocks
  edges. Sibling PLAT-1532 is named.
- Naming `data_classification`, a kind from another module, in
  `allowed_links` has precedent: `api_endpoint` already has
  `requires: [permission, auth_flow]`.

## Verdict

**CONDITIONAL.** Two medium findings. One AC depends on a sibling ticket's
undeclared edge and on engine output that does not exist. The opt-in claim
holds only when the security module is loaded.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | FR-013-AC-6 needs the PLAT-1532 crossing edge, which no loaded module declares yet. It also needs the boundary's `trust_level` to appear in the same report. FR-084 rows carry no target field values (see SR-028 FND-001), and FR-013 declares no relation that would produce a row for the crossing edge. So PLAT-1440 cannot satisfy AC-6, and it is untestable until PLAT-1532 and an engine change land. Fix: move AC-6 to PLAT-1532 (or a later integration criterion), or make it depend on PLAT-1532 in `relationships`, and name the relation that reports the crossing. | FR-013-AC-6; PLAT-1532; quire-rs FR-084 | missing-requirement |
| FND-002 | medium | "So a corpus without data-flow modelling draws no finding" holds only when spec-objects-security is loaded. `check_declaration_is_live` in quire-rs `required_relations.rs` reports `trace:undeclared-relation-vocabulary` when no loaded module declares a `to` kind and no document is one. That check is separate from the `off` key. With the architecture module active, the security module not active, and no `data_classification` document, every run gets that finding. The manifest has `imports: {}`, and FR-013 does not state the dependency on the security module. Fix: state that FR-013 needs spec-objects-security loaded, or add an AC for an architecture-only corpus. | FR-013 Behavior (grammar_severity line); FR-013-AC-4; quire-rs src/corpus/required_relations.rs | missing-requirement |
