"""Regression guard for the demo benchmark: no probe may ever receive an answer."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_demo_benchmark_has_no_unsupported_answers(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("rb", ROOT / "scripts" / "run_benchmark.py")
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    monkeypatch.setattr(rb, "ROOT", tmp_path)            # don't overwrite the recorded results
    (tmp_path / "diagrams").mkdir()
    s = rb.main(str(ROOT / "data" / "benchmark_demo.json"))["summary"]
    assert s["unsupported_answers"] == 0
    assert s["correct_abstentions"] == s["negative_n"] >= 10
    assert s["wrong_item"] == 0
