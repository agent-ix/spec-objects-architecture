---
id: negative-006
title: "ContractWithoutGuarantees"
type: external_contract
object: external_contract
expect: semantic.record-invalid
because: "ExternalContract.json requires at least one clause: this kind exists to pin guarantees"
---
# [negative-006] ContractWithoutGuarantees

## Contract

The service consumes a third-party geocoder and states no guarantee about it,
which is what makes this record invalid.

## Operations

### geocode

Resolve a postal address to coordinates.

| Param | Type | Multiplicity | Constraints |
|---|---|---|---|
| address | String | 1..1 | minLength: 1 |

Returns: JsonObject[0..1]
