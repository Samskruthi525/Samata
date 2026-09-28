"""The JSON Schemas in contracts/ must accept what the reference implementation produces."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

from heritage_core import corpus, manifest
from heritage_core.answer_contract import answer, extractive_generator
from heritage_core.retrieval import HybridIndex

ROOT = Path(__file__).resolve().parents[2]


def schema(name):
    s = json.loads((ROOT / "contracts" / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(s)
    return jsonschema.Draft202012Validator(s)


def test_answer_outputs_match_ask_schema():
    v = schema("ask-response.schema.json")
    idx = HybridIndex(corpus.load()["typed_items"])
    for q in corpus.load()["suggested"]:
        v.validate(answer(q, idx, extractive_generator).to_json())
    v.validate(answer("anything", idx, extractive_generator, online=False).to_json())


def test_answered_without_citation_is_invalid():
    v = schema("ask-response.schema.json")
    bad = {"status": "answered", "answer": "x", "answer_kind": "AI_GENERATED_SUMMARY", "citations": []}
    assert not v.is_valid(bad)


def test_manifest_matches_schema():
    v = schema("offline-manifest.schema.json")
    v.validate(manifest.build(corpus.load()["typed_items"], 7, b"test-only-key-not-a-secret",
                              issued=datetime(2026, 9, 26, tzinfo=timezone.utc)))


def test_design_doc_ingest_example_matches_schema():
    v = schema("ingest-manifest.schema.json")
    example = json.loads((ROOT / "contracts" / "examples" / "ingest-demo-item-001.json").read_text(encoding="utf-8"))
    v.validate(example)
    assert example["rights"]["public_display"] is False
