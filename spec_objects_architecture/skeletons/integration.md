---
id: integration-001
title: "Object storage backend"
artifact_type: integration
---
<!-- integration authoring skeleton (spec-objects-architecture). Fill every
     section with substantive content. Contract (manifest body_extraction
     asserts):
     - Frontmatter MUST carry id, title, artifact_type; artifact_type is
       integration (quire resolves the archetype from it).
     - "## Endpoints" (H2, required): the external endpoints this integration
       calls.
     - "## Behavior" (H2, required): how the system uses them, including
       failure handling.
     - Keep headings unique per level. -->
# [integration-001] Object storage backend

## Endpoints

- `PUT {bucket}/artifacts/{artifact_id}` — store artifact bytes after a
  successful checksum verification.
- `GET {bucket}/artifacts/{artifact_id}` — stream stored artifact bytes back
  to download requests.
- `DELETE {bucket}/artifacts/{artifact_id}` — remove artifacts that fail
  verification or are purged by retention.

## Behavior

The artifact store writes to an S3-compatible bucket using pre-signed,
content-addressed keys. Uploads are written to a staging prefix first and
moved to the canonical prefix only after digest verification succeeds.
Transient 5xx responses are retried three times with exponential backoff;
after the final failure the upload is marked `storage_failed` and the staged
object is deleted.
