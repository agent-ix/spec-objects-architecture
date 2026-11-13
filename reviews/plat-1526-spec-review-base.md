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
