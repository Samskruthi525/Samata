#!/usr/bin/env python3
"""Run a benchmark file through the reference retrieval + answer contract and record the results.

Usage: python scripts/run_benchmark.py [data/benchmark_demo.json]
Writes diagrams/benchmark_results.json (embedded in README §52.3 via <!-- GEN:benchmark -->).
Answerable questions: retrieval Hit@5 / RR against labelled passages, and whether the answer cites a labelled passage.
Unanswerable / misattribution probes: the only correct outcome is a non-answer.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))
from heritage_core import corpus  # noqa: E402
from heritage_core.answer_contract import answer, extractive_generator  # noqa: E402
from heritage_core.retrieval import HybridIndex  # noqa: E402


def is_rel(passage_id: str, item_id: str, relevant: list[str]) -> bool:
    return passage_id in relevant or f"ITEM:{item_id}" in relevant


def main(path: str) -> dict:
    bench = json.loads(Path(path).read_text(encoding="utf-8"))
    items = corpus.load()["typed_items"]
    idx = HybridIndex(items)
    pid_item = {p.id: it.id for it in items.values() for p in it.passages}
    rows = []
    for q in bench["questions"]:
        hits = idx.search(q["text"], k=5)
        rank = next((r for r, h in enumerate(hits, 1) if is_rel(h.passage.id, h.passage.item_id, q["relevant"])), None)
        a = answer(q["text"], idx, extractive_generator)
        cited = [c.excerpt_id for c in a.citations]
        cited_ok = any(is_rel(c.excerpt_id, c.item_id, q["relevant"]) for c in a.citations)
        rel_items = {pid_item.get(r, r.removeprefix("ITEM:")) for r in q["relevant"]}
        same_item = any(c.item_id in rel_items for c in a.citations)
        if q["answerable"]:
            outcome = ("correct" if a.status == "answered" and cited_ok else
                       "false_abstention" if a.status != "answered" else
                       "other_passage_same_item" if same_item else "wrong_item")
        else:
            outcome = "correct_abstention" if a.status != "answered" else "UNSUPPORTED_ANSWER"
        rows.append({"id": q["id"], "bucket": q["bucket"], "text": q["text"], "status": a.status,
                     "cited": cited, "rank": rank, "rr": (1 / rank) if rank else 0.0, "outcome": outcome,
                     "reason": a.reason})
    ans = [r for r in rows if r["bucket"] == "answerable"]
    neg = [r for r in rows if r["bucket"] != "answerable"]
    summary = {
        "answerable_n": len(ans),
        "hit@5": round(sum(1 for r in ans if r["rank"]) / len(ans), 3),
        "mrr": round(sum(r["rr"] for r in ans) / len(ans), 3),
        "answered_with_labelled_citation": sum(1 for r in ans if r["outcome"] == "correct"),
        "false_abstentions": sum(1 for r in ans if r["outcome"] == "false_abstention"),
        "other_passage_same_item": sum(1 for r in ans if r["outcome"] == "other_passage_same_item"),
        "wrong_item": sum(1 for r in ans if r["outcome"] == "wrong_item"),
        "negative_n": len(neg),
        "correct_abstentions": sum(1 for r in neg if r["outcome"] == "correct_abstention"),
        "unsupported_answers": sum(1 for r in neg if r["outcome"] == "UNSUPPORTED_ANSWER"),
    }
    out = {"benchmark_version": bench["benchmark_version"], "summary": summary, "rows": rows}
    (ROOT / "diagrams" / "benchmark_results.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    res = main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "benchmark_demo.json"))
    print(json.dumps(res["summary"], indent=1))
    for r in res["rows"]:
        print(f'{r["id"]} {r["bucket"]:<14} {r["status"]:<13} rank={r["rank"]} {r["outcome"]:<20} {r["cited"]} {r["reason"]}')
