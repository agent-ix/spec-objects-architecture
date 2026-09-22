"""Shared fixtures for the module's test suite.

Two policies are enforced here and nowhere else:

* **The engine is a hard dependency of the semantic rows.** ``quire`` is a
  dev dependency resolved from ``internal-pypi`` (``poetry install``). When
  it is absent the semantic tests **fail**; they never skip, because a skipped
  row is not coverage (FR-005).
* **The emitted schemas are read from the committed tree**, and every
  ``$ref`` to semantic-core resolves against the package the toolchain
  installs, so a record test validates against the real bytes.
"""

from __future__ import annotations

import functools
import hashlib
import json
import pathlib
import re
from typing import Any

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE_ROOT = REPO_ROOT / "spec_objects_architecture"
MANIFEST_PATH = PACKAGE_ROOT / "manifest.yaml"
SCHEMAS_DIR = PACKAGE_ROOT / "schemas"
SKELETONS_DIR = PACKAGE_ROOT / "skeletons"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
NEGATIVE_DIR = FIXTURES_DIR / "negative"
BASELINE_DIR = FIXTURES_DIR / "baseline-0.2.0"
SEMANTIC_CORE_DIR = (
    REPO_ROOT
    / "node_modules"
    / "@agent-ix"
    / "semantic-core"
    / "generated"
    / "json-schema"
)

SEMANTIC_CORE_BASE = "https://schemas.agent-ix.org/semantic-core/0.3.0/"

QUIRE_MISSING = (
    "the Quire wheel exposing `extract_semantic` is not installed in this "
    "environment. Run `poetry install` (quire is a dev dependency from "
    "internal-pypi). The semantic tests fail rather than skip, because a "
    "skipped row is not coverage."
)

OBJECT_TYPES = (
    "api_endpoint",
    "data_schema",
    "queue",
    "action",
    "ui_component",
    "interface",
    "external_contract",
    "extension_point",
    "binary_format",
    "rate_limit",
)

#: The QSpec FR-152 systems-model kinds this module adds as object types
#: (FR-007). `interface` is the fifth kind and is already in OBJECT_TYPES.
SYSTEMS_TYPES = ("part", "port", "connection", "allocation")

#: The five FR-152 kinds, in FR-152's kind-mapping order.
SYSTEMS_KINDS = ("interface", "part", "port", "connection", "allocation")

#: Every exported object type, in manifest `semantic.exports` order.
EXPORTS = OBJECT_TYPES + SYSTEMS_TYPES

#: The quire-rs issue that owns reading `Pre:`/`Post:` operation contract lines.
#: An engine that does not read them extracts no `post` clause reference, so
#: `ExternalContract.json` refuses the external contract skeleton and a dangling
#: `Post:` is never reported.
POST_LINES_ISSUE = "agent-ix/quire-rs#431"
POST_LINES_REASON = (
    "the installed engine does not read `Pre:`/`Post:` as operation contract "
    "lines, so no operation carries a `post` clause reference; "
    f"{POST_LINES_ISSUE}"
)

#: FR-003: an object id is a letter, then letters, digits and underscores.
#: `typespec/main.tsp` states it once as `ObjectId`; the manifest's shared `id`
#: locator carries it as a capturing `regex`.
OBJECT_ID_PATTERN = "^[A-Za-z][A-Za-z0-9_]*$"
OBJECT_ID_LOCATOR_REGEX = "^([A-Za-z][A-Za-z0-9_]*)$"

MODEL_OF = {
    "api_endpoint": "ApiEndpoint",
    "data_schema": "DataSchema",
    "queue": "Queue",
    "action": "Action",
    "ui_component": "UiComponent",
    "interface": "Interface",
    "external_contract": "ExternalContract",
    "extension_point": "ExtensionPoint",
    "binary_format": "BinaryFormat",
    "rate_limit": "RateLimit",
    "part": "Part",
    "port": "Port",
    "connection": "Connection",
    "allocation": "Allocation",
}

SUPPORT_MODELS = (
    "IdentityField",
    "ReturningOperation",
    "GuaranteedOperation",
    "RouteDecl",
    "HttpMethod",
    "DeliveryPolicy",
    "DeliverySemantics",
    "OrderingScope",
    "VersioningPolicy",
    "VersioningScheme",
    "RegistrationPolicy",
    "ConflictPolicy",
    "StabilityPolicy",
    "CompatibilityWindow",
    "RecordLayout",
    "LayoutField",
    "LayoutType",
    "Endianness",
    "Threshold",
    "LimitScope",
    "ExceedResponse",
    "PortDirection",
    "ConnectionDirection",
    "ConnectionEnd",
    "ObjectId",
    "ObjectFrontmatter",
)

