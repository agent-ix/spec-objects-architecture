"""Data sink declarations, delivery edges and relation reports (PLAT-1535)."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

import pytest
import yaml

from tests.conftest import (
    DATA_FLOW_MEMBER,
    FIXTURES_DIR,
    PACKAGE_ROOT,
    SCHEMAS_DIR,
    data_flow_relations,
    diagnostic_lines,
    load_manifest,
    module_args,
    object_type,
    run_quire,
    validate_data_flow,
)

CORPUS = FIXTURES_DIR / "data_flow_sinks"
VALID = CORPUS / "valid"
INVALID = CORPUS / "invalid"
SINK_KINDS = (
    "ui_screen",
    "log",
    "export_file",
    "analytics_event",
    "llm_prompt",
    "tool_call",
    "outbound_message",
    "datastore",
)
PROCESSOR_AGREEMENTS = ("covered", "not_covered", "not_applicable", "unknown")


def _flow_module(root: pathlib.Path, rules: list[dict]) -> pathlib.Path:
    module = root / "flow-module"
    shutil.copytree(PACKAGE_ROOT, module)
    manifest_path = module / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest.setdefault("traceability", {})["flow_rules"] = rules
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return module


def _flow_modules(module: pathlib.Path) -> list[str]:
    args = module_args()
    args[-1] = str(module)
    return args


def _flow_report(
    root: pathlib.Path, module: pathlib.Path = PACKAGE_ROOT, *extra: str
) -> subprocess.CompletedProcess:
    return run_quire(
        "relations",
        "--flow",
        "--json",
        *_flow_modules(module),
        "--repo",
        f"{DATA_FLOW_MEMBER}={root}",
        *extra,
    )


def _flow_rule(name: str) -> dict:
    return {
        "name": name,
        "subject": ["data_sink"],
        "match": [
            {"path": [], "field": "processor_agreement", "any_of": ["not_covered"]}
        ],
        "check": name,
        "rationale": "A processor agreement must be authored as covered.",
    }


def _single_sink(root: pathlib.Path, agreement: str) -> None:
    sink_dir = root / "spec/design/sinks"
    sink_dir.mkdir(parents=True)
    (sink_dir / "SINK-1.md").write_text(
        "---\nid: SINK-1\ntitle: Sink\ntype: data_sink\nobject: data_sink\n"
        f"kind: llm_prompt\nprocessor_agreement: {agreement}\n---\n# Sink\n"
    )


@pytest.mark.trace("TC-167", "FR-015-AC-1", "FR-015-AC-2")
def test_every_sink_kind_and_valid_region_validate():
    result = validate_data_flow(VALID)
    assert result.returncode == 0, result.stderr
    for kind in SINK_KINDS:
        assert any(
            f"kind: {kind}" in path.read_text()
            for path in (VALID / "spec/design/sinks").glob("SINK-*.md")
        ), kind


@pytest.mark.trace("TC-168", "FR-015-AC-1", "FR-015-AC-2")
def test_invalid_kind_agreement_and_region_name_the_bad_frontmatter():
    result = validate_data_flow(INVALID, "--strict")
    assert result.returncode == 3, result.stderr
    for name, value in (
        ("SINK-BAD-KIND", "chatbot"),
        ("SINK-MISSING-AGREEMENT", "processor_agreement"),
        ("SINK-BAD-AGREEMENT", "yes"),
        ("SINK-BAD-REGION", "Germany"),
    ):
        assert name in result.stderr, result.stderr
        assert value in result.stderr, result.stderr


@pytest.mark.trace("TC-169", "FR-015-AC-3", "FR-015-AC-4", "FR-015-AC-5")
def test_delivers_to_and_carries_validate_and_refuse_wrong_or_dangling_targets():
    valid = validate_data_flow(VALID)
    assert valid.returncode == 0, valid.stderr

    invalid = validate_data_flow(INVALID, "--strict")
    assert invalid.returncode == 3, invalid.stderr
    edge_errors = diagnostic_lines(invalid, "disallowed-edge-target")
    wrong_delivery = [line for line in edge_errors if "CONN-WRONG-DELIVERY" in line]
    wrong_carries = [line for line in edge_errors if "SINK-WRONG-CARRIES" in line]
    assert len(wrong_delivery) == 1, invalid.stderr
    assert "delivers_to" in wrong_delivery[0] and "'part'" in wrong_delivery[0]
    assert len(wrong_carries) == 1, invalid.stderr
    assert "carries" in wrong_carries[0] and "'queue'" in wrong_carries[0]
    dangling = diagnostic_lines(invalid, "dangling-reference")
    assert any(
        "CONN-DANGLING-DELIVERY" in line and "SINK-MISSING" in line for line in dangling
    )


@pytest.mark.trace("TC-170", "FR-015-AC-6")
def test_relation_report_includes_each_sink_kind_and_authored_processor():
    reports = data_flow_relations(VALID)
    expected = {
        "connection-delivers-to-sink": (
            "CONN-DELIVERS",
            {
                "SINK-UI-SCREEN": "ui_screen",
                "SINK-LOG": "log",
                "SINK-EXPORT": "export_file",
                "SINK-ANALYTICS": "analytics_event",
            },
        ),
        "part-delivers-to-sink": (
            "PART-DELIVERS",
            {
                "SINK-LLM-PROMPT": "llm_prompt",
                "SINK-TOOL-CALL": "tool_call",
                "SINK-MESSAGE": "outbound_message",
                "SINK-DATASTORE": "datastore",
            },
        ),
    }
    for relation, (source_id, sinks) in expected.items():
        rows = reports[relation]["rows"]
        row = next((row for row in rows if row["document"]["id"] == source_id), None)
        assert row is not None, rows
        linked = {entry["id"]: entry for entry in row["linked"]}
        assert set(linked) == set(sinks)
        for sink_id, kind in sinks.items():
            assert linked[sink_id]["record"]["kind"] == kind
            assert "processorAgreement" in linked[sink_id]["record"]

    prompt = next(
        entry
        for row in reports["part-delivers-to-sink"]["rows"]
        for entry in row["linked"]
        if entry["id"] == "SINK-LLM-PROMPT"
    )
    tool_call = next(
        entry
        for row in reports["part-delivers-to-sink"]["rows"]
        for entry in row["linked"]
        if entry["id"] == "SINK-TOOL-CALL"
    )
    assert prompt["record"]["processor"] == "EXT-MODEL-PROVIDER"
    assert tool_call["record"]["processor"] == "PART-SINK-PROCESSOR"


@pytest.mark.trace("FR-015-AC-7")
def test_flow_facts_preserve_each_processor_agreement_value(tmp_path):
    for agreement in ("covered", "unknown", "not_applicable"):
        corpus = tmp_path / agreement
        shutil.copytree(VALID, corpus)
        sink = corpus / "spec/design/sinks/SINK-LLM-PROMPT.md"
        source = sink.read_text()
        sink.write_text(
            source.replace(
                "processor_agreement: not_covered", f"processor_agreement: {agreement}"
            )
        )

        result = _flow_report(corpus)
        assert result.returncode == 0, result.stderr
        facts = json.loads(result.stdout)["facts"]["data_sink"]
        prompt = next(item for item in facts if item["id"] == "SINK-LLM-PROMPT")
        assert prompt["fields"]["processor_agreement"] == agreement


@pytest.mark.trace("FR-015-AC-9")
def test_flow_facts_do_not_infer_undeclared_sinks_fields_or_edges(tmp_path):
    complete_report = _flow_report(VALID)
    assert complete_report.returncode == 0, complete_report.stderr
    for item in json.loads(complete_report.stdout)["facts"]["data_sink"]:
        document = next(yaml.safe_load_all((VALID / item["path"]).read_text()))
        expected_fields = {
            key: document[key]
            for key in (
                "id",
                "kind",
                "processor_agreement",
                "processor",
                "audience_roles",
                "region",
                "purpose",
            )
            if key in document
        }
        assert item["fields"] == expected_fields, item["id"]

    empty = tmp_path / "empty"
    empty.mkdir()
    sink_dir = empty / "spec/design/sinks"
    sink_dir.mkdir(parents=True)
    (empty / "spec/design/sinks/CONN-1.md").write_text(
        "---\nid: CONN-1\ntitle: Connection\ntype: connection\nobject: "
        "connection\n---\n# Connection\n"
    )
    report = _flow_report(empty)
    assert report.returncode == 0, report.stderr
    facts = json.loads(report.stdout)["facts"]
    assert facts["data_sink"] == []
    assert facts["connection"] == [
        {
            "id": "CONN-1",
            "repo": DATA_FLOW_MEMBER,
            "path": "spec/design/sinks/CONN-1.md",
            "fields": {"id": "CONN-1"},
            "edges": [],
        }
    ]

    sparse = tmp_path / "sparse"
    _single_sink(sparse, "unknown")
    report = _flow_report(sparse)
    assert report.returncode == 0, report.stderr
    (sink,) = json.loads(report.stdout)["facts"]["data_sink"]
    assert sink["fields"] == {
        "id": "SINK-1",
        "kind": "llm_prompt",
        "processor_agreement": "unknown",
    }
    assert sink["edges"] == []


@pytest.mark.trace("FR-015-AC-10")
def test_flow_report_is_deterministic_and_strict_tracks_denials(tmp_path):
    corpus = tmp_path / "corpus"
    _single_sink(corpus, "not_covered")
    module = _flow_module(tmp_path, [_flow_rule("sink-agreement")])

    first = _flow_report(corpus, module)
    second = _flow_report(corpus, module)
    assert first.returncode == 0, first.stderr
    assert first.stdout.encode() == second.stdout.encode()
    assert any(
        item["rule"] == "sink-agreement" for item in json.loads(first.stdout)["denials"]
    )
    assert _flow_report(corpus, module, "--strict").returncode == 1

    (corpus / "spec/design/sinks/SINK-1.md").write_text(
        (corpus / "spec/design/sinks/SINK-1.md")
        .read_text()
        .replace("processor_agreement: not_covered", "processor_agreement: covered")
    )
    assert _flow_report(corpus, module, "--strict").returncode == 0


@pytest.mark.trace("FR-015-AC-11")
def test_flow_severity_lowers_only_the_named_rule(tmp_path):
    corpus = tmp_path / "corpus"
    _single_sink(corpus, "not_covered")
    rules = [_flow_rule("sink-agreement-a"), _flow_rule("sink-agreement-b")]
    module = _flow_module(tmp_path, rules)
    manifest_path = module / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["grammar_severity"] = {f"trace:{rule['name']}": "error" for rule in rules}
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    command = [
        "validate",
        "--okf",
        *_flow_modules(module),
        "--repo",
        f"{DATA_FLOW_MEMBER}={corpus}",
        "--severity",
        "trace:sink-agreement-a=warning",
        "--severity",
        "trace:sink-agreement-b=warning",
    ]
    both_warnings = run_quire(*command)
    assert both_warnings.returncode == 0, both_warnings.stdout + both_warnings.stderr
    assert "sink-agreement-a" in both_warnings.stdout + both_warnings.stderr
    assert "sink-agreement-b" in both_warnings.stdout + both_warnings.stderr

    only_one_warning = run_quire(*command[:-2])
    assert only_one_warning.returncode != 0, (
        only_one_warning.stdout + only_one_warning.stderr
    )
    assert "sink-agreement-b" in only_one_warning.stdout + only_one_warning.stderr


@pytest.mark.trace("TC-171", "FR-015-AC-2", "FR-015-AC-12")
def test_data_sink_record_schema_is_closed_and_uses_the_declared_vocabularies(
    schema_registry,
):
    # schema_registry supplies the semantic-core resources for $refs.
    schema = json.loads((SCHEMAS_DIR / "DataSink.json").read_text())
    assert schema["unevaluatedProperties"] == {"not": {}}
    validator = schema_registry("DataSink")
    base = {"kind": "llm_prompt", "processorAgreement": "not_covered"}
    assert validator.is_valid(base)
    assert validator.is_valid(
        {
            **base,
            "processor": "EXT-MODEL-PROVIDER",
            "region": ["DE", "eu"],
            "purpose": ["triage-summary"],
            "audienceRoles": ["triage-agent"],
        }
    )
    for invalid in (
        {**base, "kind": "chatbot"},
        {**base, "processorAgreement": "yes"},
        {**base, "region": ["Germany"]},
        {**base, "purpose": [""]},
        {**base, "purpose": ["   "]},
        {**base, "unknown": True},
    ):
        assert not validator.is_valid(invalid), invalid


@pytest.mark.trace("TC-173", "FR-015-AC-1", "FR-015-AC-2")
def test_data_sink_frontmatter_schema_is_open_and_uses_closed_rule_vocabularies(
    schema_registry,
):
    """Frontmatter keeps optional typed fields open and exposes closed enums.

    Assumptions:
        - The schemas were generated from the TypeSpec source.
        - The schema registry resolves module-local enum references.

    Criteria:
        - Every declared sink kind and agreement value validates.
        - Values outside either enum fail validation.
        - Optional processor, audience_roles, region, and purpose fields accept
          authored values without requiring referenced documents.
        - Additional frontmatter fields remain allowed.
    """
    schema = json.loads((SCHEMAS_DIR / "DataSinkFrontmatter.json").read_text())
    assert schema["unevaluatedProperties"] == {}
    for field in ("processor", "audience_roles", "region", "purpose"):
        assert "$ref" not in schema["properties"][field], field
    assert (
        schema["properties"]["kind"]["enum"]
        == json.loads((SCHEMAS_DIR / "SinkKind.json").read_text())["enum"]
    )
    assert (
        schema["properties"]["processor_agreement"]["enum"]
        == json.loads((SCHEMAS_DIR / "ProcessorAgreement.json").read_text())["enum"]
    )
    validator = schema_registry("DataSinkFrontmatter")
    for kind in SINK_KINDS:
        assert validator.is_valid(
            {"kind": kind, "processor_agreement": "covered", "id": "SINK-1"}
        ), kind
    for agreement in PROCESSOR_AGREEMENTS:
        assert validator.is_valid(
            {"kind": "llm_prompt", "processor_agreement": agreement}
        ), agreement
    assert not validator.is_valid({"kind": "chatbot", "processor_agreement": "covered"})
    assert not validator.is_valid({"kind": "llm_prompt", "processor_agreement": "yes"})

    sink_facts = {
        "kind": "llm_prompt",
        "processor_agreement": "not_covered",
        "processor": "EXT-MODEL-PROVIDER",
        "audience_roles": ["triage-agent"],
        "region": ["US", "eea"],
        "purpose": ["triage-summary"],
    }
    assert validator.is_valid(sink_facts)
    assert validator.is_valid({"kind": "log", "processor_agreement": "not_applicable"})
    for invalid in (
        {**sink_facts, "processor": "bad id"},
        {**sink_facts, "audience_roles": [""]},
        {**sink_facts, "region": ["Germany"]},
        {**sink_facts, "purpose": ["   "]},
        {"processor": "EXT-MODEL-PROVIDER", "processor_agreement": "covered"},
        {"kind": "llm_prompt"},
    ):
        assert not validator.is_valid(invalid), invalid


@pytest.mark.trace("TC-174", "FR-015-AC-8")
def test_flow_rule_loader_resolves_sink_frontmatter_enums(tmp_path):
    """Flow-rule conditions load against sink enums and reject unknown values.

    Assumptions:
        - The installed Quire engine validates flow-rule declarations at load.
        - A module test root reuses the generated frontmatter schema.

    Criteria:
        - Conditions covering every sink kind and agreement value load.
        - An out-of-enum condition value rejects the module and names its value.
    """
    corpus = tmp_path / "corpus"
    documents = corpus / "spec"
    documents.mkdir(parents=True)
    (documents / "sink.md").write_text(
        "---\nid: SINK-1\ntitle: Sink\ntype: data_sink\n"
        "kind: llm_prompt\nprocessor_agreement: covered\n---\n# Sink\n"
    )

    valid_module = tmp_path / "valid-module"
    invalid_module = tmp_path / "invalid-module"
    for root, invalid in ((valid_module, False), (invalid_module, True)):
        schemas = root / "schemas"
        schemas.mkdir(parents=True)
        shutil.copyfile(
            SCHEMAS_DIR / "DataSinkFrontmatter.json",
            schemas / "DataSinkFrontmatter.json",
        )
        agreements = list(PROCESSOR_AGREEMENTS)
        if invalid:
            agreements[-1] = "medical"
        manifest = {
            "name": "data-sink-flow-rule-test",
            "version": "0.1.0",
            "description": "Test the sink frontmatter vocabularies.",
            "archetypes": [
                {
                    "name": "data_sink",
                    "frontmatter_schema_ref": "schemas/DataSinkFrontmatter.json",
                }
            ],
            "traceability": {
                "flow_rules": [
                    {
                        "name": "data-sink-frontmatter-enum-test",
                        "subject": ["data_sink"],
                        "match": [
                            {
                                "path": [],
                                "field": "kind",
                                "any_of": list(SINK_KINDS),
                            },
                            {
                                "path": [],
                                "field": "processor_agreement",
                                "any_of": agreements,
                            },
                        ],
                        "check": "data-sink-frontmatter-enum-test",
                        "rationale": "The test checks the declared sink vocabularies.",
                    }
                ]
            },
        }
        (root / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))

    valid = run_quire(
        "relations",
        "--flow",
        "--json",
        "--module",
        str(valid_module),
        "--repo",
        f"agent-ix/df={corpus}",
    )
    assert valid.returncode == 0, valid.stderr

    invalid = run_quire(
        "relations",
        "--flow",
        "--json",
        "--module",
        str(invalid_module),
        "--repo",
        f"agent-ix/df={corpus}",
    )
    assert invalid.returncode != 0, invalid.stderr
    assert "flow_rules" in invalid.stderr, invalid.stderr


@pytest.mark.trace("TC-172", "FR-015-AC-5", "FR-015-AC-12")
def test_data_sink_is_exported_and_declares_only_the_supported_links():
    manifest = load_manifest()
    assert "data_sink" in manifest["semantic"]["exports"]
    sink = object_type("data_sink")
    assert sink["frontmatter_schema_ref"] == "schemas/DataSinkFrontmatter.json"
    assert sink["allowed_links"] == {
        "carries": ["data_classification"],
        "references": ["part", "external_contract", "role"],
    }
    assert object_type("connection")["allowed_links"]["delivers_to"] == ["data_sink"]
    assert object_type("part")["allowed_links"]["delivers_to"] == ["data_sink"]
    assert manifest["edge_types"]["delivers_to"]["category"] == "dataflow"
