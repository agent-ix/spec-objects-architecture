---
id: SR-035
title: "Spec review (EARS conformance) - PLAT-1441 FR-013 architecture report selection (PR #50)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md (origin/main...62fe79c, PR #50)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
---
# SR-035: Spec review (EARS conformance) - FR-013 report selection (PR #50)

## Summary

Ticket: PLAT-1441. Checks the four new Behavior statements (lines 80-86) against EARS grammar. Line
80 is a ubiquitous SHALL with the module as subject. Lines 83-86 are SHALL / SHALL NOT statements
about the relation report, which matches the subject style of the existing report lines (94-99).

## Verdict

**CONDITIONAL.** One low finding.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | low | Lines 83, 85 and 86 each open with "With `record_keys` set", but line 80 makes `record_keys` unconditional on both entries, so the precondition is always true and names no state the report can be in. The second sentence of line 80 ("The selection is module-declared: the engine holds no category names ...") is descriptive and has no SHALL. Fix: drop the precondition, or write "Because both entries set `record_keys`, ...". Then either state the second sentence as a SHALL NOT or cite FR-058 for it. | spec/functional/FR-013-connection-carries-data-classification.md:80-86 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-002 | medium | Line 82, rewritten in 5b5bcba, says the report "SHALL contain `regulatedCategories` ... only when a valid FR-084 `record` for that entry contains the selected key". "Only when" states a necessary condition, not an obligation: a report that never emits `regulatedCategories` satisfies it. Line 84 (omit when `record` is omitted or lacks the key) is the same rule restated, so no Behavior SHALL now requires presence, although AC-5 does. Fix: "SHALL contain `regulatedCategories` on a document or linked entry when, and only when, a valid FR-084 `record` for that entry contains the selected key", and keep line 84 as the list of omission cases. | spec/functional/FR-013-connection-carries-data-classification.md:82-85 |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | The "With `record_keys` set" preconditions are gone, and line 80's descriptive sentence is folded into the SHALL as a "so" clause (5b5bcba). |
| FND-002 | fixed | 689267c changes line 82 to "SHALL contain `regulatedCategories` on a document or linked entry if and only if a valid FR-084 `record` for that entry contains the selected key". Presence is now an obligation, and line 84 stays as the list of omission cases. |
