---
id: SR-016
title: "Code review r3 — FR-008 record-key sections at e164b70 (PR #41)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; PR #41 diff origin/main...e164b70: package.json, package-lock.json, pyproject.toml, poetry.lock, spec_objects_architecture/manifest.yaml, spec_objects_architecture/schemas/, spec_objects_architecture/skeletons/, typespec/main.tsp, tests/"
review_set: subset
---
# SR-016: Code review r3 — FR-008 record-key sections at e164b70 (PR #41)

## Summary

Ticket: PLAT-196 (also PLAT-201). This is the third review round, over the
whole `git diff origin/main...e164b70` after the rebase onto #42. It covers the
semantic-core 0.4.1 bump, the regenerated schemas, the quire `^0.55.0` dev
dependency and its lock, the engine-drift test changes (TC-091, TC-111,
TC-019), the SR-014 FND-003 test change (TC-130), and the fixture updates for
the `{kind, value}` `TypeRef` target.

The gate was not re-run, as the brief asked. The coder reports `make lint` passing
and `make test` at 277 passed, 7 skipped, 1 xfailed, 0 failed, 100% coverage at
e164b70.

## Verdict

**MERGEABLE after one low fix.** No code defect blocks merge.

Verified clean:

- **Dependency bump.** `package.json` and `package-lock.json` change only
  `@agent-ix/semantic-core` 0.3.3 to 0.4.1. The lock entry now resolves from
  `registry.npmjs.org`, and its integrity matches `npm view
  @agent-ix/semantic-core@0.4.1 dist.integrity` on npmjs. The published 0.4.1
  `TypeRefTarget.json` is the `oneOf` over `{kind: SemanticId|KernelScalar,
  value}`, which is the form the engine emits. This closes the root cause of
  SR-010 FND-001.
- **No leftover private-registry wiring.** The repo has no `.npmrc`, and no
  `npm.pkg.github.com`, `NPM_CONFIG_USERCONFIG` or `NODE_AUTH_TOKEN`.
- **`poetry.lock`.** It changes only the `quire` entry (0.52.0 to 0.55.0 with
  its five wheel hashes), the `content-hash`, and the tool header line (Poetry
  2.3.1 to 2.3.2). This is tool output and nothing beyond what the bump needs.
- **Schemas.** All 21 schema files differ only by the `$ref` base
  `semantic-core/0.3.3/` → `0.4.1/` (55 symmetric lines). The one exception is
  the `LayoutField.json` `description`, which equals the edited `main.tsp` doc
  comment. The generator derives the base from the manifest's
  `semantic.semantic_core`. Nothing looks hand-edited. `make schemas-check` was
  not re-run (no `node_modules` in the worktree).
- **Fixtures.** The `{kind, value}` fixture updates in `test_role_schemas.py`
  and `test_systems_kinds.py` keep their negative meaning. The bare-token case
  (`{kind: SemanticId, value: "Mystery"}`) still fails on the `SemanticId`
  pattern.
- **TC-019.** It asserts that every `resolved` starts with
  `https://registry.npmjs.org/`, with no exception for semantic-core.
- **TC-091.** It drops the strict xfail, so the per-file-index half is now an
  enforced pass.
- **TC-111.** It asserts the engine's new pattern-mismatch message. The spec
  wording is now stale; see SR-017.
- **TC-130.** It adds `external_contract` cut of `## Invariants` and
  `## Operations`, which SR-014 FND-003 asked for. `api_endpoint` cuts
  `## Routes` together with `## Operations`, because a route names an operation
  declared under `## Operations`.
- **Ceremony.** No new pin, digest or version tracker. The manifest
  `semantic_core` value is the semantic-module contract field the engine reads
  (`semanticCore`), not a record.
- **Vendoring.** The semantic-core schemas are referenced through
  `node_modules`, not copied.
- **Reviews.** The earlier review files under `reviews/` are untouched by this
  PR. It only adds and appends to its own `plat-196-*` files.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | low | The TC-130 docstring now ends "`api_endpoint` drops `## Routes` with `## Operations` ...; its schema half is TC-037". TC-037 is the `external_contract` schema test (FR-004-AC-8), not the `api_endpoint` one. The sentence was moved when `external_contract` joined the parametrisation, and it now names the wrong subject. Move "its schema half is TC-037" back to the `external_contract` sentence. | tests/test_role_schemas.py:568-577 | implementation-bug-despite-evidence |

## Gates Run

- None re-run, per the brief. Inspection only: `git diff origin/main...HEAD`,
  `npm view`/`npm pack` of `@agent-ix/semantic-core@0.4.1` from npmjs.

## Language Dispatch

Python, JSON and Markdown only. No Rust, no React lane.
