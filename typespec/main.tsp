import "@typespec/json-schema";
import "@agent-ix/semantic-core";

using TypeSpec.JsonSchema;
using AgentIx.Semantic.Core;

/**
 * Tier-2 architecture object declaration schemas (agent-ix/spec-objects-architecture#8).
 *
 * One model per architecture object type this module contributes, each
 * validating that type's Quire declaration record (fields, relations, clauses,
 * operations; quire-rs FR-070..FR-072) with type-specific required keys,
 * forbidden keys, and item rules (FR-004). Every grammar item is a `$ref` to
 * `@agent-ix/semantic-core` 0.1.0 and is never redeclared here (FR-004-CON-1);
 * this namespace contributes archetype shapes only.
 *
 * The `$id` base embeds the manifest `version` by intent (FR-002-CON-5): one
 * schema URL names exactly one immutable byte sequence, so a downstream fixture
 * reader that pinned a version can never silently read later bytes. A bump edits
 * this base and `manifest.yaml`'s `version` in one commit and re-runs
 * `make schemas`.
 */
@jsonSchema("https://schemas.agent-ix.org/agent-ix/spec-objects-architecture/0.3.0/")
namespace AgentIx.SpecObjects.Architecture;

// ---------------------------------------------------------------------------
// Open marker models (used only as `@contains` predicates)
// ---------------------------------------------------------------------------

/**
 * Open marker: a `FieldDecl` flagged as identity. Deliberately open so it
 * matches any identity-flagged field.
 */
model IdentityField {
  identity: true;
}

/** Open marker: an `OperationDecl` that declares a return value. */
model ReturningOperation {
  returns: TypeRef;
}

/**
 * Open marker: an `OperationDecl` carrying at least one postcondition — the
 * guarantee shape an external contract exists to pin.
 */
model GuaranteedOperation {
  @minItems(1) post: ClauseRef[];
}

// ---------------------------------------------------------------------------
// Closed architecture vocabularies
// ---------------------------------------------------------------------------

/** HTTP methods a route may declare. */
enum HttpMethod {
  GET,
  POST,
  PUT,
  PATCH,
  DELETE,
  HEAD,
  OPTIONS,
}

/** Message-delivery guarantee of a queue. */
enum DeliverySemantics {
  at_most_once,
  at_least_once,
  exactly_once,
}

/** Scope over which a queue preserves message order. */
enum OrderingScope {
  none,
  partition,
  global,
}

/** How an external contract signals a change. */
enum VersioningScheme {
  semver,
  date,
  header,
  none,
}

/** What an extension point does with a duplicate registration. */
enum ConflictPolicy {
  last_wins,
  first_wins,
  error,
}

/** The compatibility window an extension point offers implementers. */
enum CompatibilityWindow {
  major,
  minor,
  none,
}

/** Physical field types a binary layout may declare. */
enum LayoutType {
  u8,
  u16,
  u32,
  u64,
  i8,
  i16,
  i32,
  i64,
  f32,
  f64,
  bytes,
  item_pointer,
}

/** Byte order of a persisted binary layout. */
enum Endianness {
  little,
  big,
}

/** The population a rate-limit threshold applies to. */
enum LimitScope {
  per_token,
  per_tenant,
  per_ip,
  global,
}

// ---------------------------------------------------------------------------
// Architecture value models
// ---------------------------------------------------------------------------

/**
 * One concrete route of an API endpoint.
 *
 * Reader rule JSON Schema cannot express (FR-004): `operation` names an
 * `operations[].name` of the same record. It is stated for the extractor that
 * first populates `routes` and is not claimed as a schema refusal.
 */
model RouteDecl {
  method: HttpMethod;

  @minLength(1) path: string;

  operation: Identifier;
  ...Record<never>;
}

/** The delivery guarantee profile of a queue. */
model DeliveryPolicy {
  semantics: DeliverySemantics;
  ordering?: OrderingScope;
  retention?: string;
  ...Record<never>;
}

/** The change-signalling profile of an external contract. */
model VersioningPolicy {
  scheme: VersioningScheme;
  breaking_change_signal?: string;
  ...Record<never>;
}

/** How implementations register against an extension point. */
model RegistrationPolicy {
  mechanism: Identifier;
  conflict: ConflictPolicy;
  discovery?: string;
  ...Record<never>;
}

/** The compatibility guarantee an extension point offers. */
model StabilityPolicy {
  compatibility: CompatibilityWindow;
  deprecation_window?: string;
  ...Record<never>;
}

/**
 * One physical field of a binary record.
 *
 * A `size` naming an `Identifier` names a sibling field of the same record
 * whose value carries the length; that cross-reference is a reader rule.
 */
model LayoutField {
  name: Identifier;

  @minValue(0) offset: int32;

  size: uint32 | Identifier;

  type: LayoutType;
  ...Record<never>;
}

