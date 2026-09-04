---
id: StR-001
title: "Tier-2 architecture objects"
type: StR
---
# StR-001: Tier-2 architecture objects

## Stakeholder Need

The Filament platform, spec authors, and agent CLI generators **SHALL** be able to extract graph entities for technical architecture concerns — API endpoints, UI components, data schemas, queues, actions, and integrations — from architecture specs. The need is stated from the consumers' perspective and avoids prescribing a mechanism.

## Rationale

Spec authors and agent CLI generators (minijinja-cli) are accountable for producing valid, machine-extractable architecture artifacts. Without a shared set of tier-2 object types and the templates and schemas to produce them, each consumer would reinvent the entity model, and Module activation against filament-core could not register a consistent set of contributions. A single Module supplying these object types preserves consistency across the platform.

## Validation Criteria


| ID | Criteria | Validation |
|----|----------|------------|
| StR-001-VC-1 | A Module activation against filament-core registers the contents this module declares. | Inspection |
| StR-001-VC-2 | Agent CLI generators (minijinja-cli) can produce valid artifacts using the templates and schemas this module ships. | Demonstration |
| StR-001-VC-3 | Every object type ships a typed declaration schema a fixture reader can consume; an api-endpoint record and a rate-limit record are distinguishable by schema alone. | Demonstration |

Satisfaction is judged by demonstrating all three outcomes against a live filament-core instance, a generator run, and the shipped schemas.

## Dependencies

Relationships at the stakeholder level. **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) (Module Manifest Schema).
