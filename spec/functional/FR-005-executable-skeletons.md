---
id: FR-005
title: "Make every skeleton an executable typed fixture"
type: FR
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-objects-architecture/FR-003"
    type: "depends_on"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-071"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-072"
    type: "depends_on"
---
# FR-005: Make every skeleton an executable typed fixture

## Description

Every skeleton under `spec_objects_architecture/skeletons/` SHALL author its
declarations in the quoin FR-071/FR-072 Markdown forms (typed `## Properties`
table by default, `## Invariants` clause fences, `## Operations`
subsections) and validate through Quire against this module, accompanied by
negative fixtures that fail for a named reason, so that the skeletons are the
module's executable positive fixtures and the negatives pin what the schemas
refuse.

## Inputs

- The rewritten skeletons `skeletons/<type>.md` (one per object type) and the
  alternate-form skeletons `skeletons/data_schema.sysml.md`,
  `skeletons/queue.sysml.md`, `skeletons/ui_component.sysml.md`.
- Negative fixtures `tests/fixtures/negative/<type>-<case>.md`, each with
  frontmatter `expect:` naming the diagnostic code or reason the fixture must
  produce.
- The Quire wheel 0.46.0 or later, exposing `extract_semantic`,
  `validate_document`, and `Registry`, installed into the module's Python
  environment by `make dev-quire` (see Behavior).

## Outputs

- A validation result per skeleton with no error and no `semantic.record-invalid`.
- A semantic record per skeleton whose `fields`, `clauses`, and `operations`
  availability match the type's required set.

## Behavior