#: The optional protocol-profile keys that must stay out of every required list.
PROFILE_KEYS = ("delivery", "versioning", "registration", "stability", "endianness")

KERNEL_SCALARS = (
    "UUID",
    "Boolean",
    "Integer",
    "Decimal",
    "String",
    "Timestamp",
    "Duration",
    "Bytes",
    "JsonObject",
)


def load_manifest() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def manifest_version() -> str:
    return load_manifest()["version"]


def module_base() -> str:
    """The `$id` base, read from the manifest version — never hard-coded
    (FR-002-CON-5)."""
    return (
        "https://schemas.agent-ix.org/agent-ix/spec-objects-architecture/"
        f"{manifest_version()}/"
    )


def object_types() -> list[dict[str, Any]]:
    return load_manifest()["object_types"]


def object_type(name: str) -> dict[str, Any]:
    return next(ot for ot in object_types() if ot["name"] == name)


def locators(ot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    body = ot.get("body_extraction") or {}
    return ((body.get("yield_pattern") or {}).get("match")) or {}


def frontmatter(markdown: str) -> dict[str, Any]:
    match = re.match(r"---\n(.*?)\n---\n", markdown, re.DOTALL)
    assert match, "document has no frontmatter"
    return yaml.safe_load(match.group(1))


def is_systems_skeleton(path: pathlib.Path) -> bool:
    """A skeleton of an FR-007 systems type (FR-005 governs the others)."""
    return path.stem in SYSTEMS_TYPES


def declaration_skeletons() -> list[pathlib.Path]:
    """The FR-005 skeleton set: every shipped skeleton except the four
    systems-model skeletons, which FR-007 governs separately."""
    return [
        path
        for path in sorted(SKELETONS_DIR.glob("*.md"))
        if not is_systems_skeleton(path)
    ]


def systems_skeletons() -> list[pathlib.Path]:
    return [SKELETONS_DIR / f"{name}.md" for name in SYSTEMS_TYPES]


def all_skeletons() -> list[pathlib.Path]:
    return sorted(SKELETONS_DIR.glob("*.md"))


def _extract_probe(markdown: str, kind: str, body_extraction: dict | None = None):
    """Extract a minimal probe document, or `None` when no engine is installed
    (`require_quire` fails those tests by name). Any other engine error
    propagates: a probe never hides a defect unrelated to its feature."""
    try:
        import quire
    except ImportError:
        return None
    request = {
        "markdown": markdown,
        "module": {
            "contractVersion": "1.0.0",
            "semanticCore": load_manifest()["semantic"]["semantic_core"],
            "package": "agent-ix/spec-objects-architecture",
            "exports": [kind],
        },
        "path": f"spec/{kind}.md",
        "bundle": {"package": "agent-ix/spec-objects-architecture"},
    }
    if body_extraction is not None:
        request["bodyExtraction"] = body_extraction
    return quire.extract_semantic(request)


@functools.cache
def engine_reads_post_lines() -> bool:
    """agent-ix/quire-rs#431: the engine reads a `Post:` line under an operation
    as a `post` clause reference."""
    record = _extract_probe(
        "---\nid: probe\ntitle: Probe\ntype: external_contract\n"
        "object: external_contract\n---\n# [probe] Probe\n\n"
        "## Invariants\n\n### Holds\n\n```ocl\ncontext Probe\n"
        "inv Holds:\n  true\n```\n\n## Operations\n\n### run\n\n"
        "Post: Holds\n",
        "external_contract",
    )
    if record is None:  # no engine: `require_quire` fails the row by name
        return True
    return any(op.get("post") for op in record.get("operations") or [])


def post_lines_xfail():
    """A strict xfail on an engine that does not read `Post:` lines."""
    return pytest.mark.xfail(
        condition=not engine_reads_post_lines(), strict=True, reason=POST_LINES_REASON
    )


def validation_gap(path: pathlib.Path) -> str | None:
    """The named defect that keeps a skeleton from validating with the
    installed engine, if any.

    A known defect, not a requirement: FR-005 and FR-007 require every
    skeleton to validate with zero errors. An engine that carries the fix
    (probed, not assumed) has no gap, so the row runs as a plain pass. The
    systems-table (agent-ix/quire-rs#446) and interface `featureOrder`
    (agent-ix/quire-rs#448) lowerings landed on quire-rs main at or after
    `6eec7e8`, published in quire 0.47.1, so those two gaps are gone."""
    if path.stem == "external_contract" and not engine_reads_post_lines():
        return POST_LINES_REASON
    return None


def validation_params(paths: list[pathlib.Path]) -> list:
    """`paths` as pytest params, each known-defect skeleton a strict xfail."""
    params = []
    for path in paths:
        reason = validation_gap(path)
        marks = [pytest.mark.xfail(strict=True, reason=reason)] if reason else []
        params.append(pytest.param(path, id=path.name, marks=marks))
    return params


def sha256_of(path: pathlib.Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def require_quire():
    """Import quire, or fail the test naming the provisioning path."""
    try:
        import quire
    except ImportError as error:
        pytest.fail(f"{QUIRE_MISSING} (import error: {error})")
    if not hasattr(quire, "extract_semantic"):
        pytest.fail(
            f"`extract_semantic` is missing from the installed quire: {QUIRE_MISSING}"
        )
    return quire


@pytest.fixture(scope="session")
def quire_engine():
    return require_quire()


@pytest.fixture(scope="session")
def manifest() -> dict[str, Any]:
    return load_manifest()


@pytest.fixture(scope="session")
def semantic_block(manifest: dict[str, Any]) -> dict[str, Any]:
    return manifest["semantic"]


@pytest.fixture(scope="session")
def semantic_module(semantic_block: dict[str, Any]) -> dict[str, Any]:
    """The `module` block `extract_semantic` takes, derived from the manifest."""
    return {
        "contractVersion": semantic_block["contract_version"],
        "semanticCore": semantic_block["semantic_core"],
        "package": semantic_block["package"],
        "exports": semantic_block["exports"],
        "imports": semantic_block["imports"],
        "compatibilityPosture": semantic_block["compatibility_posture"],
        "legacyForms": semantic_block["legacy_forms"],
    }


@pytest.fixture(scope="session")
def skeletons() -> list[pathlib.Path]:
    """The FR-005 skeleton set (see `declaration_skeletons`)."""
    return declaration_skeletons()


@pytest.fixture(scope="session")
def bundle_index(semantic_block: dict[str, Any]) -> dict[str, Any]:
    """A bundle index built from the skeleton frontmatter (FR-005-AC-3)."""
    objects: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(SKELETONS_DIR.glob("*.md")):
        front = frontmatter(path.read_text())
        if front["id"] in seen:
            continue
        seen.add(front["id"])
        objects.append({"id": front["id"], "names": [front["id"], front["title"]]})
    return {
        "package": semantic_block["package"],
        "objects": objects,
        "enumerations": [],
        "imports": {},
    }


@pytest.fixture(scope="session")
def schema_registry():
    """A 2020-12 validator factory over the shipped schemas plus semantic-core.

    Every `$ref` resolves locally: module models from the committed
    `schemas/` directory, grammar models from the semantic-core package the
    pinned toolchain installs.
    """
    from referencing import Registry, Resource

    if not SEMANTIC_CORE_DIR.is_dir():
        pytest.fail(
            "@agent-ix/semantic-core is not installed, so `$ref`s to the grammar "
            "cannot resolve. Run `make semantic-install` (FR-002-CON-4: `@agent-ix` "
            "resolves from GitHub Packages)."
        )
    resources = []
    for path in sorted(SCHEMAS_DIR.glob("*.json")):
        if path.name == "toolchain.json":
            continue
        schema = json.loads(path.read_text())
        resources.append((schema["$id"], Resource.from_contents(schema)))
    for path in sorted(SEMANTIC_CORE_DIR.glob("*.json")):
        schema = json.loads(path.read_text())
        uri = schema.get("$id") or f"{SEMANTIC_CORE_BASE}{path.name}"
        resources.append((uri, Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)

    def validator_for(model: str):
        from jsonschema import Draft202012Validator

        schema = json.loads((SCHEMAS_DIR / f"{model}.json").read_text())
        return Draft202012Validator(schema, registry=registry)

    return validator_for
