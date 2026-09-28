#!/usr/bin/env python3
"""Data-driven Markdown tables injected into README.md at build time.

build_readme.py replaces every  <!-- GEN:<name> -->  marker with TABLES[name]().
Keeps README tables in sync with data/demo_corpus.json and diagrams/computed_metrics.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "data" / "demo_corpus.json").read_text(encoding="utf-8"))
M_PATH = ROOT / "diagrams" / "computed_metrics.json"

KIND = {"writing": "Writings & speeches", "constitutional": "Constitutional records",
        "manuscript_photo": "Manuscripts & photographs", "media": "Audio & video", "interpretive": "Interpretive"}


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def items():
    rows = ["| ID | Category | Title | Date label | Language | Source (register ref) | Rights | Status | Offline | Badges | Evidence units |",
            "|---|---|---|---|---|---|---|---|:---:|---|:---:|"]
    for i in D["items"]:
        units = sum(len(p.get("passages", [])) for p in i.get("pages", [])) + len(i.get("segments", []))
        kind = "pages" if i.get("pages") else "segments" if i.get("segments") else "-"
        rows.append(f"| `{i['id']}` | {KIND[i['kind']]} | {esc(i['title'])} | {esc(i['dateLabel'])} | {esc(i.get('language', '-'))} | "
                    f"{esc(i['sourceName'])} ({i['sourceRef']}) | `{i['rights']}` | `{i.get('status', 'published')}` | "
                    f"{'✓' if i.get('cached') else '-'} | {', '.join(i['badges'])} | {units} {kind if units else ''} |")
    return "\n".join(rows)


def passages():
    rows = ["| Passage ID | Item | Printed page | PDF index | Citable | Curator note (from prototype) |",
            "|---|---|---|---:|:---:|---|"]
    for i in D["items"]:
        for p in i.get("pages", []):
            for ps in p.get("passages", []):
                rows.append(f"| `{ps['id']}` | `{i['id']}` | {esc(p.get('printed'))} | {p.get('pdf')} | {'✓' if ps.get('cite') else '-'} | {esc(ps.get('note', ''))} |")
    return "\n".join(rows)


def segments():
    rows = ["| Item | Start | Duration | Speaker | Text (demo) |", "|---|---:|---:|---|---|"]
    for i in D["items"]:
        for s in i.get("segments", []):
            rows.append(f"| `{i['id']}` | {s['ms'] / 1000:.0f} s | {s.get('dur', 0) / 1000:.0f} s | {esc(s.get('speaker', '-'))} | {esc(s['text'])} |")
    return "\n".join(rows)


def events():
    rows = ["| Event ID | Date | Title | Category | Evidence (relation → item [page/passage]) |", "|---|---|---|---|---|"]
    for e in D["events"]:
        ev = "; ".join(f"{x['rel']} → `{x['item']}`" + (f" p{x['page']}" if 'page' in x else "") +
                       (f" `{x['passage']}`" if x.get('passage') else "") for x in e.get("evidence", []))
        rows.append(f"| `{e['id']}` | {esc(e['date'])} | {esc(e['title'])} | {KIND.get(e['kind'], e['kind'])} | {ev} |")
    return "\n".join(rows)


def km():
    nodes = {n["id"]: n for n in D["km_nodes"]}
    rows = ["| From | Relation | To | To-node type |", "|---|---|---|---|"]
    for e in D["km_edges"]:
        a, b = nodes.get(e["from"]), nodes.get(e["to"])
        rows.append(f"| {' '.join(a['lines']) if a else e['from']} | `{e['rel']}` | {' '.join(b['lines']) if b else e['to']} | {b['type'] if b else '?'} |")
    return "\n".join(rows)


def stories():
    rows = ["| Story | Subtitle | Stops |", "|---|---|---|"]
    for s in D["stories"]:
        rows.append(f"| **{esc(s['title'])}** (`{s['id']}`) | {esc(s['sub'])} | " +
                    " → ".join(f"{esc(t['date'])}: {esc(t['title'])}" for t in s["stops"]) + " |")
    return "\n".join(rows)


def tests():
    where = {"hw": "Physical Pi", "demo": "HTML demo (Run button)", "corpus": "Test corpus", "be": "Backend"}
    rows = ["| Test ID | Procedure | Pass criterion | Executable in | Observed result | Date / tester |", "|---|---|---|---|---|---|"]
    for t in D["tests"]:
        rows.append(f"| **{t['id']}** | {esc(t['procedure'])} | {esc(t['pass'])} | {where[t['mode']]} | *not yet recorded* | |")
    return "\n".join(rows)


def asks():
    rows = ["| Route keys (prototype matches any) | Cited passages |", "|---|---|"]
    for a in D["ask_set"]:
        rows.append(f"| {', '.join('`' + k + '`' for k in a['keys'])} | " +
                    ", ".join(f"`{c['item']}` {('`' + c['passage'] + '`') if c.get('passage') else '(whole media item)'} ({esc(c.get('label', ''))})" for c in a["cites"]) + " |")
    return "\n".join(rows)


def ocr():
    m = json.loads(M_PATH.read_text(encoding="utf-8"))
    rows = ["| Page | CER | WER |", "|---|---:|---:|"]
    for r in m["ocr"]:
        rows.append(f"| {r['page']} | {r['cer'] * 100:.1f} % | {r['wer'] * 100:.1f} % |")
    return "\n".join(rows)


def retrieval():
    m = json.loads(M_PATH.read_text(encoding="utf-8"))["retrieval"]
    qs = [x["q"] for x in m["lexical"]["per_query"]]
    rows = ["| Query | Lexical RR | Dense RR | Hybrid RR |", "|---|---:|---:|---:|"]
    for i, q in enumerate(qs):
        rows.append(f"| `{q}` | " + " | ".join(f"{m[k]['per_query'][i]['rr']:.2f}" for k in ("lexical", "dense", "hybrid")) + " |")
    rows.append("| **Hit@5 (mean)** | " + " | ".join(f"**{m[k]['hit@5']:.3f}**" for k in ("lexical", "dense", "hybrid")) + " |")
    rows.append("| **MRR (mean)** | " + " | ".join(f"**{m[k]['mrr']:.3f}**" for k in ("lexical", "dense", "hybrid")) + " |")
    return "\n".join(rows)


def _first_section(fname):
    import re
    for part in sorted((ROOT / "readme_src").glob("*.md")):
        sec = None
        for line in part.read_text(encoding="utf-8").splitlines():
            m = re.match(r"## (\d+\. .+|Appendix [A-Z]: .+)$", line)
            if m:
                sec = m.group(1)
            if fname in line and sec and "GEN:figures" not in line:
                return sec
    return "—"


def figures():
    rows = ["| File | Kind | First used in |", "|---|---|---|"]
    for f in sorted((ROOT / "diagrams").glob("*.png")):
        rows.append(f"| [`diagrams/{f.name}`](diagrams/{f.name}) | Python (matplotlib) | {esc(_first_section(f.name))} |")
    for f in sorted((ROOT / "docs" / "screenshots").glob("*.png")):
        rows.append(f"| [`docs/screenshots/{f.name}`](docs/screenshots/{f.name}) | Headless-Chromium capture of the prototype | {esc(_first_section(f.name))} |")
    return "\n".join(rows)


def strings():
    i18n = json.loads((ROOT / "data" / "i18n_strings.json").read_text(encoding="utf-8"))
    en = i18n["en"]
    langs = [l for l in ("en", "hi", "mr", "te") if l in i18n]
    groups = {}
    import re
    for k in en:
        g = k.split("_")[0] if "_" in k else k
        g = re.sub(r"\d+$", "#", g)          # d1..d9 -> d#, era1..era5 -> era#
        groups.setdefault(g, []).append(k)
    single = [k for g, ks in groups.items() if len(ks) == 1 for k in ks]
    groups = {g: ks for g, ks in groups.items() if len(ks) > 1}
    if single:
        groups["(single-key labels)"] = single
    rows = ["| Key prefix | Keys | Example key | English text (example) | " + " | ".join(l.upper() for l in langs) + " |",
            "|---|---:|---|---|" + "---:|" * len(langs)]
    for g, ks in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0])):
        ex = ks[0]
        txt = re.sub(r"<[^>]+>", "", str(en[ex])).replace("\n", " ")
        txt = txt if len(txt) <= 70 else txt[:67] + "…"
        cov = " | ".join(f"{sum(1 for k in ks if k in i18n[l])}/{len(ks)}" for l in langs)
        gl = g if g.startswith("(") else f"`{g}`"
        rows.append(f"| {gl} | {len(ks)} | `{ex}` | {esc(txt)} | {cov} |")
    rows.append(f"| **Total** | **{len(en)}** | | | " + " | ".join(f"**{len(i18n[l])}/{len(en)}**" for l in langs) + " |")
    return "\n".join(rows)


def credits():
    rows = ["| Image key | Depicts (alt text) | Credit line as embedded in the prototype | Status for public reuse |", "|---|---|---|---|"]
    for c in D.get("image_credits", []):
        cr = c["credit"]
        st = ("⚠️ **Licence to be cleared** before deployment" if "clear" in cr.lower()
              else "Share-alike licence: attribution + same licence required" if "BY-SA" in cr
              else "Public-domain claim: verify jurisdiction and provenance")
        rows.append(f"| `{c['key']}` | {esc(c['alt'])} | {esc(cr)} | {st} |")
    return "\n".join(rows)


def sources():
    rows = ["| Ref | Item | Source named in the prototype | Rights state | Workflow status | Cached offline |", "|---|---|---|---|---|:---:|"]
    for i in sorted(D["items"], key=lambda x: x.get("sourceRef", "")):
        rows.append(f"| {i.get('sourceRef','—')} | {i['id']} | {esc(i.get('sourceName','—'))} | `{i.get('rights')}` | "
                    f"`{i.get('status') or 'published'}` | {'yes' if i.get('cached') else 'no'} |")
    return "\n".join(rows)


TABLES = {k: v for k, v in globals().items() if callable(v) and k not in ("esc", "Path") and not k.startswith("_")}


def _embed(rel, lang):
    return f"**[`{rel}`]({rel})**\n\n```{lang}\n" + (ROOT / rel).read_text(encoding="utf-8").rstrip() + "\n```"


def schemas():
    return "\n\n".join(_embed(f"contracts/{n}", "json") for n in
                        ("ask-response.schema.json", "offline-manifest.schema.json", "ingest-manifest.schema.json"))


def openapi():
    return _embed("contracts/openapi-excerpt.yaml", "yaml")


def ingestexample():
    return _embed("contracts/examples/ingest-demo-item-001.json", "json")


def testrun():
    return "```text\n" + (ROOT / "docs" / "test_run.txt").read_text(encoding="utf-8").rstrip() + "\n```"


TABLES = {k: v for k, v in globals().items() if callable(v) and k not in ("esc", "Path") and not k.startswith("_")}


def benchmark():
    b = json.loads((ROOT / "diagrams" / "benchmark_results.json").read_text(encoding="utf-8"))
    s = b["summary"]
    rows = ["| ID | Bucket | Question | Status | Cited passage | First relevant rank | Outcome | Reason (non-answers) |",
            "|---|---|---|---|---|:---:|---|---|"]
    for r in b["rows"]:
        oc = {"correct": "✅ correct", "correct_abstention": "✅ correct abstention",
              "other_passage_same_item": "🟡 other passage, same item", "false_abstention": "🔴 false abstention",
              "wrong_item": "🔴 wrong item", "UNSUPPORTED_ANSWER": "🔴 **unsupported answer**"}[r["outcome"]]
        rows.append(f"| {r['id']} | {r['bucket']} | {esc(r['text'])} | `{r['status']}` | "
                    f"{', '.join(f'`{c}`' for c in r['cited']) or '—'} | {r['rank'] or '—'} | {oc} | {esc(r['reason']) or '—'} |")
    summ = ["", "| Summary | Value |", "|---|---:|",
            f"| Answerable questions | {s['answerable_n']} |",
            f"| Retrieval Hit@5 / MRR (answerable) | {s['hit@5']:.3f} / {s['mrr']:.3f} |",
            f"| Answered, citing a labelled passage | {s['answered_with_labelled_citation']} / {s['answerable_n']} |",
            f"| Answered, citing another passage of a labelled item | {s['other_passage_same_item']} / {s['answerable_n']} |",
            f"| Answered, citing an unlabelled item | {s['wrong_item']} / {s['answerable_n']} |",
            f"| False abstentions | {s['false_abstentions']} / {s['answerable_n']} |",
            f"| Unanswerable + misattribution probes | {s['negative_n']} |",
            f"| Correct abstentions on probes | {s['correct_abstentions']} / {s['negative_n']} |",
            f"| **Unsupported answers on probes** | **{s['unsupported_answers']}** |"]
    return "\n".join(rows + summ)


TABLES = {k: v for k, v in globals().items() if callable(v) and k not in ("esc", "Path") and not k.startswith("_")}
