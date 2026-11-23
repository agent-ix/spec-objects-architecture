---
id: SR-047
title: "Gap analysis — PLAT-1836 class-below-part on NFR and part-class-below-owner (PR #58)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-012-software-safety-class-assignment.md, spec_objects_architecture/manifest.yaml, tests/test_software_safety_class_checks.py, tests/fixtures/class_inheritance/"
review_set: subset
---
# SR-047: Gap analysis — PLAT-1836 class-below-part on NFR and part-class-below-owner (PR #58)

## Summary

Ticket: PLAT-1836, part 1. The ticket text was treated as data. Two of its
items are in this PR: "part-class inheritance over owned_by" and "extend
class-below-part to NFR". Its standing instruction is that the tool never
assigns classes; people decide. Plan completion was not assessed.

`quire matrix --scope .` shows both new criteria tagged:

- FR-012-AC-16 → `tests/test_software_safety_class_checks.py:141`. The
  binding is correct. The test asserts the manifest entry, then asserts that
  NFR-001 (`class-1` → `class-2`) gives exactly one `class-below-part`
  finding naming the NFR, the allocation, the part and both values, and that
  NFR-002 gives none.
- FR-012-AC-17 → `tests/test_software_safety_class_checks.py:154`. The
  binding is correct. The test asserts one `class-below-owner` finding for
  `child_low`, and none for `child_same` or `child_none`.

Both tests failed under the behavioural mutations: reverting the NFR
extension, flipping the direction, and swapping the classes (SR-046). The
code that realizes the criteria is `manifest.yaml:115-135`. No module code
is orphaned or stubbed.

Report-only does meet the ticket's intent. "Inheritance" that assigns or
raises a class would break the standing rule that the tool never assigns
classes, and FR-091 "Reports, never assigns" forbids it in the engine as
well. The finding below concerns the case that inheritance exists to govern.

## Verdict

**CONDITIONAL.** AC-16 and AC-17 are met and their tests can fail. One medium
gap remains: the unclassed child is not covered, and no spec note says how
the ticket's "inheritance" wording was resolved.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | Inheritance matters most for a child part that states **no** class under a classed owner. Here that part draws nothing by default: FR-091 skips any pair with a missing side, and `trace:unassigned-class` ships `off`. FR-012 says that the child "inherits nothing", but it does not say how a project catches this case. The route is to enable `trace:unassigned-class` (`part-needs-class`), since `field_consistency` cannot compare a missing value and a `where` selector cannot see the owner's class. FR-012 also does not record that the ticket's "part-class inheritance" was deliberately built as report-only. Add a short spec note on both points, and add a criterion (or extend AC-17) stating that with `trace:unassigned-class` enabled, `child_none` yields `trace:unassigned-class`. | spec/functional/FR-012-software-safety-class-assignment.md:74-81, 110 | missing-requirement |
