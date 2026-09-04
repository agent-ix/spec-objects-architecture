---
id: action-001
title: "VerifyArtifactChecksum"
type: action
object: action
---
<!-- action authoring skeleton (spec-objects-architecture). Fill every section
     with substantive content. Contract (manifest body_extraction asserts):
     - Frontmatter MUST carry id, title, type: action, object: action.
     - "## Operations" (H2): Action.json admits EXACTLY ONE operation — an
       action that declared two invocations would be a process. The operation
       owns one `### <name>` heading with its parameter table and a `Returns:`
       line where it answers with a value.
     - "## Inputs" (H2, required): every input the action consumes, with type
       and source. It is the human-facing view of the operation's parameter
       table.
     - An action declares one invocation, not data: Action.json forbids
       `fields`, so there is no "## Properties" section.
     - Keep headings unique per level. -->
# [action-001] VerifyArtifactChecksum

## Inputs

- `artifact_id` (uuid) — identifies the uploaded artifact to verify; supplied
  by the `artifact.uploaded` queue message.
- `declared_digest` (hex SHA-256 string) — the digest the uploader claimed;
  read from the artifact's import manifest.
- `content_stream` (bytes) — the stored artifact bytes, streamed from the
  object store so verification never buffers the whole artifact in memory.

## Operations

The single operation the VerifyArtifactChecksum declaration exposes. Action.json
admits exactly one, which is what makes an action distinguishable from a
multi-step process.

### verify_artifact_checksum

Recompute the SHA-256 of the streamed artifact bytes and compare it with the
digest the uploader declared; answers true when the two agree and false when
they differ, never raising for a mismatch.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| artifact_id | UUID | 1..1 | |
| declared_digest | String | 1..1 | minLength: 64, maxLength: 64 |
| content_stream | Bytes | 1..1 | nonEmpty |

Returns: Boolean[1..1]
