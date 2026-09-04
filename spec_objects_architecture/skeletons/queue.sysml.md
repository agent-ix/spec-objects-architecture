---
id: queue-001
title: "ArtifactIngestQueue"
type: queue
object: queue
---
<!-- queue authoring skeleton, alternate Properties form. Declares exactly the
     same fields as queue.md, authored as one ```sysml``` fence instead of the
     typed table (FR-005-AC-2). One artifact carries one form; the alternate is
     a separate file, never a second block in the same artifact. -->
# [queue-001] ArtifactIngestQueue

## Properties

```sysml
attribute artifact_id : UUID[1..1] { identity }
attribute event : String[1..1] { minLength: 1 }
attribute digest : String[1..1] { minLength: 64, maxLength: 64 }
attribute size_bytes : Integer[1..1] { min: 0 }
attribute uploaded_at : Timestamp[1..1]
```

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
