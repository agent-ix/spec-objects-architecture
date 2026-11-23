---
id: SR-048
title: "Spec integrity review — PLAT-1836 FR-012 AC-16 and AC-17 (PR #58)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-012-software-safety-class-assignment.md"
review_set: subset
---
# SR-048: Spec integrity review — PLAT-1836 FR-012 AC-16 and AC-17 (PR #58)

## Summary

Ticket: PLAT-1836. Examined:

- the FR-012 tracking line;
- the edited `requirement-class-below-allocated-part` bullet;
- the new `part-class-below-owner` bullet;
- FR-012-AC-16 and FR-012-AC-17.

Context only:

- FR-007 (part `owner` member, `owned_by` verb);
- the `part` skeleton;
- quire-rs FR-091;
- spec-artifacts-iso FR-009 (the NFR frontmatter schema on `origin/main`
  declares the three class fields).

`quire validate --scope .` on FR-012 exits 0. The new text is consistent
with FR-091:

- the direction is right;
- the rank comes from the ISO `enum`;
- no value is assigned.

## Verdict

**CONDITIONAL.** There is one medium consistency gap, between the `owned_by`
edge and the part's `owner` member, and two low findings.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | Ownership is stated through two channels, and the new check reads only one of them. FR-007 requires each part to state its `owner` as a `## Part` table member. The `part` skeleton writes the owner only there (`Owner: search_service`) and has no `owned_by` edge. `part-class-below-owner` follows the frontmatter `owned_by` edge alone. A corpus authored from the skeleton therefore never triggers the check, and nothing says that the edge and the member must agree. FR-012 should say that the comparison follows the `owned_by` edge, not the `owner` member. It should also say whether a part must author `owned_by` to its owning part for the check to apply, or point the skeleton and FR-007 at that edge. | spec/functional/FR-012-software-safety-class-assignment.md:75-81; spec_objects_architecture/skeletons/part.md | missing-requirement |
| FND-002 | low | FR-012-AC-17 omits "with the ISO module loaded", although AC-16 states it. The entry's `order_from` (FR `software_safety_class` enum) exists only when the ISO module is loaded; without it, FR-091 reports `trace:undeclared-relation-vocabulary` and compares nothing. As written, AC-17 can be read as holding without the ISO module. | spec/functional/FR-012-software-safety-class-assignment.md:110 | wrong-requirement |
| FND-003 | low | The PR extends the body line "Tracked by Linear PLAT-1526 (...) and PLAT-1836 (...)". That line is provenance bookkeeping in the spec body; the ticket link belongs in the tracker and in git history. Adding to it grows a ceremony line rather than stating a requirement. Drop the addition (and preferably the line). | spec/functional/FR-012-software-safety-class-assignment.md:25 | wrong-requirement |
