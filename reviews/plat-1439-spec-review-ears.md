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

## Dispositions

| FND | Outcome | Reason |
|---|---|---|
| FND-001 | fixed | The Description now states the capability ("The module SHALL let a `connection` state ...") and says stating classifications is optional. |
| FND-002 | fixed | Both statements now have the edge as subject ("A `carries` edge ... SHALL yield ...") and cite quire-rs FR-040 and FR-026. |

## Round 2 (a61972d)

I re-checked the two Behavior lines a61972d changes. The cross-repository line is deleted. The security-module line no longer contains a `SHALL`. It is a statement of scope for the `off`-key bullet before it, and it adds no obligation. So it needs no EARS pattern. Every remaining Behavior bullet that has a `SHALL` still has one obligation and an active subject. The FND-001 and FND-002 fixes are unchanged.

No new findings. **Round-2 verdict: PASS.**

## Round 3 (f5970b9)

The rewritten dangling bullet has two sentences, each with one obligation. The first is a ubiquitous
`SHALL`, and the `carries` edge is its subject (the FND-002 fix stands). The second is an unwanted-behaviour
`SHALL NOT` with a trailing `when` condition (the source member declares its identity). Its subject is the
`ix://` target of the same `carries` edge. A trailing condition is acceptable EARS form here, and the
condition can be tested. Neither sentence makes a ticket or an owner the subject.

No new findings. **Round-3 verdict: PASS.**
