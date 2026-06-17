---
id: IT-001
title: "Manifest activation roundtrip against filament-core"
type: IT
relationships:
  - target: "ix://agent-ix/spec-objects-architecture/FR-001"
    type: "verifies"
---
# [IT-001] Manifest activation roundtrip

## Objective

Verify that this Module's manifest activates against a clean filament-core-service instance and that every declared contribution lands in the database, including idempotent re-activation. Without this test, a manifest that fails to register its archetypes, object types, grammars, or artifact types — or that duplicates rows on re-activation — would go undetected.

## Target Integration

The service under test is filament-core-service, reached over its HTTP module-activation API. The integration exercised is an HTTP client call submitting `spec_objects_architecture/manifest.yaml` to `POST /api/v1/modules/activate`, followed by HTTP reads of the registry endpoints (`/api/v1/archetypes`, `/api/v1/object-types`, `/api/v1/grammars`, `/api/v1/artifact-types`).

## Preconditions

A filament-core-service instance is deployed to a clean cluster (or the kind dev cluster) and reachable, with an empty `modules` registry so the presence of newly created rows is meaningful.

## Inputs

This repo's packaged `spec_objects_architecture/manifest.yaml`, submitted to the activation endpoint `POST /api/v1/modules/activate`.

## Test Procedure

Each step performs one discrete action and has its own success criterion.

1. Deploy filament-core-service to a clean cluster (or use the kind dev cluster).
2. POST `spec_objects_architecture/manifest.yaml` to `/api/v1/modules/activate`.
   - IT-001-SC-01: the endpoint returns 200 OK and a `modules` row is created.
3. GET `/api/v1/archetypes`, `/api/v1/object-types`, `/api/v1/grammars`, and `/api/v1/artifact-types`.
   - IT-001-SC-02: each declared item is present with correct attributes.
4. Re-POST the same manifest.
   - IT-001-SC-03: the response is an idempotent no-op (same `modules.id`, same SHA-256 content hash, no row duplication).

## Expected Results

The first activation returns 200 OK and creates a `modules` row plus every declared archetype, object type, grammar, and artifact type in the corresponding registry tables. Re-activation produces the same `modules.id` and the same SHA-256 content hash with no duplicated rows. The test passes only when every per-step success criterion holds.
