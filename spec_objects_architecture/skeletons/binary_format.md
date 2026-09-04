---
id: binary-format-001
title: "IndexMetadataBlock"
type: binary_format
object: binary_format
---
<!-- binary_format authoring skeleton (spec-objects-architecture). Fill
     every section with substantive content. Contract (manifest
     body_extraction asserts):
     - Frontmatter MUST carry id, title, type: binary_format,
       object: binary_format.
     - "## Invariants" (H2): one `### <clauseId>` per clause, each owning
       exactly one ```ocl``` fence. BinaryFormat.json requires at least one
       clause — this kind exists to pin the layout invariants (no overlap,
       size accounting, magic) that the YAML table alone cannot enforce.
     - "## Layout" (H2, required): MUST contain a fenced ```yaml code block
       describing the persisted binary layout — one or more record types,
       each with per-field name/offset/size/type (and endianness where it
       matters). This kind exists because JSON Schema has no offsets/
       strides/endianness vocabulary; use `data_schema` for genuinely
       JSON-shaped data.
     - A binary layout declares bytes, not typed fields or calls:
       BinaryFormat.json forbids `fields` and `operations`, so there is
       neither a "## Properties" nor an "## Operations" section.
     - Keep headings unique per level. -->
# [binary-format-001] IndexMetadataBlock

## Layout

```yaml
format: index-metadata
endianness: little
record_types:
  - name: metadata_block
    magic: 0x56494345
    size: 80
    fields:
      - { name: magic,            offset: 0,  size: 4, type: u32 }
      - { name: format_version,   offset: 4,  size: 4, type: u32 }
      - { name: dimensions,       offset: 8,  size: 2, type: u16 }
      - { name: quant_kind,       offset: 10, size: 1, type: u8 }
      - { name: payload_len,      offset: 11, size: 4, type: u32 }
      - { name: reserved,         offset: 15, size: 65, type: bytes }
  - name: posting_tuple
    tag: 0x21
    fields:
      - { name: tag,              offset: 0, size: 1, type: u8 }
      - { name: heap_pointer,     offset: 1, size: 6, type: item_pointer }
      - { name: payload,          offset: 7, size: payload_len, type: bytes }
```

## Invariants

The clauses the IndexMetadataBlock declaration pins. Each clause owns one
`ocl` fence under its own `### <clauseId>` heading; the fence text is carried
verbatim and never evaluated here.

### FieldsDoNotOverlap

```ocl
context IndexMetadataBlock
inv FieldsDoNotOverlap:
  self.recordTypes->forAll(r | r.fields->forAll(a, b | a <> b implies a.offset + a.size <= b.offset or b.offset + b.size <= a.offset))
```

### DeclaredSizeCoversEveryField

```ocl
context IndexMetadataBlock
inv DeclaredSizeCoversEveryField:
  self.recordTypes->forAll(r | r.size->notEmpty() implies r.fields->forAll(f | f.offset + f.size <= r.size))
```

### MagicIsReadBeforeAnyField

```ocl
context IndexMetadataBlock
inv MagicIsReadBeforeAnyField:
  self.recordTypes->forAll(r | r.magic->notEmpty() implies r.fields->first().offset = 0)
```
