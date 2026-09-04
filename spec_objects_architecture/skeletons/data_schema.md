---
id: data-schema-001
title: "ArtifactRecord"
type: data_schema
object: data_schema
---
<!-- data_schema authoring skeleton (spec-objects-architecture). Fill every
     section with substantive content. Contract (manifest body_extraction
     asserts):
     - Frontmatter MUST carry id, title, type: data_schema, object: data_schema.
     - "## Properties" (H2): one typed row per property, header exactly
       `Field | Type | Multiplicity | Constraints`. This is the authority.
     - "## Schema" (H2, required): MUST contain a fenced ```json code block
       holding the JSON Schema for the record. It is a derived, human-facing
       view of the same declarations (FR-006): the same property names, and
       a `required` list equal to the rows whose multiplicity lower bound
       is 1.
     - The record is registered as a `TypeRef` target under
       ix://agent-ix/spec-objects-architecture/type/ArtifactRecord, so an
       api_endpoint operation or a queue message field can name it.
     - A record declares data, not behaviour: DataSchema.json forbids
       `operations`, so there is no "## Operations" section.
     - Keep headings unique per level. -->
# [data-schema-001] ArtifactRecord

## Properties

| Field | Type | Multiplicity | Constraints |
|---|---|---|---|
| artifact_id | UUID | 1..1 | identity |
| digest | String | 1..1 | minLength: 64, maxLength: 64 |
| size_bytes | Integer | 1..1 | min: 0 |
| content_type | String | 0..1 | |
| created_at | Timestamp | 1..1 | |

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
