---
id: SR-030
title: "EARS conformance - PLAT-1439 FR-013 connection carries data_classification (PR #49)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md, spec/functional/FR-007-systems-model-kinds.md"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
---
# SR-030: EARS conformance - FR-013 (PR #49)

## Summary

Ticket: PLAT-1439. Examined the FR-013 Description statement, its 14 Behavior
statements, and the added FR-007 Behavior line. `quire validate` raises no
EARS warning on FR-013. The one FR-007 warning (`ears:non-singular`, line 91)
is on an unchanged line.

Clean: each Behavior bullet has one `SHALL` or `SHALL NOT`, an active subject
and a checkable response. The prohibitions ("SHALL NOT redeclare", "SHALL NOT
derive", "SHALL issue no denial") are stated as ubiquitous constraints. The
FR-007 line has one obligation, and its rationale is outside the `SHALL`
clause.

## Verdict

**CONDITIONAL.** The main obligation is stated as mandatory, but the
requirement makes it opt-in. Two Behavior statements name the engine, not
this module, as their subject.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | The Description's normative statement "A `connection` SHALL state, through `carries` edges, the data classifications whose data flows on it" makes every connection without `carries` non-conformant. The same FR makes the completeness check opt-in, `off` by default (AC-4), so an unclassified connection is allowed. The ticket's draft read "SHALL be able to state". Fix: state the capability ("The module SHALL let a `connection` state ...") and leave the mandatory form to a project that turns the check on. | FR-013 Description; FR-013-AC-4 | wrong-requirement |
| FND-002 | low | Two Behavior statements have `Quire` as their subject ("Quire SHALL reject ...", "Quire SHALL report ... `dangling-reference`"). This module cannot oblige the engine, and the statements describe existing quire-rs FR-040 and FR-026 behaviour. Fix: write them as module outcomes, for example "A `carries` edge from a connection to a non-`data_classification` SHALL yield `disallowed-edge-target`", and cite FR-040 and FR-026. | FR-013 Behavior; FR-013-AC-2 | wrong-requirement |
