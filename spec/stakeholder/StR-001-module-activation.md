---
id: StR-001
title: "Tier-2 architecture objects"
type: StR
---
# StR-001: Tier-2 architecture objects

## Stakeholder Need

The Filament platform, spec authors, and agent CLI generators **SHALL** obtain extractable graph entities for the ten technical architecture concerns this module contributes — API endpoints, data schemas, queues, actions, UI components, interfaces, external contracts, extension points, binary formats, and rate limits — from architecture specs. The need is stated from the consumers' perspective and avoids prescribing a mechanism. The `integration` object type this need once named was retired by format-walkthrough decision #8: an internal contract is an `interface`, an external one an `external_contract`.

## Rationale

Spec authors and agent CLI generators (minijinja-cli) are accountable for producing valid, machine-extractable architecture artifacts. Without a shared set of tier-2 object types and the skeletons and schemas to produce them, each consumer would reinvent the entity model, and Module activation against filament-core could not register a consistent set of contributions. A single Module supplying these object types preserves consistency across the platform.

## Validation Criteria


| ID | Criteria | Validation |
|----|----------|------------|
| StR-001-VC-1 | A Module activation against filament-core registers the contents this module declares. | Inspection |
| StR-001-VC-2 | An agent CLI generator (minijinja-cli) renders every skeleton this module ships and each rendered artifact validates against the module. | Demonstration |
| StR-001-VC-3 | Every object type ships a typed declaration schema a fixture reader can consume; an api-endpoint record and a rate-limit record are distinguishable by schema alone. | Demonstration |

Satisfaction is judged by demonstrating all three outcomes against a live filament-core instance, a generator run, and the shipped schemas.

## Dependencies

Relationships at the stakeholder level. **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) (Module Manifest Schema).
