"""Shared fixtures for the module's test suite.

Two policies are enforced here and nowhere else:

* **The engine is a hard dependency of the semantic rows.** ``quire`` is not
  declared in ``pyproject.toml`` — no index a repository may commit against
  carries 0.46.0 (``internal-pypi`` serves 0.33.0 at most and no ``quire-rs``
  tag carries the semantic layer), so the wheel is provisioned by
  ``make dev-quire`` and ``agent-ix/quire-rs#392`` is the blocking issue. When
  it is absent the semantic tests **fail**; they never skip, because a skipped
  row is not coverage (FR-005).
* **The emitted schemas are read from the committed tree**, and every
  ``$ref`` to semantic-core resolves against the package the toolchain
  installs, so a record test validates against the real bytes.
"""

from __future__ import annotations

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

SEMANTIC_CORE_BASE = "https://schemas.agent-ix.org/semantic-core/0.1.0/"

QUIRE_MISSING = (
    "the Quire wheel exposing `extract_semantic` is not installed in this "
    "environment. Run `make dev-quire` (agent-ix/quire-rs#392 tracks publishing "
    "0.46.0 to an index this repository may depend on). The semantic tests fail "
    "rather than skip, because a skipped row is not coverage."
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

#: The quire-rs issue that owns lowering the systems tables into the record.
SYSTEMS_EXTRACTION_ISSUE = "agent-ix/quire-rs#446"
SYSTEMS_EXTRACTION_ISSUE_REASON = (
    "the engine yields the systems table but does not lower it into the "
    "record, so the required members are absent and the record fails "
    f"`semantic.record-invalid`; {SYSTEMS_EXTRACTION_ISSUE}"
)
#: FCD #172 adds the `featureOrder` member; the Markdown shape that carries it,
#: and its extraction, are not yet defined.
INTERFACE_FEATURE_ORDER_ISSUE = "agent-ix/filament-core-data#172"
INTERFACE_FEATURE_ORDER_REASON = (
    "Interface.json requires `featureOrder`, and no authored shape or "
    "extraction carries it yet, so the record fails `semantic.record-invalid`; "
    f"{INTERFACE_FEATURE_ORDER_ISSUE}"
)

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
    """The FR-005 skeleton set: every shipped skeleton except the four FR-007
    systems skeletons, whose records the engine cannot yet assemble
    (agent-ix/quire-rs#446)."""
    return [
        path
        for path in sorted(SKELETONS_DIR.glob("*.md"))
        if not is_systems_skeleton(path)
    ]


def systems_skeletons() -> list[pathlib.Path]:
    return [SKELETONS_DIR / f"{name}.md" for name in SYSTEMS_TYPES]


def all_skeletons() -> list[pathlib.Path]:
    return sorted(SKELETONS_DIR.glob("*.md"))


def validation_gap(path: pathlib.Path) -> str | None:
    """The named defect that keeps a skeleton from validating today, if any.

    Each is a known defect, not a requirement: FR-005 and FR-007 require every
    skeleton to validate with zero errors."""
    if is_systems_skeleton(path):
        return SYSTEMS_EXTRACTION_ISSUE_REASON
    if path.stem == "interface":
        return INTERFACE_FEATURE_ORDER_REASON
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
            "cannot resolve. Run `npm ci` (FR-002-CON-4: `@agent-ix` resolves "
            "from npm.ix through the user-level npm config)."
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
