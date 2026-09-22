---
type: log
title: "Update Log"
description: "Chronological log of structural changes to this bundle."
---
# Update Log

## History

* **2026-06-15** — Adopted OKF-compatible bundle structure with directory indexes.
* **2026-09-04** — Added the semantic-module contract (issue #8): US-001, FR-002..FR-006, NFR-001, IT-002, and the `usecase/` and `non-functional/` directories.
* **2026-09-17** — Added FR-007, the systems-model kinds (issue #10), and bumped the manifest to 0.4.0.
* **2026-09-22** — PLAT-974: CI off the dev mirrors. `quire` is now a committed dev dependency pinned to `internal-pypi` (0.47.1) — `agent-ix/quire-rs#392` is resolved, the `make dev-quire` target and the `local-pypi` poetry source are deleted, and FR-005 states the dependency rather than the blocker. `@agent-ix/semantic-core` resolves from GitHub Packages (`npm.pkg.github.com`) instead of the dev-only `npm.ix` mirror, so `.github/workflows/ci.yml` moves from `lib-ci.yml` to `semantic-module-ci.yml` and a new `make semantic-install` target (`npm ci`) replaces the local-npm-config assumption FR-002-CON-4 used to name. Quire 0.47.1 (built from quire-rs main at or after `6eec7e8`) carries the fixes that used to need a conditional probe and a strict expected failure: the systems tables lower into the record (`agent-ix/quire-rs#446`, FR-007-AC-7), the interface `## Features` table lowers into `featureOrder` (`agent-ix/quire-rs#448`, FR-003-AC-4, FR-005-AC-1, FR-007-AC-11), and `ModelFeature::Generalization` gates a `specializes` relationship on the `generalization` mapping (`agent-ix/quire-rs#463`, FR-007-AC-12) — the `engine_lowers_systems_tables`, `engine_lowers_feature_order`, and `engine_gates_generalization_mapping` probes and their xfail markers are deleted from `tests/conftest.py`, and FR-007's coverage status moves from `🚧` to `✅`.
