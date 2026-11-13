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

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-005 | medium | quoin FR-161 now takes its items from an `item_relation`: a relation-report row whose `document` is the part and whose `linked` entries are the requirements allocated to it. It reads the class from that row's `carried` object, and FR-161 says "The module declares the relation". FR-012 declares no such relation, and FR-058 `required_relations` has no `via` hop to express part <- allocated_to <- allocation -> allocates -> FR. quire-rs FR-090 carries values only onto `requirements[]` entries and relation-report row documents. So the `carried_fields from: [part]` entry of AC-12 surfaces nowhere, and AC-12 tests only that the entry is declared. Fix: declare the item relation (with the `via` hop added to FR-058, or as data FR-161 can read), and give AC-12 an observable outcome. | FR-012-AC-12; quoin FR-161; quire-rs FR-090; quire-rs FR-058 | missing-requirement |
| FND-006 | medium | The part frontmatter is the open `ObjectFrontmatter`, which declares no `software_safety_class` property ("no frontmatter schema change is needed"). quire-rs#669 FR-091's merge-time check reports `trace:undeclared-relation-vocabulary` for a `to_field` or `required_fields.field` that is "a property of none of the named archetypes' frontmatter schemas and is carried by none of their documents". Any corpus whose parts are all unassigned, which is the default state, therefore draws that finding for `requirement-class-below-allocated-part` and `part-needs-class`, although AC-14 ships the latter `off`. Fix: declare the three properties in the part frontmatter schema (type only, no value list), or add an AC that a corpus of unassigned parts yields no `undeclared-relation-vocabulary`. | FR-012 Description "One mechanism: frontmatter"; FR-012-AC-13; FR-012-AC-14; quire-rs FR-091 | wrong-requirement |

## New findings (disposition pass 3)

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-007 | medium | FR-012 asks for `PartFrontmatter` "extending the open `ObjectFrontmatter`", referenced by the `part` object type. quire-rs main does accept `frontmatter_schema_ref` on an `object_types` entry: one `Archetype` struct serves every section (`src/loader/manifest.rs:471-473`). But it compiles that schema with plain `compile_schema` (`src/loader/compile.rs:201`), which has no resolver and refuses a remote `$ref` (test `compile_schema_refuses_a_remote_ref`); only `data_schema` goes through the semantic source resolver. A TypeSpec-emitted schema that extends or spreads `ObjectFrontmatter` emits `$ref`s to `ObjectFrontmatter.json` / `ObjectId.json` by `https` `$id`, so the `part` archetype would fail to load and break AC-15. The iso frontmatter schemas are self-contained, with no `$ref`. Fix: make `PartFrontmatter` a self-contained file with no `$ref`, open, declaring only the three string properties, and drop "extending". | FR-012 Description "One mechanism: frontmatter"; FR-012-AC-12; FR-012-AC-15 | wrong-requirement |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (849d139). The entry carries `via: {archetype: allocation, edges: [allocates], direction: incoming}`, then `edges: [allocated_to]` to `part`. That matches the two-hop path in quire-rs#669 FR-091 (5f7b2fd), and AC-13 tests it through an `allocation`. |
| FND-002 | fixed | Round 1 (849d139). quire-rs#669 FR-091 (5f7b2fd) checks archetype and field names against the merged registry and never at single-module load. FR-012 states that this module owns the entry, and AC-15 requires the module to load on its own. |
| FND-003 | fixed | Round 1 (849d139). `field`, `to_field` and `required_fields.field` are all the top-level frontmatter key `software_safety_class`, and quire-rs#669 FR-091 states that no extracted body-record key is read. |
| FND-004 | still-open | #44 (FR-010) has merged to main (c745c8b), and branch 849d139 now has textual merge conflicts with main in `spec/functional/index.md` (the FR-010 and FR-012 lines) and `spec/spec.md:147-152` (the FR-010 and FR-012 sentences). The branch needs a rebase on main. The Description still says "whichever pull request lands second"; once rebased it should cite the merged FR-010. Main's manifest has no `traceability` block yet, so that part is not a conflict. |
| FND-004 | fixed | Round 3 (6b2c9a0, merge 042b57c). The branch merged origin/main (c745c8b). `index.md` and `spec.md` carry FR-010 and FR-012, `git merge-tree` shows no conflict, and GitHub reports MERGEABLE. FR-012 now cites the merged FR-010 as the owner of the `traceability` block and `depends_on` it. |
| FND-005 | fixed | Round 3 (6b2c9a0). The part-side `carried_fields` entry is gone, and quoin FR-161 (1a57940b) now reports per requirement and reads no part class or allocation. FR-012 states that the part class feeds only `field_consistency`, so no item relation is needed. |
| FND-006 | fixed | Round 3 (6b2c9a0). `PartFrontmatter` declares the three properties as plain strings, and AC-12 requires that an all-unassigned corpus with ISO loaded yields no `trace:undeclared-relation-vocabulary` for any of the three entries. The new FND-007 covers how that schema must be written to load. |
