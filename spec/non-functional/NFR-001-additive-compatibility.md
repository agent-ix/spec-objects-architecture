---
id: NFR-001
title: "Compatibility of the semantic contract"
type: NFR
quality_attribute: compatibility
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/FR-003"
    type: "constrains"
  - target: "ix://agent-ix/spec-objects-architecture/FR-004"
    type: "constrains"
  - target: "ix://agent-ix/spec-objects-architecture/FR-005"
    type: "constrains"
  - target: "ix://agent-ix/spec-objects-architecture/FR-006"
    type: "constrains"
  - target: "ix://agent-ix/spec-objects-architecture/FR-007"
    type: "depends_on"
---
# NFR-001: Compatibility of the semantic contract

## Statement

The module SHALL be additive for every 0.2.0 artifact except in two declared
breaks, measured over the checked-in 0.2.0 skeleton set — the ten skeletons as
they stood at manifest version 0.2.0: each 0.2.0 skeleton outside those breaks
validates against version 0.4.0 with at most warning-level semantic findings,
each 0.2.0 `body_extraction` locator is unchanged apart from the object id
`regex`, and the fence and section text those locators yield is byte-identical
between the two versions. Yields of locators added at 0.4.0 are unmeasured and
are not claimed.

The two breaks are:

- **Object ids.** An object id SHALL match `^[A-Za-z][A-Za-z0-9_]*$`
  ([FR-003](../functional/FR-003-semantic-manifest-contract.md)). An artifact
  whose id carries a hyphen, as every 0.2.0 skeleton's does, is refused with
  its required `id` missing, on all fourteen object types.
- **Interface feature order.** An `interface` artifact SHALL author a
  `## Features` table (`Feature | Kind`) carrying its feature order
  ([FR-007](../functional/FR-007-systems-model-kinds.md)). The `features`
  locator is required, so an interface without the table, as the 0.2.0
  `interface` skeleton is, is refused with its required `features` missing.

These refusals are breaking for an artifact that validated at 0.2.0, so the
manifest declares `compatibility_posture: strict` (FR-003).

The module SHALL keep every 0.2.0 object type's `allowed_links` set unchanged
at 0.4.0 except for one named addition: `interface` admits `specializes` to
`interface` ([FR-007](../functional/FR-007-systems-model-kinds.md)), so an
interface can declare its supertypes. The addition widens what an interface
may link to and changes no edge the corpus already carries.

The module SHALL keep every 0.2.0 object type's `roles` set unchanged at 0.4.0
except for one named addition: `interface` gains the role `systems-interface`
after its 0.2.0 roles ([FR-007](../functional/FR-007-systems-model-kinds.md)),
so a systems port can name the interface it is typed by. A role addition
changes no edge the corpus carries: it only widens the targets a new object
type's `allowed_links` may name.

## Scope

- Applies to: `manifest.yaml`, the shipped schemas, and the skeletons.
- Additive: every 0.2.0 locator other than the `id` regex, the legacy
  `## Contract` and `## Props` forms, and every locator added at 0.4.0 except
  `interface.features`.
- Breaking: the object id, which admits no hyphen, on all fourteen object
  types; and the `interface` `## Features` table, which every interface must
  author.
- Operational context: existing corpus artifacts authored in legacy forms
  (prose `## Contract`, untyped `## Props` bullet lists) under
  `legacy_forms: warning`; no corpus repository is edited.
- Not applied to: the wild corpus. This NFR's population is the ten
  checked-in 0.2.0 skeletons, and the number below counts only those. A
  census of `~/dev` on 2026-09-04 — every Markdown file whose frontmatter
  `type:` is one of the ten, excluding this repository, `node_modules` and
  `.git` — found **24 artifacts in three types**: `api_endpoint` 10,
  `external_contract` 9, `interface` 5, and none in the other seven. **0 of
  the 24 carry `object:`**. Each hyphenated id among them and each of the 5
  interfaces without a `## Features` table is refused by the declared breaks;
  migrating them belongs to the promotion sweep (`agent-ix/quoin#291`), and
  no corpus artifact is edited here.

## Rationale

The ticket's merge gate is advisory-only until corpus promotion, and it
forbids enabling impact propagation or extraction behaviour. A module that
changed a locator would change every existing extraction record, which is
exactly the resource-identity change the gate says needs controlled-corpus
evidence, so every locator outside the two breaks stays as it was. The breaks
are the architect's object-id ruling and the IR's ordered interface features
(QSpec FR-152), neither of which an additive form can carry.

## Measurement and Evaluation

