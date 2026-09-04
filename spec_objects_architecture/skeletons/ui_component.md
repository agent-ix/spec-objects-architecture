---
id: ui-component-001
title: "ArtifactTable"
type: ui_component
object: ui_component
---
<!-- ui_component authoring skeleton (spec-objects-architecture). Fill every
     section with substantive content. Contract (manifest body_extraction
     asserts):
     - Frontmatter MUST carry id, title, type: ui_component, object: ui_component.
     - "## Properties" (H2): one typed row per prop, header exactly
       `Field | Type | Multiplicity | Constraints`. UiComponent.json admits
       ZERO identity rows — props are not identified; identity belongs to the
       record a prop references.
     - "## Props" (H2, required): the human-facing description of the same
       props, one bullet per row of the table.
     - Keep headings unique per level. -->
# [ui-component-001] ArtifactTable

## Properties

| Field | Type | Multiplicity | Constraints |
|---|---|---|---|
| artifacts | ArtifactRecord | 0..* ordered | |
| page_size | Integer | 1..1 | min: 1, max: 200 |
| loading | Boolean | 1..1 | |
| empty_message | String | 0..1 | minLength: 1 |

## Props

- `artifacts: ArtifactRecord[]` — the artifact records to render, one row per
  artifact with digest, size, and upload time columns; render order is the
  order given.
- `page_size: number` — rows per page; the table paginates client-side when
  `artifacts.length` exceeds this value (default 25).
- `loading: boolean` — when true the table renders a skeleton row state and
  disables row selection.
- `empty_message: string` — the text shown in place of the table body when
  `artifacts` is empty; a default is used when it is omitted.
