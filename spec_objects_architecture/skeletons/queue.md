---
id: queue-001
title: "ArtifactIngestQueue"
type: queue
object: queue
---
<!-- queue authoring skeleton (spec-objects-architecture). Fill every section
     with substantive content. Contract (manifest body_extraction asserts):
     - Frontmatter MUST carry id, title, type: queue, object: queue.
     - "## Properties" (H2): one typed row per message-envelope field, header
       exactly `Field | Type | Multiplicity | Constraints`. Queue.json requires
       at least one row carrying the `identity` constraint — the partition key.
     - "## Message Format" (H2, required): MUST contain a fenced ```json code
       block holding an example message payload. It is a derived, human-facing
       view of the same declarations (FR-006): the same key set as the table.
     - A queue carries messages, it does not expose calls: Queue.json forbids
       `operations`, so there is no "## Operations" section.
     - Keep headings unique per level. -->
# [queue-001] ArtifactIngestQueue

## Properties

| Field | Type | Multiplicity | Constraints |
|---|---|---|---|
| artifact_id | UUID | 1..1 | identity |
| event | String | 1..1 | minLength: 1 |
| digest | String | 1..1 | minLength: 64, maxLength: 64 |
| size_bytes | Integer | 1..1 | min: 0 |
| uploaded_at | Timestamp | 1..1 | |

## Message Format

Each message announces one uploaded artifact awaiting checksum verification.
Messages are JSON-encoded and keyed by `artifact_id` for partition affinity.

```json
{
  "artifact_id": "7f9c2ba4-e88f-4aa9-a3c1-0d2e6f1b5a90",
  "event": "artifact.uploaded",
  "digest": "a3f5c1d2e6b4980f7c2a1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8091a2b3c4d5e6",
  "size_bytes": 1048576,
  "uploaded_at": "2026-06-10T12:00:00Z"
}
```
