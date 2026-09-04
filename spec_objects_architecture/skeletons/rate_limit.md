---
id: rate-limit-001
title: "ArtifactUploadRateLimit"
type: rate_limit
object: rate_limit
---
<!-- rate_limit authoring skeleton (spec-objects-architecture). Fill every
     section with substantive content. Contract (manifest body_extraction
     asserts):
     - Frontmatter MUST carry id, title, type: rate_limit, object: rate_limit.
     - "## Invariants" (H2): one `### <clauseId>` per clause, each owning
       exactly one ```ocl``` fence. RateLimit.json requires at least one
       clause — this kind exists to pin what happens at the limit.
     - "## Thresholds" (H2, required): the concrete limits, windows, and the
       response when a limit is exceeded.
     - A rate limit declares a policy, not data or calls: RateLimit.json
       forbids `fields` and `operations`, so there is neither a
       "## Properties" nor an "## Operations" section.
     - Keep headings unique per level. -->
# [rate-limit-001] ArtifactUploadRateLimit

## Thresholds

- Per token: 60 uploads per minute, sliding window; excess requests receive
  `429 Too Many Requests` with a `Retry-After` header.
- Per token: 5 GiB uploaded bytes per hour; byte-budget exhaustion also
  returns `429` and resets at the top of the hour.
- Global: 1000 concurrent upload streams across the service; beyond that the
  gateway sheds load with `503 Service Unavailable`.

## Invariants

The clauses the ArtifactUploadRateLimit declaration pins. Each clause owns one
`ocl` fence under its own `### <clauseId>` heading; the fence text is carried
verbatim and never evaluated here.

### ExcessRequestIsRefusedNotQueued

```ocl
context ArtifactUploadRateLimit
inv ExcessRequestIsRefusedNotQueued:
  self.thresholds->forAll(t | t.exceededCount > 0 implies t.onExceeded.status = 429 or t.onExceeded.status = 503)
```

### RetryAfterAccompaniesEveryRefusal

```ocl
context ArtifactUploadRateLimit
inv RetryAfterAccompaniesEveryRefusal:
  self.thresholds->forAll(t | t.onExceeded.status = 429 implies t.onExceeded.retryAfter)
```

### GlobalLimitDominatesPerTokenLimit

```ocl
context ArtifactUploadRateLimit
inv GlobalLimitDominatesPerTokenLimit:
  self.thresholds->select(t | t.scope = LimitScope::global)->forAll(g | self.thresholds->select(t | t.scope = LimitScope::per_token)->forAll(p | p.limit <= g.limit))
```
