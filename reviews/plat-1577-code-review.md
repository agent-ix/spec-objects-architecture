---
id: SR-022
title: "Code review — PLAT-1577 part software safety class (PR #46)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; typespec/main.tsp, spec_objects_architecture/manifest.yaml, spec_objects_architecture/schemas/Part.json, spec_objects_architecture/schemas/PartFrontmatter.json, spec_objects_architecture/skeletons/part.md, tests/conftest.py, tests/test_manifest_semantic.py, tests/test_systems_kinds.py, tests/test_software_safety_class.py"
review_set: subset
---
# SR-022: Code review — PLAT-1577 part software safety class (PR #46)

## Summary

Ticket: PLAT-1577. Scope is `git diff origin/main...HEAD` at fa5bcbd (one
commit, nine files). Python and TypeSpec/JSON schema only, so no Rust or
React lane ran. Checks run: the focused tests (`tests/test_software_safety_class.py`,
`tests/test_manifest_semantic.py`, `tests/test_systems_kinds.py`: 74 passed,
1 xfailed) and `make schemas-check` (41 schemas match). I also probed
`quire validate` 0.44.0 (engine 0.59.1) by hand on part documents with an
empty assigner, no class, and no title.

What I verified as correct:

- `model Part` and `Part.json` declare the three optional keys as plain
  strings with `minLength: 1` and no `enum` or `default`. None of them is in
  `required`. `dependentRequired` makes the class require the other two and
  each of the other two require the class. The seal
  (`unevaluatedProperties: {not: {}}`) is kept.
- `PartFrontmatter.json` is open (`unevaluatedProperties: {}`). It has no
  `$ref` and no `required`, and declares only the three snake_case
  properties, with the same `dependentRequired`.
- `frontmatter_schema_ref` appears only on `part`. The `part` yield_pattern
  has three optional `frontmatter_field` locators.
- The skeleton names the three fields in its contract comment and carries
  none of them. No module file computes, fills in or rewrites a class value
  (FR-012-CON-2). No standard is named or quoted (FR-012-CON-1). The class
  vocabulary appears nowhere in the module.
- The edits to the existing tests are justified. `test_manifest_semantic`
  exempts only `part` from the no-`frontmatter_schema_ref` rule, which
  FR-012-AC-12 requires. `test_systems_kinds` adds exactly the three
  optional record keys for `part` only. `conftest.SUPPORT_MODELS` registers
  `PartFrontmatter` as a support model.

## Verdict

**CONDITIONAL.** The schemas, manifest and skeleton match FR-012 for the
in-scope criteria. One test carries the wrong trace tag and checks almost
nothing, and the `quire validate` diagnostic assertions match on substrings
that would also accept the wrong key.

Diagnostic naming: `quire validate` reports the frontmatter spelling
(`"software_safety_class" is a required property`,
`"" is shorter than 1 character (at software_safety_class_assigned_by)`).
The `Part.json` record schema reports the camelCase record key. The ACs name
the record key. The PR tests both: the record schema test checks camelCase
and the `quire validate` test checks snake_case. Because the two spellings
map one to one, this matches the spec's intent and is not a finding.
FR-012-AC-5 to AC-7 could state the document-level spelling explicitly.
Separately, engine 0.59.1 prints the `dependentRequired` frontmatter error
twice for a part with no class. That is engine behaviour, not this PR.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | `test_fr012_con2_manifest_lists_no_class_value` is tagged `FR-012-CON-1`, but CON-1 is "names no standard / quotes no standard text". The test checks neither. Its name says CON-2, and what it does check is the AC-9 clause "no file of the module lists a class value", which this PR defers. It also checks only for the literal `class-1` in two files, so it cannot fail for any other value or file. The tag inflates the CON-1 matrix row with a test that does not exercise it. CON-1 and CON-2 are Inspection items, so delete the test (or move it to the AC-9 slice with a real assertion) rather than retagging it. | tests/test_software_safety_class.py:233-237 | correct-requirement-no-evidence |
| FND-002 | low | `test_fr012_quire_validate_rejects_incomplete_assignment` asserts `named in result.stderr` with `named = "software_safety_class"` for the no-class and empty-class cases. That substring also matches `software_safety_class_assigned_by` and `software_safety_class_rationale`, so a diagnostic naming the wrong key would still pass. Match the quoted name or the `(at <key>)` location instead, for example `'"software_safety_class" is a required property'` and `'(at software_safety_class)'`. The record-schema test has the same pattern with `softwareSafetyClass`. | tests/test_software_safety_class.py:183-200, tests/test_software_safety_class.py:136-180 | correct-requirement-no-evidence |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (c34ee27). `test_fr012_con2_manifest_lists_no_class_value` and its `FR-012-CON-1` tag are deleted. CON-1 and CON-2 stay Inspection items, and both still hold by inspection. |
| FND-002 | fixed | Round 1 (c34ee27). The record-schema test now matches `f"'{named}'"`. The `quire validate` test matches `f'"{named}"'` or `f"(at {named})"`. The closing quote or parenthesis stops `software_safety_class` / `softwareSafetyClass` from matching the longer keys. Focused run: 19 passed. |
