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
unchanged at 0.3.0, and SHALL keep the fence and section text those locators
yield byte-identical between the two versions. Yields of locators added at
0.3.0 are unmeasured and are not claimed.

## Scope

- Applies to: `manifest.yaml`, the shipped schemas, and the skeletons.
- Operational context: existing corpus artifacts authored in legacy forms
  (prose `## Contract`, untyped `## Props` bullet lists) under
  `legacy_forms: warning`; no corpus repository is edited.

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
| Each legacy-form skeleton under 0.3.0: `semantic.legacy-properties-form` warnings | 1 | 1 | Test |
| 0.2.0 locator yield per legacy skeleton, 0.2.0 vs 0.3.0 | identical | identical | Test |
| Object types whose `allowed_links` set changed | 0 | 0 | Test |

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

A checked-in copy of the 0.2.0 `body_extraction` and of all ten 0.2.0
skeletons is compared against the 0.3.0 manifest and validated under it: the
locator definitions are equal, each legacy skeleton validates with no error
and — where it carries a legacy-form Properties section — exactly one
legacy-form warning, and each 0.2.0 locator yield is unchanged. The
`allowed_links` sets are compared in the same baseline diff, because a changed
edge vocabulary would change the graph the corpus already carries.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| NFR-001-AC-1 | Every 0.2.0 `body_extraction` locator is present in 0.3.0 with identical facets (0 changed). | Test |
| NFR-001-AC-2 | Every skeleton of the checked-in 0.2.0 set validates under 0.3.0 with 0 error findings. | Test |
| NFR-001-AC-3 | Each 0.2.0 skeleton carrying a legacy-form Properties section yields exactly 1 `semantic.legacy-properties-form` warning. | Test |
| NFR-001-AC-4 | Each 0.2.0 locator's yield for each 0.2.0 skeleton is byte-identical under 0.2.0 and 0.3.0. | Test |
| NFR-001-AC-5 | Every object type's `allowed_links` and `roles` sets are identical at 0.2.0 and 0.3.0. | Test |

## Dependencies

- **Upstream**: [FR-003](../functional/FR-003-semantic-manifest-contract.md), [FR-005](../functional/FR-005-executable-skeletons.md), [FR-006](../functional/FR-006-architecture-lowerings.md); quoin FR-074 (`ix://agent-ix/quoin/FR-074`)
- **Downstream**: corpus promotion (`agent-ix/quoin#291` sweep), outside this module
