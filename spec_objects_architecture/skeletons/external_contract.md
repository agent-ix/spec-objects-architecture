---
id: external-contract-001
title: "IdentityServiceContract"
type: external_contract
object: external_contract
---
<!-- external_contract authoring skeleton (spec-objects-architecture). Fill
     every section with substantive content. Contract (manifest
     body_extraction asserts):
     - Frontmatter MUST carry id, title, type: external_contract,
       object: external_contract.
     - "## Operations" (H2): one `### <name>` per operation. ExternalContract
       .json requires at least one operation whose `Post:` line names a clause
       declared in this artifact — the guarantee the external party makes.
     - "## Invariants" (H2): one `### <clauseId>` per clause, each owning
       exactly one ```ocl``` fence. ExternalContract.json requires at least
       one clause: this kind exists to pin guarantees.
     - "## Contract" (H2, required): the contract with the EXTERNAL system —
       what it provides/expects, invariants, versioning expectations.
     - "## Endpoints" (H2, optional): concrete surface consumed/exposed.
     - "## Behavior" (H2, optional): interaction semantics, failure modes.
     - Boundary: contracts WITHIN the system are `interface` objects;
       this kind is for systems outside it (vendors, peer services whose
       contract this repo does not own).
     - An external contract declares calls and guarantees, not state:
       ExternalContract.json forbids `fields`, so there is no
       "## Properties" section.
     - Keep headings unique per level. -->
# [external-contract-001] IdentityServiceContract

## Contract

The auth-service consumes the Identity service as its sole source of user
credential validation and user lookup. Identity guarantees: `tenant_id` is the
canonical isolation boundary; user status transitions follow the published
lifecycle; breaking response-shape changes bump the internal API version
header. The auth-service guarantees it never caches credential-validation
verdicts beyond a single request.

## Endpoints

- `POST /auth/internal/authenticate` — validate username/password credentials
- `GET /auth/internal/lookup/{user_id}` — fetch user profile by id

## Behavior

- Credential validation is fail-closed: any non-200 response is treated as a
  rejection; timeouts surface as 503 to the caller, never as auth success.
- User lookups tolerate eventual consistency up to 5 s after a mutation.

## Invariants

The clauses the IdentityServiceContract declaration pins. Each clause owns one
`ocl` fence under its own `### <clauseId>` heading; the fence text is carried
verbatim and never evaluated here.

### CredentialValidationIsFailClosed

```ocl
context IdentityServiceContract
inv CredentialValidationIsFailClosed:
  self.lastResponseStatus <> 200 implies not self.lastVerdictAccepted
```

### TenantIsTheIsolationBoundary

```ocl
context IdentityServiceContract
inv TenantIsTheIsolationBoundary:
  self.lookupResults->forAll(r | r.tenantId = self.requestedTenantId)
```

## Operations

The operations the IdentityServiceContract declaration covers. Each operation
owns one `### <name>` heading with its parameter table, a `Returns:` line
where it answers with a value, and a `Post:` line naming the guarantee the
external party makes.

### authenticate

Validate a username and password pair against the Identity service and answer
whether the credentials are accepted.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| tenant_id | UUID | 1..1 | |
| username | String | 1..1 | minLength: 1 |
| password | String | 1..1 | minLength: 1 |

Returns: Boolean[1..1]

Post: CredentialValidationIsFailClosed

### lookup_user

Fetch one user's profile by id, tolerating up to five seconds of replication
lag after a mutation.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| tenant_id | UUID | 1..1 | |
| user_id | UUID | 1..1 | |

Returns: JsonObject[0..1]

Post: TenantIsTheIsolationBoundary
