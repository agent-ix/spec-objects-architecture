---
id: api-endpoint-001
title: "ArtifactUploadEndpoint"
type: api_endpoint
object: api_endpoint
---
<!-- api_endpoint authoring skeleton (spec-objects-architecture). Fill every
     section with substantive content. Contract (manifest body_extraction
     asserts):
     - Frontmatter MUST carry id, title, type: api_endpoint, object: api_endpoint.
     - "## Operations" (H2): one `### <name>` per operation, an optional
       `| Param | Type | Multiplicity | Constraints |` table, a `Returns:`
       line where the operation answers with a value, and optional
       `Pre:`/`Post:` lines naming clause ids declared in this artifact.
       ApiEndpoint.json requires at least one operation that returns.
     - "## Endpoint" (H2, required): what the endpoint does and why, plus
       the concrete method + path routes (multi-route surfaces list every
       route here — there is no separate Routes section; format-walkthrough
       decision #20).
     - "## 2. API Contract" (H2, optional): request/response detail; the
       numbered heading text "2. API Contract" is matched verbatim.
     - An endpoint declares operations, not data: ApiEndpoint.json forbids
       `fields`, so there is no "## Properties" section.
     - Keep headings unique per level. -->
# [api-endpoint-001] ArtifactUploadEndpoint

## Endpoint

`POST /artifacts` accepts a binary artifact upload together with a declared
SHA-256 digest and persists the artifact to the store once the computed
digest matches the declared digest. Mismatches are rejected before anything
is written.

Routes:

- `POST /artifacts` — upload a new artifact (multipart body + digest field)
- `GET /artifacts/{artifact_id}` — fetch artifact metadata by id
- `GET /artifacts/{artifact_id}/content` — stream the stored artifact bytes

## 2. API Contract

- Request: `multipart/form-data` with parts `content` (artifact bytes) and
  `digest` (hex-encoded SHA-256 of the content part).
- Response `201 Created`: JSON body `{"artifact_id": "...", "digest": "..."}`.
- Response `422 Unprocessable Entity`: digest mismatch; the body carries the
  declared and computed digest pair.
- Auth: bearer token carrying the `artifacts:write` scope.

## Operations

The operations the ArtifactUploadEndpoint declaration exposes. Each operation
owns one `### <name>` heading with an optional parameter table and a
`Returns:` line where it answers with a value. Every non-kernel type token
names a `data_schema` declaration this module ships.

### upload_artifact

Accept the artifact bytes plus the declared digest, verify the two agree, and
persist the artifact; answers with the stored record.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| content | Bytes | 1..1 | nonEmpty |
| declared_digest | String | 1..1 | minLength: 64, maxLength: 64 |
| content_type | String | 0..1 | |

Returns: ArtifactRecord[1..1]

### get_artifact

Fetch one artifact's metadata by id without streaming its bytes.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| artifact_id | UUID | 1..1 | |

Returns: ArtifactRecord[0..1]

### stream_artifact_content

Stream the stored bytes of one artifact to the caller.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| artifact_id | UUID | 1..1 | |

Returns: Bytes[1..1]
