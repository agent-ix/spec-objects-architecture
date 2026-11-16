---
id: sink_001
title: DataSink
type: data_sink
object: data_sink
kind: ui_screen
processor_agreement: unknown
---
# [sink_001] DataSink

A data sink names a place where data is displayed, stored, logged, exported,
aggregated, or sent to another service. The `kind` states the destination form,
and `processor_agreement` records whether the agreement status for a processor
is known to cover this use. Use `unknown` when it has not been assessed.

The optional `processor` names the part or external contract that processes
the data. `region` states known processing locations, `purpose` states the
uses of the data at this sink, and `audience_roles` names roles that can see
it. A source connection or part can declare a `delivers_to` relationship to
this sink. Add `carries` relationships to the data classifications that reach
this sink when the part writes directly to it.
