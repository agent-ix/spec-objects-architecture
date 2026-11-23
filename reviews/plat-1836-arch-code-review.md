---
id: SR-046
title: "Code review — PLAT-1836 class-below-part on NFR and part-class-below-owner (PR #58)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; spec_objects_architecture/manifest.yaml, tests/test_software_safety_class_checks.py, tests/fixtures/class_inheritance/"
review_set: subset
---
# SR-046: Code review — PLAT-1836 class-below-part on NFR and part-class-below-owner (PR #58)

## Summary

Ticket: PLAT-1836. PR head 462927b, scoped to `git diff origin/main...HEAD`.
The PR changes module data only. `requirement-class-below-allocated-part` now
reads `from: [FR, NFR]`. A new `field_consistency` entry,
`part-class-below-owner`, follows `owned_by` outgoing from a part to a part
and uses `rule: not_below` and `check: class-below-owner`. There are two new
tests (AC-16 and AC-17) and a new fixture corpus, `class_inheritance`.

Engine facts, checked against quire-rs `origin/main` FR-091 and the installed
quire 0.52.0 (engine 0.62.2):

- `check` is a name the module chooses. The engine has no built-in
  `class-below-owner` kind; it reports `trace:<check>` (FR-091-CON-1: "the
  engine holds no ... verb, rank or value").
- `direction: outgoing` over `owned_by` makes the child (the part that
  authors `owned_by`) the `from` side and the owner the target. `not_below`
  reports when the child ranks lower, which is the intended direction.
- The rank comes from the ISO module's `enum` through `order_from`. The
  module holds no class list and no order.

The tests were run with the project's poetry venv, `-o addopts=""`, and a
modules directory holding spec-artifacts-iso `origin/main` (9342304) plus the
installed process, security and business modules. Results:

- PR: `test_software_safety_class_checks.py` 9 passed.
  `test_software_safety_class.py` 28 passed together with the checks file,
  using `npm ci` semantic-core in a scratch copy.
  `test_manifest.py`, `test_manifest_semantic.py` and `test_design_edges.py`
  gave 48 passed and 1 xfailed, the same as `origin/main`.
- With the stale installed iso module, AC-10, AC-12 and AC-13 fail on
  pristine `origin/main` too, so that failure is environmental and not
  caused by this PR.

The engine output names both documents and both values, for example
`'child_low' states software_safety_class 'class-1', below
software_safety_class 'class-2' stated by 'owner_high'`.

Mutations, with the manifest-shape asserts removed so that only behaviour is
judged:

- Reverting to `from: FR` fails AC-16.
- Flipping `direction` to `incoming` fails AC-17.
- Swapping the owner and child classes fails AC-17.

With the shape asserts kept, each mutation fails earlier, at the manifest
assert.

Checked and clean:

- No class value appears in module files.
- No compatibility layer was added.
- Nothing counts or pins files.
- No standard is named and no paywalled text is quoted.

## Verdict

**PASS with one low finding.** The manifest entries are correct for the
engine semantics, and the tests can fail.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | low | Every `class_inheritance` part fixture states `Owner: search_service` in its `## Part` table, while its `owned_by` edge names `owner_high`. So the fixture records two different owners for the same part. The check reads only the edge, so the test passes, but the fixture shows a contradictory model as if it were valid. Make each child's Owner cell agree with its edge (or state in the fixture that the edge, not the Owner member, is what the check reads; see SR-048 FND-001). | tests/fixtures/class_inheritance/spec/design/child_low.md:15-19, child_same.md:15-19, child_none.md:13-17 | implementation-bug-despite-evidence |
