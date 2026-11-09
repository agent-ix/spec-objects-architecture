---
id: rate_limit_001
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
     - "## Thresholds" (H2, required): one table
       `Scope | Metric | Limit | Window | Status | Retry After | Behavior`,
       one row per limit. `Status` is the HTTP status answered when the limit
       is exceeded and is required; `Retry After` is `true` or `false`;
       `Behavior` is optional prose (FR-008).
     - A rate limit declares a policy, not data or calls: RateLimit.json
       forbids `fields` and `operations`, so there is neither a
       "## Properties" nor an "## Operations" section.
     - Keep headings unique per level. -->
# [rate_limit_001] ArtifactUploadRateLimit

## Thresholds

| Scope | Metric | Limit | Window | Status | Retry After | Behavior |
|---|---|---|---|---|---|---|
| per_token | uploads | 60 | 1m | 429 | true | sliding window |
| per_token | uploaded_bytes | 5368709120 | 1h | 429 | true | resets at the top of the hour |
| global | concurrent_streams | 1000 | 1m | 503 | false | the gateway sheds load |

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