- Each skeleton with a `fields` requirement (`data_schema`, `queue`, `ui_component`) SHALL author `## Properties` as one table with the header exactly `Field | Type | Multiplicity | Constraints`.
- The `data_schema`, `queue`, and `ui_component` alternate skeletons SHALL author the same declarations as one ```` ```sysml ```` fence of `attribute <name> : <Type>[<mult>] { <constraints> }` and `ref item <name> : <Type>[<mult>]` lines.
- Each alternate skeleton SHALL declare the same fields as its table skeleton, under that skeleton's frontmatter `id` and `title`; the module therefore ships two files under one id by intent, and the identity of their extracted `FieldDecl[]` is the obligation FR-005-AC-2 tests.
- Each skeleton whose type requires `operations` (`api_endpoint`, `action`, `interface`, `external_contract`, `extension_point`) SHALL author `## Operations` with one `### <name>` per operation, an optional `| Param | Type | Multiplicity | Constraints |` table, a `Returns:` line where the operation returns a value, and optional `Pre:`/`Post:` lines that, when present, name clause ids declared in the same artifact.
- The `action` skeleton SHALL declare exactly one operation, because `Action` admits exactly one.
- The `api_endpoint` skeleton SHALL declare at least one operation carrying a `Returns:` line, and the `external_contract` skeleton at least one operation carrying a `Post:` line, because those are the item rules their schemas enforce.
- Each skeleton whose type requires `clauses` (`external_contract`, `extension_point`, `binary_format`, `rate_limit`) SHALL author `## Invariants` with one `### <clauseId>` per clause, each owning exactly one ```` ```ocl ```` fence.
- The `api_endpoint`, `data_schema`, `queue`, `action`, `ui_component`, and `interface` skeletons SHALL carry no `## Invariants` section, so the module ships both the clause-bearing and the clause-free availability state.
- Each skeleton's frontmatter SHALL carry `object: <type name>` beside `type: <type name>`, because Quire runs the semantic layer (extraction and record validation) on the `object:` archetype of a document; a skeleton without it validates its headings only.
- The manifest SHALL gain a `required: false` `section_body` locator for every `## Properties`, `## Invariants`, and `## Operations` section a skeleton introduces, so the section is asserted by the manifest and remains optional for existing artifacts.
- Every skeleton `title` SHALL be an `Identifier` (`^[A-Za-z_][A-Za-z0-9_]*$`), distinct across the ten object types and outside the `KernelScalar` names, so a `Type` cell can name it. An alternate-form skeleton shares its table skeleton's `id` and `title` by intent — the two files declare one object — so uniqueness is measured over the ten declarations, not over the thirteen files.
- Every `Type` cell that names another skeleton SHALL use that skeleton's `title`, so that under a bundle index built from the skeletons every non-kernel token resolves to `ix://agent-ix/spec-objects-architecture/type/<Title>` with no `semantic.unresolved-type` finding.
- Every skeleton SHALL keep every H2 heading whose manifest locator is `required: true` for its type (`## Endpoint`, `## Schema`, `## Message Format`, `## Inputs`, `## Props`, `## Contract`, `## Layout`, `## Thresholds`).
- No skeleton SHALL carry an H2 heading the manifest does not assert.
- Where a typed section and a kernel section describe the same declarations (the `data_schema` `## Schema` fence and its `## Properties` table; the `queue` `## Message Format` fence and its table; the `interface` `## Contract` YAML and its `## Operations`; the `ui_component` `## Props` prose and its table), the typed section SHALL be the authority and the kernel section a derived, human-facing view; [FR-006](./FR-006-architecture-lowerings.md) fixes the agreement each pair holds.
- Each negative fixture SHALL fail `validate_document` with an error whose message carries the fixture's `expect:` code, covering at least: an api endpoint whose only operation declares no return (`semantic.record-invalid`), a data schema declaring operations (`semantic.record-invalid`), a queue without an identity row (`semantic.record-invalid`), an action declaring two operations (`semantic.record-invalid`), a ui component with an identity row (`semantic.record-invalid`), an external contract with no `## Invariants` (`semantic.record-invalid`), a rate limit with no `## Invariants` (`semantic.record-invalid`), a `## Properties` section carrying both a table and a fence (`semantic.properties-both-forms`), an operation whose `Post:` names an undeclared clause (`semantic.dangling-clause-ref`), and a `Type` token that is not an `Identifier` (`semantic.invalid-type-token`); the last three re-check the engine's published diagnostics under this module's schemas rather than re-specify them.
- The repository SHALL provide a `make dev-quire` target that installs the Quire wheel this requirement names into the module's Python environment, so the semantic test dependency is provisioned by a documented command rather than by an undeclared side install.
- If the installed Quire wheel is absent or lacks `extract_semantic`, then every semantic test SHALL fail — not skip — with a message naming the missing function, the `make dev-quire` target, and `agent-ix/quire-rs#392`, so that no matrix row can pass or be reported green without the engine under test.
- While no committable index carries Quire 0.46.0, the module SHALL NOT declare `quire` in `pyproject.toml`. `internal-pypi` (the index this repo's CI uses) serves 0.33.0 at most and no `quire-rs` tag carries the semantic layer, so the wheel exists only on the dev-only `pypi.ix`; `agent-ix/quire-rs#392` is the blocking issue, and its resolution replaces the `make dev-quire` target with a committed dev dependency.
- Only a criterion this specification names as blocked SHALL be exempt from the previous rule, as an explicit expected failure naming the blocking issue. Today that is the record validation of a legacy-form artifact declaring `object:` (`agent-ix/quire-rs#391`, beside NFR-001-AC-2) and the naming half of FR-003-AC-6 (`agent-ix/quire-rs#221`, `agent-ix/quire-rs#394`).

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-005-CON-1 | The module SHALL keep the skeletons and negatives in this repository only, editing no corpus repository and no vendored quoin/quire fixture. Verified as a **tree** assertion over `git ls-files` — no `corpus/` path, no `fixtures/semantic-module` path, no `/vendor/` path and no `.gitmodules` exists in the repository, and every tracked path is part of the module's own surface — never as a diff against a moving ref, which would change meaning the moment the branch merges. | Boundary | Test |
| FR-005-CON-2 | A skeleton SHALL carry one Properties form; the alternate form is a separate file, never a second block in the same artifact. | Integrity | Test |
| FR-005-CON-3 | The bundle index SHALL hold one entry per declaration `id`, not one per file, so the three alternate-form skeletons do not list their declaration twice. | Integrity | Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-005-AC-1 | Every skeleton file (ten types plus three alternates) passes `validate_document` against this module with `is_valid` true and no `semantic.record-invalid` error. | Test |
| FR-005-AC-2 | For `data_schema`, `queue`, and `ui_component`, the table and `sysml` skeletons extract to identical normalized `fields` with `fieldsForm` `table` and `fence` respectively. | Test |
| FR-005-AC-3 | Under a bundle index built from the skeleton frontmatter, every skeleton extracts with zero `error` diagnostics and zero `semantic.unresolved-type` findings, and every non-kernel `type.target` starts with `ix://agent-ix/spec-objects-architecture/type/`. | Test |
| FR-005-AC-4 | Each skeleton's `availability` states match its type: `fields` `available` for `data_schema`, `queue`, and `ui_component`; `operations` `available` for `api_endpoint`, `action`, `interface`, `external_contract`, and `extension_point`; `clauses` `available` for `external_contract`, `extension_point`, `binary_format`, and `rate_limit`; `not_applicable` for every other kind. | Test |
| FR-005-AC-5 | Every negative fixture fails validation with an error message containing its `expect:` code, and at least the ten cases listed in Behavior are present. | Test |
| FR-005-AC-6 | Every skeleton's H2 set equals a subset of the headings the manifest asserts for its type and includes every `required: true` heading. | Test |
| FR-005-AC-7 | The skeleton for each of the ten types has no placeholder token and every asserted section body is non-empty. | Test |
| FR-005-AC-8 | Every skeleton `title` matches the `Identifier` pattern, is unique across the skeletons, and is not a `KernelScalar` name; every skeleton frontmatter carries `object` equal to `type`. | Test |
| FR-005-AC-9 | The `action` skeleton extracts exactly one operation, the `api_endpoint` skeleton at least one operation carrying `returns`, and the `external_contract` skeleton at least one operation carrying a non-empty `post`. | Test |
| FR-005-AC-10 | The bundle index the module builds holds ten entries, one per declaration id; an index built one entry per file makes every reference to an alternate-bearing declaration `semantic.ambiguous-type`, which is carried as an expected failure naming `agent-ix/quire-rs#398`. | Test |

## Dependencies

- **Upstream**: [FR-003](./FR-003-semantic-manifest-contract.md), [FR-004](./FR-004-role-schemas.md); quoin FR-071/FR-072 (`ix://agent-ix/quoin/FR-071`, `ix://agent-ix/quoin/FR-072`); quire-rs FR-070/FR-071/FR-072
- **Upstream (unpinned neighbour contract)**: the `semantic.record-invalid` diagnostic this requirement's Outputs and FR-005-AC-1 depend on exists in quire-rs source but in no quire-rs acceptance criterion; `agent-ix/quire-rs#391` is where that record-validation contract, and the code naming it, are being settled.
- **Upstream (provisioning)**: `agent-ix/quire-rs#392` — publish the 0.46.0 wheel to `internal-pypi` so `quire` can become a committed dev dependency.
- **Downstream**: [FR-006](./FR-006-architecture-lowerings.md); `agent-ix/quire-contract-ir#52` and `agent-ix/filament-core-data#36` consume the skeletons read-only
