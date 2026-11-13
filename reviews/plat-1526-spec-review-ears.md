---
id: SR-021
title: "EARS conformance - PLAT-1526 FR-012 software safety class on part (PR #45)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-012-software-safety-class-assignment.md"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-012", type: references}
---
# SR-021: EARS conformance - FR-012 (PR #45)

## Summary

Ticket: PLAT-1526. Examined the requirement statements of FR-012: the
Description's "The module SHALL let a person record, on that part, the software
safety class they assign to it, who assigned it, and why", "The module SHALL NOT
supply a default class", and the two constraints CON-1 and CON-2. Each is a
ubiquitous EARS statement with one subject and one response; the unwanted-
behaviour cases (empty rationale, empty assigner, extra row) are stated as
acceptance criteria with observable outcomes. No finding.

## Verdict

**PASS.** No EARS defect.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | low | No findings (placeholder) | - |
