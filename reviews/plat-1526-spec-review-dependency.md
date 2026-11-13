---
id: SR-020
title: "Dependency analysis - PLAT-1526 FR-012 software safety class on part (PR #45)"
type: SpecReview
analysis: dependency
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-012-software-safety-class-assignment.md, spec/functional/index.md"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-012", type: references}
---
# SR-020: Dependency analysis - FR-012 (PR #45)

## Summary

Ticket: PLAT-1526. Examined FR-012's frontmatter edges, Dependencies section
and the cross-repo contract of AC-9 and AC-12 against: this repo's
`manifest.yaml` on main (80b60cb), spec-artifacts-iso main manifest and PR #73
FR-009, quire-rs PR #669 FR-090/FR-091 and the loader/corpus sources on its
branch, quoin FR-161, and the concurrent PLAT-1417 PR #44 (FR-010).

Rulings on the sibling reviewer's points:

- One-hop model cannot express allocation: **confirmed**. On main
  `allocated_to` is admitted only on `allocation` (`manifest.yaml:495-498`,
  target `systems-part`), and iso `FR` `allowed_links` has no `allocated_to`.
  The modelled path is FR <-allocates- allocation -allocated_to-> part (two
  hops).
- AC-12 names `FR`, the iso archetype, which load validation cannot see:
  **confirmed** under FR-091-AC-10 as written (and FR-090-AC-7's precedent
  "an archetype the module does not declare"). FR-058 `required_relations` does
  not check archetype names at load, which is why FR-010 can name `FR`/`ADR`.
- `safetyClass.class` is a body-record key, not frontmatter: **confirmed**.
  FR-081 puts it under the extracted `record`; the corpus trace checks on the
  quire-rs branch read frontmatter only (`required_relations.rs:156-204`,
  `vocabulary_coverage.rs:195`).

## Verdict

**FAIL.** Two high, one medium, one low. AC-12 rests on an edge the model does
not have and on a module-load rule that rejects the entry's names.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | FR-012-AC-12 compares a requirement's class with "the part reached over its allocation edge", but no one-hop FR->part allocation edge exists: `allocated_to` is admitted only on `allocation` documents and iso `FR` does not admit it, so the real path is FR <- allocates <- allocation -> allocated_to -> part. quire-rs FR-091 `field_consistency` follows one hop, so the entry matches no modelled allocation and stays silent. PR #44's FR-010 adds a one-hop `realizes_requirement` (part -> FR) that `direction: incoming` could follow, but "realizes" is not "allocated to". Fix: either base AC-12 on `realizes_requirement` and say so, or require a two-hop path in quire-rs FR-091 through `allocation`. | FR-012-AC-12; manifest.yaml:495-498; quire-rs FR-091; spec-objects-architecture FR-010 | wrong-requirement |
| FND-002 | high | The AC-12 `field_consistency` entry would live in this module's manifest but names `FR` and `software_safety_class`, both declared by spec-artifacts-iso. quire-rs FR-091-AC-10 fails the module load for an undeclared archetype or a property absent from its schema (FR-090-AC-7: "an archetype the module does not declare"), so the module either fails to load on its own or silently needs iso co-loaded. FR-012 states neither which module owns the entry nor how cross-module names resolve. Fix: state the owning module and require quire-rs FR-091-AC-10 to check against the merged model of the co-loaded modules (the loader already merges, `loader/mod.rs:1359`). | FR-012-AC-12; quire-rs FR-091-AC-10; quire-rs FR-090-AC-7 | wrong-requirement |
| FND-003 | medium | AC-12's `required_fields` entry on `part` names `safetyClass.class`, a key path into the extracted body `record` (quire-rs FR-081), not frontmatter. FR-091 says `to_field` is a record key path but leaves `required_fields.field` unqualified, and its load check ("a property absent from its schema") and the existing corpus checks read frontmatter schemas only; the `part` frontmatter schema has no such property. Fix: have FR-091 state that `required_fields.field` (like `to_field`) may be a record key path checked against `data_schema`, and cite that in AC-12. | FR-012-AC-12; quire-rs FR-091; quire-rs FR-081 | missing-requirement |
| FND-004 | low | Collision with PR #44 (FR-010): both insert a line after the FR-009 entry in `spec/functional/index.md`, a textual merge conflict for whichever lands second. Both also specify the not-yet-existing manifest `traceability` block (FR-010: `required_relations`, `design_relations`; FR-012: `field_consistency`, `required_fields`) with no cross-reference, so the two implementing tickets will each create it. Fix: rebase the second PR onto the first and note in one FR that the block is shared. | spec/functional/index.md:19; FR-012-AC-12; FR-010 Outputs | wrong-requirement |