| Metric | Target | Threshold | Method |
|--------|--------|-----------|--------|
| 0.2.0 locators changed, the `id` regex aside | 0 | 0 | Test |
| Checked-in 0.2.0 skeleton set under 0.4.0, ids in word form, `interface` excluded: error findings, per skeleton | 0 | 0 | Test |
| Each 0.2.0 skeleton with its frozen hyphenated id: error findings other than its required `id` missing | 0 | 0 | Test |
| The 0.2.0 `interface` skeleton, id in word form: error findings other than its required `features` missing | 0 | 0 | Test |
| `semantic.legacy-properties-form` warnings over the ten checked-in 0.2.0 skeletons | 0 | 0 | Test |
| 0.2.0 skeletons carrying a `## Properties` section in any form (the population the warning could fire on) | 0 | 0 | Test |
| 0.2.0 locator yield per 0.2.0 skeleton, ids in word form, 0.2.0 vs 0.4.0 | identical | identical | Test |
| 0.2.0 object types whose `allowed_links` or `roles` set differs from 0.2.0 plus the named `interface` additions | 0 | 0 | Test |

## Verification

No 0.2.0 skeleton carries a frontmatter `object:` key, so Quire runs
headings-only validation on it and never assembles or checks a typed record;
NFR-001-AC-2 asserts that rather than assuming it. The checked-in 0.2.0 set is
a frozen capture and keeps its original hyphenated ids, so each skeleton is
measured twice: with its frozen id it draws only the required-`id` refusal,
and with its id in word form it validates, except `interface`, which draws
only the required-`features` refusal.

The engine defect behind the `object:` case is real but differently scoped:
once a legacy-form artifact *does* declare `object:`, quire 0.46.0 assembles
its declaration record as `{}` and validates it against the type schema
unconditionally, so it fails `semantic.record-invalid` at error severity even
under `legacy_forms: warning`. `agent-ix/quire-rs#391` owns that rule. The
module carries that case as an explicit expected failure beside NFR-001-AC-2
rather than relaxing a schema, so the day the engine changes, the row turns
red and is noticed.

The legacy-form warning count is 0, and the measurement says what that
counts and why. `semantic.legacy-properties-form` fires on a `## Properties`
section authored in a legacy form; not one of the ten checked-in 0.2.0
architecture skeletons has a `## Properties` section at all — their sections
are `Endpoint`, `Schema`, `Message Format`, `Inputs`, `Props`, `Contract`,
`Layout` and `Thresholds`. The population the warning could fire on is
therefore empty, and NFR-001-AC-3 asserts that emptiness rather than claiming
a warning the module cannot produce. This is the one place this module
measures differently from `spec-objects-business`, whose 0.2.0 skeletons do
carry bullet-list Properties sections.

A checked-in copy of the 0.2.0 `body_extraction`, the 0.2.0 edge vocabulary,
and all ten 0.2.0 skeletons is compared against the 0.4.0 manifest and
validated under it: the locator definitions are equal apart from the `id`
regex, each skeleton draws exactly the refusals the two breaks name and no
legacy-form warning, each 0.2.0 locator yield is unchanged, and the only
`allowed_links` and `roles` changes are the named `interface` additions.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| NFR-001-AC-1 | Every 0.2.0 `body_extraction` locator is present in 0.4.0 with identical facets (0 changed), except that the `id` locator also carries the FR-003 `regex`. | Test |
| NFR-001-AC-2 | Every skeleton of the checked-in 0.2.0 set, with its frozen hyphenated id, draws only its required `id` missing; with its id in word form, it validates under 0.4.0 with 0 error findings, except `interface`, whose only error is its required `features` missing. | Test |
| NFR-001-AC-3 | No 0.2.0 skeleton carries a `## Properties` section in any form, and the `semantic.legacy-properties-form` warning count over the ten of them is 0. | Test |
| NFR-001-AC-4 | Each 0.2.0 locator's yield for each 0.2.0 skeleton, its id in word form, is byte-identical under 0.2.0 and 0.4.0. | Test |
| NFR-001-AC-5 | Every 0.2.0 object type's `allowed_links` and `roles` sets are identical at 0.2.0 and 0.4.0, except that `interface` gains exactly the role `systems-interface`, appended, and exactly the link `specializes: [interface]`. | Test |

## Dependencies

- **Upstream**: [FR-003](../functional/FR-003-semantic-manifest-contract.md), [FR-005](../functional/FR-005-executable-skeletons.md), [FR-006](../functional/FR-006-architecture-lowerings.md), [FR-007](../functional/FR-007-systems-model-kinds.md); quoin FR-074 (`ix://agent-ix/quoin/FR-074`)
- **Downstream**: corpus promotion (`agent-ix/quoin#291` sweep), outside this module
