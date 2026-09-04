---
id: ui-component-001
title: "ArtifactTable"
type: ui_component
object: ui_component
---
<!-- ui_component authoring skeleton, alternate Properties form. Declares
     exactly the same props as ui_component.md, authored as one ```sysml```
     fence instead of the typed table (FR-005-AC-2). One artifact carries one
     form; the alternate is a separate file, never a second block in the same
     artifact. -->
# [ui-component-001] ArtifactTable

## Properties

```sysml
ref item artifacts : ArtifactRecord[0..* ordered]
attribute page_size : Integer[1..1] { min: 1, max: 200 }
attribute loading : Boolean[1..1]
attribute empty_message : String[0..1] { minLength: 1 }
```

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
