---
id: negative_007
title: "LimitWithoutInvariants"
type: rate_limit
object: rate_limit
expect: semantic.record-invalid
because: "RateLimit.json requires at least one clause pinning what happens at the limit"
---
# [negative_007] LimitWithoutInvariants

## Thresholds

- Per token: 60 uploads per minute, sliding window.
- Global: 1000 concurrent upload streams across the service.
