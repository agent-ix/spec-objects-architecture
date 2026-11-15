---
id: SR-026
title: "Code review - PLAT-1439 connection carries data_classification (PR #49)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md, spec/functional/FR-007-systems-model-kinds.md, spec/functional/index.md, tests/test_systems_kinds.py"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
---
# SR-026: Code review - PLAT-1439 (PR #49)

## Summary

Ticket: PLAT-1439. Scope is `git diff origin/main...HEAD`: three Markdown spec
files (new FR-013, one Behavior line and AC-5 of FR-007, one index line). The
PR changes no Python, TypeSpec, manifest, schema, skeleton, fixture or test.
The Golden Path code checklist (test style, mock boundaries, code-test
alignment) therefore has no code unit to examine. Rust review was not run, and
does not apply, because no Rust changed.

Examined as code-adjacent units:

- The index line for FR-013 matches the file name and title.
- FR-013 frontmatter `relationships` use the same `ix://` forms as FR-010 and
  FR-012, and the cross-repo target `spec-objects-security/FR-023` exists on
  the sibling PR branch (spec-objects-security PR #60).
- `quire validate --scope .` on the three files (quire 0.45.0, engine 0.60.0)
  reports no error. The one warning (`ears:non-singular` at FR-007 line 91)
  is on a line this PR does not change.
- No build artifact, vendored file, SHA pin or version-tracking record is
  added. No paywalled standard is named or quoted.

Whether the spec's claims about the engine hold is reviewed in SR-028 and
SR-029, not here, so no finding is counted twice.

## Verdict

**PASS.** No code changed, and the changed files are well formed.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | low | No findings (placeholder) | - |

## Round 2 (a61972d)

The round-1 summary says the PR changes no test. That no longer holds: faf78d3 changes
`tests/test_systems_kinds.py` (TC-104), so round 2 reviews that change too.
a61972d changes only FR-013 prose. The scope is now the PR's commits
ae5d129..a61972d over FR-013, FR-007, the index, and `tests/test_systems_kinds.py`.

- The TC-104 change uses the existing `SYSTEMS_TYPES` and `object_type` helpers from
  `tests/conftest.py`. It adds no mock and no fixture. At HEAD it asserts the old verb set
  (the manifest has no `carries`) and that no non-`connection` systems kind declares `carries`.
  Both match the amended FR-007-AC-5 for the code as it stands.
- The suite was not run here: the harness denied `poetry run pytest`. `make test` failed with
  `pytest: error: unrecognized arguments: --cov=...` because the worktree has no installed Poetry
  environment. I reasoned about the test statically.
- No build artifact, vendored file, pin or tracking record is added.

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-002 | low | The new comment ("`carries` is allowed on `connection` only (FR-013)") and the `used_verbs - {"carries"}` subtraction read as if TC-104 already tolerates the PLAT-1440 manifest change. It does not. The target loop above, at lines 258-262, asserts `token == "*" or token in manifest["roles"]` for every verb except `realizes_requirement`. `data_classification` is an object type from spec-objects-security, not a role in this manifest (roles are `systems-part`, `systems-port` and `systems-interface`). So adding `carries: [data_classification]` makes TC-104 fail with `('connection', 'data_classification')`. This does not break anything at HEAD, and it forces PLAT-1440 to revisit TC-104, which suits the deferral in SR-027 FND-001. Fix (in PLAT-1440): exempt `carries` from the role check, and assert `object_type("connection")["allowed_links"]["carries"] == ["data_classification"]`. | tests/test_systems_kinds.py:256-267; FR-007-AC-5; PLAT-1440 |

**Round-2 verdict: PASS.** No defect at HEAD. One low forward-looking note for PLAT-1440.

## Round 3 (f5970b9)

f5970b9 changes only FR-013 prose (the dangling Behavior line). It changes no test, manifest, schema,
skeleton or script. No build artifact, vendored file, pin or tracking record is added. Rust review does
not apply.

| FND | Outcome | Reason |
|---|---|---|
| FND-002 | fixed | The fix lives on the ticket, not in this PR. The PLAT-1440 description, read with `linear issue view`, now tells the implementer three things. It says to positively assert `carries: [data_classification]` on `connection` in TC-104. It says to keep `carries` absent on the other kinds. It says to exempt this one typed link from the role-target rule. Its AC 8 restates this. TC-104 at HEAD (`tests/test_systems_kinds.py:246-267`) is unchanged since round 2 and passes against the current manifest, which has no `carries` on `connection`. |

Not run: `make test` fails before collection with `pytest: error: unrecognized arguments: --cov=...`.
The worktree has no installed Poetry environment, and no test changed in this round.

**Round-3 verdict: PASS.** No new findings. The AC-7 scoping problem is SR-028 FND-007. It is a spec
defect and is not counted here.
