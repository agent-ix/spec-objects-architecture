---
id: SR-031
title: "Code review - PLAT-1441 FR-013 architecture report selection (PR #50)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md (origin/main...62fe79c, PR #50)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
---
# SR-031: Code review - FR-013 report selection (PR #50)

## Summary

Ticket: PLAT-1441. The diff is Markdown only: one file, FR-013, +13/-4. No Python, Rust or
TypeScript changed, so `rust-review` and `review-react` do not apply. The code-review lens here
asks whether each changed acceptance criterion is a claim a test can fail, and whether it agrees
with the generic `record_keys` semantics in quire-rs PR #688 (OPEN, head of
`plat-1441-quire-rs-spec`: FR-058 "Selecting record keys to carry", FR-084 "Carried record
values and the reverse view", FR-084-AC-20..29).

Examined: FR-013-AC-5 and FR-013-AC-8 (changed), the two new Outputs bullets, and the four new
Behavior lines. AC-7 (queue unchanged) was read as context; the diff does not touch it.

## Verdict

**CONDITIONAL.** AC-8 is concrete and falsifiable: it pins `record_keys` to exactly
`[regulatedCategories]` on both entries, and FR-058-AC-36 accepts a key that only one endpoint
archetype declares, so the forward entry (`from: connection`) loads. AC-5's new sentence matches
FR-084: the forward view carries the classification's `record` on its `linked` entry and the
reverse view carries it on the obliged `document`. One low wording finding. `quire validate` was
not run in this session (the permission layer required approval); the lead reports exit 0 on this
file.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | low | FR-013-AC-5 says "no `level` or other unselected key appears in either" view, but the report rows hold many keys that are not record keys (`id`, `path`, `verification`, ...), so a literal test cannot pass. The first sentence says "no `level` value", which reads as the value, not the key. FR-084-AC-22/23 say "no `level` key at any depth". Fix: "no record key outside `record_keys` (in particular no `level` key) appears in either view, at any depth". | spec/functional/FR-013-connection-carries-data-classification.md:130 |
