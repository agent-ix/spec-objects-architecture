---
id: SR-050
title: "EARS review — PLAT-1855 FR-016 and FR-010 statements (PR #59)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-016-segregation-design-relation.md, spec/functional/FR-010-design-realization-edge.md"
review_set: subset
---
# SR-050: EARS review — PLAT-1855 FR-016 and FR-010 statements (PR #59)

## Summary

Ticket: PLAT-1855. Examined every SHALL in FR-016 Behavior and Constraints (12 Behavior bullets, CON-1,
CON-2), the SHALL in the FR-016 Scope paragraph, FR-016-AC-1 to AC-10, the edited FR-010 Behavior bullet
("first two entries of `traceability.design_relations`") and FR-010-AC-3. Context only: FR-010's other
Behavior bullets, quire-rs FR-058 and FR-086.

Each Behavior bullet carries one SHALL with one subject and one observable outcome; the module-declaration
bullets are ubiquitous-form and testable by manifest inspection; the report bullets are event/state form
with a single trigger. The two SHALL NOT bullets on class/score are singular and testable (AC-9). All ten
ACs name a fixture condition and an observable output, and each can fail. AC-10 is a Demonstration over
quoin, which is the right method for a cross-tool reading. No scores, classes or acceptability are
assigned by the tool.

## Verdict

**PASS with two low findings.**

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | low | Three Behavior bullets make "Quire" the subject ("Quire SHALL report ..."), placing an obligation on another system in this module's requirement. FR-010 states the same behaviour with the module's own artifact as subject ("each relation SHALL report"). Rephrase to "Each relation SHALL report ..." so the responsible system is this module's declaration. | spec/functional/FR-016-segregation-design-relation.md:85-87 | wrong-requirement |
| FND-002 | low | The Scope paragraph carries a normative SHALL ("The relations SHALL NOT be declared without the scope") in Description prose, outside Behavior and Constraints, where it is neither numbered nor bound to a criterion. Move it to Constraints (Inspection) or drop it, since the Behavior bullet already fixes `when_any`. | spec/functional/FR-016-segregation-design-relation.md:56-57 | wrong-requirement |
