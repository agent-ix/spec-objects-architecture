---
id: SR-019
title: "Spec review (base) - PLAT-1526 FR-012 software safety class on part (PR #45)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-012-software-safety-class-assignment.md, spec/functional/index.md"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-012", type: references}
---
# SR-019: Spec review (base) - FR-012 (PR #45)

## Summary

Ticket: PLAT-1526. Base checklist over `git diff origin/main...HEAD` at f7ce53f:
the new FR-012 (Description, AC-1..AC-12, CON-1, CON-2, Dependencies) and its
index line. No AssuranceProfile exists in the repo; review set is subset
(base + dependency + ears-conformance, SR-020 and SR-021).

Clean on this pass:

- The class is assigned by a named person with a rationale and is never derived
  or defaulted: Description "No derivation, no default", AC-1 (no `default`, not
  required), AC-8, AC-10, CON-2.
- A missing assigner or rationale fails validation and is not downgraded to
  unassigned (AC-5, AC-6).
- No standard is named or quoted; CON-1 forbids it. No compatibility layer.
- The record-sections form (`## Safety Class` -> `safetyClass`, one-row table,
  `Assigned By` -> `assignedBy`) follows FR-008 and quire-rs FR-081; `max_rows`
  exists in the extract DSL, so "exactly one data row" is expressible.
- `quire validate` passes on both files (quire 0.44.0, engine 0.59.1).

## Verdict

**FAIL.** One high, one medium, four low here; the cross-repo edge and
load-order defects are in SR-020. AC-11 asks for an output no engine
requirement produces, and the part-side class is not held to the iso
vocabulary.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | FR-012-AC-11 requires the part record to reach `quire trace` output with `safetyClass.class`, but `quire trace` is a claims/citations lookup over the trace index (`quire trace --help`) and emits no declaration records. quire-rs FR-090 `carried_fields` reads only top-level frontmatter keys of requirement documents, so nothing carries a body record key anywhere. The AC cannot be passed by module data and no engine FR owns it; quoin FR-161 reads the item class "from the Quire payload" and inherits the gap. Fix: name the engine output that carries part records (and add that to quire-rs), or drop AC-11. | FR-012-AC-11; quire-rs FR-090; quoin FR-161 | missing-requirement |
| FND-002 | medium | The part-side class is not constrained to the iso vocabulary. AC-1/AC-9 make `class` a free `minLength: 1` string, so a part stating `class-9` or `Class-1` passes `quire validate`, while iso FR-009-AC-5/AC-6 reject the same values on requirements. quire-rs FR-091 reports an out-of-enum value only as an advisory finding, and FR-012 has no AC for it. Fix: add an AC that an out-of-vocabulary or wrong-case part class yields the FR-091 `trace:undeclared-field-value` finding, or state how it is otherwise rejected. | FR-012-AC-9, FR-012-AC-1; spec-artifacts-iso FR-009-AC-5/AC-6 | missing-requirement |
| FND-003 | low | FR-012-AC-12 is compound (two manifest declarations plus three fixture corpora) and does not pin the entry `name`s, `check` tokens or the severity mechanism; it defers to "the findings ... FR-091 states". "whose severity defaults to `off`" does not name the module `grammar_severity` key (quire-rs FR-057) that sets it. Fix: split the AC and state the tokens and the `grammar_severity` entry. | FR-012-AC-12 | wrong-requirement |
| FND-004 | low | FR-012-AC-1 and AC-9 name the generated `Part.json`; the source is `model Part` in `typespec/main.tsp:451` (FR-002), and a hand edit of the JSON fails `make schemas-check`. Fix: name the TypeSpec model and the projected schema, as iso FR-009-AC-3 does. | FR-012-AC-1, FR-012-AC-9 | wrong-requirement |
| FND-005 | low | No AC covers an empty `Class` cell; AC-5 and AC-6 cover `Rationale` and `Assigned By` only, so the third required cell is asserted only by the schema text of AC-1. Fix: extend AC-5/AC-6 to the `Class` cell. | FR-012-AC-5, FR-012-AC-6 | correct-requirement-no-evidence |
| FND-006 | low | `spec/spec.md:140-152` lists each FR by number in prose and is not updated for FR-012. Separately, `spec/tests.md` (TM-001) on main is a hand-kept test matrix with per-row status ticks, which is file-tracking ceremony (coverage is computed by `quire matrix`); this PR rightly adds nothing to it, but it should be deleted rather than extended. | spec/spec.md:149; spec/tests.md | wrong-requirement |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-007 | high | The fix for FND-002 copies the class vocabulary. `model Part` declares `softwareSafetyClass` as "the same string-literal union in the same order" as spec-artifacts-iso, and FR-012-AC-9 pins the two lists equal with a parity test that reads the installed iso schema. That is a second copy of module data plus a pin test, which is the vendoring/pin antipattern. It also contradicts the redesign's own "declared once, in the ISO module" and the original FR-012 "holds no copy of the list". Fix: remove the union and AC-9. Validate the part's value without a copy, by importing a named iso type or through an engine vocabulary check (see the round-1 note on `carried_vocabulary`). | FR-012-AC-9, FR-012-AC-10, FR-012 Description "One mechanism: frontmatter" | wrong-requirement |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (849d139). The `quire trace` AC is gone. The class is now a top-level frontmatter key, carried by quire-rs FR-090 `carried_fields` (`from: [part]`, FR-012-AC-12). The new SR-020 FND-005 covers whether the carried value reaches any output. |
| FND-002 | still-open | Round 1 (849d139) makes `class-9` and `Class-1` fail against `Part.json` (AC-10), but only by copying the iso list into `model Part` (new FND-007), and that copy has to be removed. Under the coordinator's no-copy direction, Part.json has no enum and the part frontmatter is the open `ObjectFrontmatter`, so `class-9` on a part passes `quire validate` again. quire-rs#669 FR-091 reports an out-of-enum value only for documents in a compared pair, and `carried_vocabulary` is a report output, not a validator. |
| FND-003 | fixed | Round 1 (849d139). The work is split into AC-12, AC-13 and AC-14. They name the entries `requirement-class-below-allocated-part`/`class-below-part` and `part-needs-class`/`unassigned-class`, and the `grammar_severity` key `trace:unassigned-class: off`. |
| FND-004 | fixed | Round 1 (849d139). AC-1 names `model Part` in `typespec/main.tsp` and requires `make schemas-check` to pass. |
| FND-005 | fixed | Round 1 (849d139). AC-7 covers an empty `software_safety_class` string, and an assigner or rationale with no class. |
| FND-006 | deferred | The `spec/spec.md` half is fixed in round 1 (849d139). The `spec/tests.md` hand-kept matrix is on main, this PR does not touch it, and deleting it is a main-wide cleanup routed to the coordinator. This PR correctly adds nothing to it. |
| FND-002 | fixed | Round 3 (6b2c9a0). The class is no longer copied. The manifest `vocabulary` entry `part-class-in-vocabulary` (AC-9) holds every part document to the ISO `carried_vocabulary`, and AC-10 tests `class-9` and `Class-1` whether or not the part is allocated. That matches quire-rs#669 FR-091 `vocabulary` (3572ba8, AC-17). The rejection is advisory, not a validation failure, by the coordinator's no-copy ruling. |
| FND-007 | fixed | Round 3 (6b2c9a0). The union and the parity test are gone. AC-1 declares the three properties as plain strings with no `enum`, and AC-9 requires that no file of the module lists a class value. |
