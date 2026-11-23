---
id: SR-049
title: "EARS review — PLAT-1836 FR-012 additions (PR #58)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-012-software-safety-class-assignment.md"
review_set: subset
---
# SR-049: EARS review — PLAT-1836 FR-012 additions (PR #58)

## Summary

Ticket: PLAT-1836. The review examined the new and edited requirement text in
FR-012: the two `field_consistency` bullets, FR-012-AC-16 and FR-012-AC-17.
For context it also read the FR-012 title and the `**SHALL**` statements in
its Description.

Both ACs can be tested and fail on their own. Each names one trigger, one
observable output (`trace:class-below-part` / `trace:class-below-owner` with
named documents and values) and a negative case. The mutations in SR-046
confirmed that both can fail.

## Verdict

**PASS with one low finding.**

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | low | The new obligation is written in the passive voice, with no actor and no SHALL: "A part that states a class lower than the part that owns it is reported". It sits in a declaration bullet, so the FR's `**SHALL**` statements and its title ("A part carries an optional human-assigned software safety class ...") still do not cover the owner comparison or NFR allocation. Add one EARS statement to the Description, for example "When a part states a class lower than the part it is `owned_by`, the module SHALL declare a finding naming both parts and both values". | spec/functional/FR-012-software-safety-class-assignment.md:75-81 | wrong-requirement |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (dcb76e2). FR-012 now has three single-response statements: **SHALL** report `trace:class-below-part` for an `FR` or `NFR` below its allocated part; **SHALL** report `trace:class-below-owner` for a part below its owner, naming both parts and both values; **SHALL NOT** set, raise or default any class. Each statement names the module as the actor and one observable output. |
