---
id: StR-001
title: "Tier-2 architecture objects"
type: StR
---
# [StR-001] Tier-2 architecture objects

## Stakeholder

Filament platform / spec authors / agent CLI generators.

## Need

Architecture specs need extractable graph entities for API endpoints, UI components, data schemas, queues, actions, integrations.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| StR-001-AC-1 | A Module activation against filament-core registers the contents this module declares. |
| StR-001-AC-2 | Agent CLI generators (minijinja-cli) can produce valid artifacts using the templates and schemas this module ships. |

## Dependencies

- **Upstream**: filament-core-service FR-035 (Module Manifest Schema)
