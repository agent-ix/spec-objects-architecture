---
id: extension-point-001
title: "RendererRegistryExtension"
type: extension_point
object: extension_point
---
<!-- extension_point authoring skeleton (spec-objects-architecture). Fill
     every section with substantive content. Contract (manifest
     body_extraction asserts):
     - Frontmatter MUST carry id, title, type: extension_point,
       object: extension_point.
     - "## Operations" (H2): the operations third-party implementers write
       against. ExtensionPoint.json requires at least one.
     - "## Invariants" (H2): one `### <clauseId>` per clause, each owning
       exactly one ```ocl``` fence. ExtensionPoint.json requires at least one
       clause — the stability guarantee implementers rely on.
     - "## Contract" (H2, required): the interface the extension point
       exposes to plug-ins (name the `interface` object it publishes).
     - "## Registration" (H2, optional): how implementations register and
       are discovered/selected.
     - "## Stability" (H2, optional): compatibility window, versioning and
       deprecation guarantees offered to third-party implementers.
     - Use this kind only when pluggability itself needs to be a node
       (external authors, compatibility guarantees); an internal contract
       with known implementations is just an `interface` plus
       `implements` edges.
     - ExtensionPoint.json forbids `fields`, so there is no
       "## Properties" section.
     - Keep headings unique per level. -->
# [extension-point-001] RendererRegistryExtension

## Contract

Modules contribute object renderers through the `RendererRegistry` interface
(interface-002): per `object_type_name`, a module registers the React
component and configuration this library needs to render that type — with no
modification to the host library's source.

## Registration

- Registration happens at module init via `registry.register(typeName, entry)`.
- Last registration per `object_type_name` wins; duplicate registrations log a
  warning with both module names.
- Unregistered types fall back to the generic payload renderer.

## Stability

- The registry entry shape is semver-stable within a major version; new
  optional fields may be added in minors.
- Deprecated fields keep working for one major version and log a deprecation
  warning naming the replacement.

## Invariants

The clauses the RendererRegistryExtension declaration pins. Each clause owns
one `ocl` fence under its own `### <clauseId>` heading; the fence text is
carried verbatim and never evaluated here.

### LastRegistrationWinsPerType

```ocl
context RendererRegistryExtension
inv LastRegistrationWinsPerType:
  self.entries->forAll(e | self.resolve(e.typeName) = self.entries->last())
```

### DeprecatedFieldsSurviveOneMajor

```ocl
context RendererRegistryExtension
inv DeprecatedFieldsSurviveOneMajor:
  self.deprecatedFields->forAll(f | f.removedInMajor > f.deprecatedInMajor)
```

## Operations

The operations the RendererRegistryExtension declaration exposes to plug-in
authors. Each operation owns one `### <name>` heading with its parameter table
and a `Returns:` line where it answers with a value.

### register

Register one renderer entry for an object type at module init; the last
registration for a given type wins.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| type_name | String | 1..1 | minLength: 1 |
| entry | JsonObject | 1..1 | |

Post: LastRegistrationWinsPerType

### resolve

Answer the renderer entry currently registered for an object type, or nothing
when the type falls back to the generic payload renderer.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| type_name | String | 1..1 | minLength: 1 |

Returns: JsonObject[0..1]
