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

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-002 | low | Fix commit 5b5bcba dropped AC-5's unconditional "contains no `level` value" clause. The no-`level` assertion now sits inside "Where the classification's valid record has `regulatedCategories`", so AC-5 no longer checks `level` absence for a classification without categories, although Behavior line 86 forbids it at any depth unconditionally; AC-9 checks only `regulatedCategories` absence there. The first sentence also lost its "and" ("lists ..., lists ..., lists per classification ..."). Fix: make the no-key clause its own sentence covering every entry in both views, and restore "and". | spec/functional/FR-013-connection-carries-data-classification.md:130 |

## New findings (disposition pass 2)

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-003 | medium | The committed review records in this PR are coder-written paraphrases, not the reviewer's SR files. `reviews/plat-1441-spec-review-ears.md` records SR-035 FND-002 as "the first AC's clauses need a complete unconditional no-unselected-record-key assertion". That is SR-031 FND-002's defect. The posted SR-035 FND-002 is the "SHALL contain ... only when" necessary-condition finding, and the file has no `## New findings` row for it. `reviews/plat-1441-code-review.md` cuts SR-031 FND-002 down to the missing "and" and drops the unconditional no-`level` part. `reviews/plat-1441-gap-analysis.md` adds a "Pass-1 verdict: approved" line the reviewer never wrote. The repo record therefore disagrees with the Linear record. Fix: copy the reviewer's round-2 scratchpad SR files over `reviews/plat-1441-{code-review,gap-analysis,spec-review-base,spec-review-ears}.md` verbatim. | reviews/plat-1441-spec-review-ears.md:29-34; reviews/plat-1441-code-review.md:41-52; reviews/plat-1441-gap-analysis.md:40-47 |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | AC-5 now reads "no record key outside `record_keys`, including `level`, appears at any depth in either" (5b5bcba). |
| FND-002 | fixed | 689267c restores "and" before "lists per classification", and makes the no-key clause its own unconditional sentence: "Whether or not `regulatedCategories` is present, no record key outside `record_keys`, including `level`, appears at any depth in either view." |
| FND-003 | still-open | New this round. No fix round has run for it. Copy the reviewer's scratchpad SR files over the committed `reviews/plat-1441-*.md` files. |
