---
id: NFR-001
title: "Additive compatibility of the semantic contract"
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
---
# NFR-001: Additive compatibility of the semantic contract

## Statement

The module SHALL keep every artifact of the checked-in 0.2.0 skeleton set —
the ten skeletons as they stood at manifest version 0.2.0, which is the
population this NFR measures — validating against version 0.3.0 with at most
warning-level semantic findings.

The module SHALL keep every 0.2.0 `body_extraction` locator definition
unchanged at 0.3.0.

The module SHALL keep the fence and section text those locators yield
byte-identical between the two versions. Yields of locators added at 0.3.0 are
unmeasured and are not claimed.

The module SHALL keep every object type's `allowed_links` and `roles` sets
unchanged at 0.3.0, because a changed edge vocabulary would change the graph
the corpus already carries.

## Scope

- Applies to: `manifest.yaml`, the shipped schemas, and the skeletons.
- Operational context: existing corpus artifacts authored in legacy forms
  (prose `## Contract`, untyped `## Props` bullet lists) under
  `legacy_forms: warning`; no corpus repository is edited.
- Not applied to: the wild corpus. This NFR's population is the ten
  checked-in 0.2.0 skeletons, and the number below counts only those. A
  census of `~/dev` on 2026-09-04 — every Markdown file whose frontmatter
  `type:` is one of the ten, excluding this repository, `node_modules` and
  `.git` — found **24 artifacts in three types**: `api_endpoint` 10,
  `external_contract` 9, `interface` 5, and none in the other seven. **0 of
  the 24 carry `object:`**, which is why they are unaffected today and why
  this NFR holds. It is also why promotion is a separate, gated step: the day
  `agent-ix/quoin#291` adds `object:` to them, each will be judged against its
  type schema, and none currently authors the `## Operations` or
  `## Invariants` sections `ApiEndpoint`, `Interface` and `ExternalContract`
  require. That migration belongs to the promotion sweep, not to this
  requirement, and no corpus artifact is edited here.

## Rationale

The ticket's merge gate is advisory-only until corpus promotion, and it
forbids enabling impact propagation or extraction behaviour. A module that
turned legacy artifacts into errors would force corpus edits this campaign
forbids; a module that changed a locator would change every existing
extraction record, which is exactly the resource-identity change the gate says
needs controlled-corpus evidence.

## Measurement and Evaluation

| Metric | Target | Threshold | Method |
|--------|--------|-----------|--------|
| 0.2.0 locators changed | 0 | 0 | Test |
| Checked-in 0.2.0 skeleton set under 0.3.0: error findings, per skeleton | 0 | 0 | Test |
| `semantic.legacy-properties-form` warnings over the ten checked-in 0.2.0 skeletons | 0 | 0 | Test |
| 0.2.0 skeletons carrying a `## Properties` section in any form (the population the warning could fire on) | 0 | 0 | Test |
| 0.2.0 locator yield per 0.2.0 skeleton, 0.2.0 vs 0.3.0 | identical | identical | Test |
| Object types whose `allowed_links` or `roles` set changed | 0 | 0 | Test |

## Verification

NFR-001-AC-2 holds on the population this NFR measures, and the measurement
says why: no 0.2.0 skeleton carries a frontmatter `object:` key, so Quire runs
headings-only validation on it and never assembles or checks a typed record.
That is what makes 0.3.0 additive for the artifacts that exist today, and it
is asserted rather than assumed.

The engine defect behind it is real but differently scoped: once a legacy-form
artifact *does* declare `object:`, quire 0.46.0 assembles its declaration
record as `{}` and validates it against the type schema unconditionally, so it
fails `semantic.record-invalid` at error severity even under
`legacy_forms: warning`. `agent-ix/quire-rs#391` owns that rule. The module
carries that case as an explicit expected failure beside NFR-001-AC-2 rather
than relaxing a schema, so the day the engine changes, the row turns red and
is noticed.

The legacy-form warning count is 0, and the measurement says what that
counts and why. `semantic.legacy-properties-form` fires on a `## Properties`
section authored in a legacy form; not one of the ten checked-in 0.2.0
architecture skeletons has a `## Properties` section at all — their sections
are `Endpoint`, `Schema`, `Message Format`, `Inputs`, `Props`, `Contract`,
`Layout` and `Thresholds`. The population the warning could fire on is
therefore empty, and NFR-001-AC-3 asserts that emptiness rather than claiming
a warning the module cannot produce. This is the one place this module
measures differently from `spec-objects-business`, whose 0.2.0 skeletons do
carry bullet-list Properties sections; copying its "exactly one warning"
target here would have been a green row over nothing.

A checked-in copy of the 0.2.0 `body_extraction`, the 0.2.0 edge vocabulary,
and all ten 0.2.0 skeletons is compared against the 0.3.0 manifest and
validated under it: the locator definitions are equal, each skeleton validates
with no error and no legacy-form warning, each 0.2.0 locator yield is
unchanged, and no `allowed_links` or `roles` set moved.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| NFR-001-AC-1 | Every 0.2.0 `body_extraction` locator is present in 0.3.0 with identical facets (0 changed). | Test |
| NFR-001-AC-2 | Every skeleton of the checked-in 0.2.0 set validates under 0.3.0 with 0 error findings. | Test |
| NFR-001-AC-3 | No 0.2.0 skeleton carries a `## Properties` section in any form, and the `semantic.legacy-properties-form` warning count over the ten of them is 0. | Test |
| NFR-001-AC-4 | Each 0.2.0 locator's yield for each 0.2.0 skeleton is byte-identical under 0.2.0 and 0.3.0. | Test |
| NFR-001-AC-5 | Every object type's `allowed_links` and `roles` sets are identical at 0.2.0 and 0.3.0. | Test |

## Dependencies

- **Upstream**: [FR-003](../functional/FR-003-semantic-manifest-contract.md), [FR-005](../functional/FR-005-executable-skeletons.md), [FR-006](../functional/FR-006-architecture-lowerings.md); quoin FR-074 (`ix://agent-ix/quoin/FR-074`)
- **Downstream**: corpus promotion (`agent-ix/quoin#291` sweep), outside this module
