---
id: data-schema-001
title: "ArtifactRecord"
type: data_schema
object: data_schema
---
<!-- data_schema authoring skeleton, alternate Properties form. Declares exactly
     the same fields as data_schema.md, authored as one ```sysml``` fence
     instead of the typed table (FR-005-AC-2). One artifact carries one form;
     the alternate is a separate file, never a second block in the same
     artifact. -->
# [data-schema-001] ArtifactRecord

## Properties

```sysml
attribute artifact_id : UUID[1..1] { identity }
attribute digest : String[1..1] { minLength: 64, maxLength: 64 }
attribute size_bytes : Integer[1..1] { min: 0 }
attribute content_type : String[0..1]
attribute created_at : Timestamp[1..1]
```

## Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ArtifactRecord",
  "type": "object",
  "required": ["artifact_id", "digest", "size_bytes", "created_at"],
  "properties": {
    "artifact_id": { "type": "string", "format": "uuid" },
    "digest": { "type": "string", "minLength": 64, "maxLength": 64 },
    "size_bytes": { "type": "integer", "minimum": 0 },
    "content_type": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" }
  },
  "additionalProperties": false
}
```