/** One record type of a persisted binary layout. */
model RecordLayout {
  name: Identifier;
  tag?: string;

  @minValue(0) size?: int32;

  @minItems(1) fields: LayoutField[];

  ...Record<never>;
}

/** What a service does when a rate-limit threshold is exceeded. */
model ExceedResponse {
  @minValue(100)
  @maxValue(599)
  status: int32;

  retry_after?: boolean;
  behavior?: string;
  ...Record<never>;
}

/** One rate-limit threshold. */
model Threshold {
  scope: LimitScope;
  metric: Identifier;

  @minValue(0) limit: float64;

  @minLength(1) window: string;

  on_exceeded: ExceedResponse;
  ...Record<never>;
}

// ---------------------------------------------------------------------------
// Object-type declaration records
// ---------------------------------------------------------------------------

/**
 * A network-addressable endpoint. It declares operations, not data: `fields`
 * is forbidden by the seal, and at least one operation answers with a record.
 */
model ApiEndpoint {
  @minItems(1)
  @contains(ReturningOperation)
  operations: OperationDecl[];

  routes?: RouteDecl[];
  clauses?: ClauseRef[];
  relations?: RelationDecl[];
  requires?: SemanticId[];
  ...Record<never>;
}

/**
 * A record shape other objects reference by `TypeRef`. It declares data, not
 * behaviour: `operations` is forbidden by the seal.
 */
model DataSchema {
  @minItems(1)
  fields: FieldDecl[];

  clauses?: ClauseRef[];
  relations?: RelationDecl[];
  ...Record<never>;
}

/**
 * A message queue. Its `fields` are the message envelope, one of which is the
 * partition key, so at least one is an identity field. `operations` and
 * `relations` are forbidden by the seal: a queue carries messages, it does not
 * expose calls.
 */
model Queue {
  @minItems(1)
  @contains(IdentityField)
  fields: FieldDecl[];

  delivery?: DeliveryPolicy;
  carries?: SemanticId[];
  clauses?: ClauseRef[];
  ...Record<never>;
}

/**
 * One invokable behaviour. Exactly one operation: an action that declared two
 * invocations would be a process. `fields` is forbidden by the seal.
 */
model Action {
  @minItems(1)
  @maxItems(1)
  operations: OperationDecl[];

  clauses?: ClauseRef[];
  relations?: RelationDecl[];
  triggers?: SemanticId[];
  ...Record<never>;
}

/**
 * A UI component. Its `fields` are props, which carry no identity of their
 * own — identity belongs to the record a prop references.
 */
model UiComponent {
  @minItems(1)
  @contains(IdentityField)
  @minContains(0)
  @maxContains(0)
  fields: FieldDecl[];

  operations?: OperationDecl[];
  clauses?: ClauseRef[];
  relations?: RelationDecl[];
  renders?: SemanticId[];
  ...Record<never>;
}

/**
 * A contract within the system: the operations a component exposes or depends
 * on. `fields` is forbidden by the seal — an interface declares calls, not
 * state.
 */
model Interface {
  @minItems(1)
  operations: OperationDecl[];

  associated_types?: TypeRef[];
  clauses?: ClauseRef[];
  relations?: RelationDecl[];
  ...Record<never>;
}

/**
 * A contract with a system outside this one. It exists to pin guarantees, so it
 * carries at least one clause and at least one operation with a postcondition.
 * `fields` is forbidden by the seal.
 */
model ExternalContract {
  @minItems(1)
  @contains(GuaranteedOperation)
  operations: OperationDecl[];

  @minItems(1)
  clauses: ClauseRef[];

  provider?: SemanticId;
  versioning?: VersioningPolicy;
  relations?: RelationDecl[];
  ...Record<never>;
}

/**
 * Pluggability as a first-class node: the operations third-party implementers
 * write against, plus the stability guarantee they rely on. `fields` and
 * `relations` are forbidden by the seal.
 */
model ExtensionPoint {
  @minItems(1)
  operations: OperationDecl[];

  @minItems(1)
  clauses: ClauseRef[];

  exposes?: SemanticId;
  registration?: RegistrationPolicy;
  stability?: StabilityPolicy;
  ...Record<never>;
}

/**
 * A persisted binary layout — offsets, strides and endianness JSON Schema has
 * no vocabulary for. It exists to pin layout invariants, so it carries at least
 * one clause; `fields` and `operations` are forbidden by the seal.
 */
model BinaryFormat {
  @minItems(1)
  clauses: ClauseRef[];

  records?: RecordLayout[];
  endianness?: Endianness;
  serializes?: SemanticId[];
  ...Record<never>;
}

/**
 * A throttling policy. It exists to pin what happens at the limit, so it
 * carries at least one clause; `fields` and `operations` are forbidden by the
 * seal.
 */
model RateLimit {
  @minItems(1)
  clauses: ClauseRef[];

  thresholds?: Threshold[];
  throttles?: SemanticId[];
  ...Record<never>;
}
