# Part I: Verification and Evaluation

## 49. Test Strategy

> **Testing is not complete just because a demo screen looks convincing.** Prepare a rights-cleared fixed corpus, an expert-checked answer sheet, a printed-page alignment sheet and a hardware checklist. **Log observed outcomes separately** from the proposed acceptance targets.

<div align="center">
<img src="diagrams/27_test_coverage.png" alt="Test coverage" width="900"/>
</div>

### 49.1 Test levels

| Level | What | Where | Tooling | Status |
|---|---|---|---|---|
| **L1 Unit (rules)** | Rights gate, retrieval, answer contract, manifest, state machine, metrics, bridge | `reference/tests/` | pytest | ✅ 46 passing |
| **L2 Unit (services)** | API routes, worker jobs, agent sync | Each implementation repo | pytest, vitest | 📐 |
| **L3 Contract** | OpenAPI and JSON Schema conformance; shared vectors from `heritage_core` | API, UI, agent CI | schemathesis / jsonschema (`TBD`) | 📐 |
| **L4 Integration** | Pi ↔ local service ↔ UI; UI ↔ API; manifest round-trip | Staging + a bench Pi | Playwright, scripts | 📐 |
| **L5 Hardware** | HW-01…HW-04 with a meter, a stopwatch, thermal logs | Physical kiosk | Manual + logs | ⏳ |
| **L6 Evaluation** | Search P@5/MRR, answer support, citation validity, OCR CER/WER per script | Fixed benchmark | `heritage_core.metrics` | ✅ metric code; ⏳ real corpus |
| **L7 Visitor / accessibility** | Personas P1–P6; ACCESS-01 | Venue | Observation sheets | ⏳ |
| **L8 Security** | SEC-01, injection (RAG-03), secret scan, admin/device separation | Staging | Scripts, scanners | 📐 |

### 49.2 Principles

1. **Targets are not results.** Charts in this README are targets or illustrations. The test report holds real measurements, screenshots and failed cases.
2. **Don't merge metrics with different denominators** into a single "AI accuracy" score.
3. **Every failure is recorded**, including abstentions and unsupported answers.
4. **Record the context:** date, tester, Pi OS release, hardware revision, corpus version, model/embedding versions.
5. **Relevance is defined before evaluation.** The curator labels the relevant passages first; then the system is run.

---

## 50. Test Protocol

These are the component and integration test cases from the design document (§12.1). The prototype mirrors them in its TESTS table. The **Observed result** column is left blank on purpose; it gets filled in during the real test runs in Phases 2–6.

<!-- GEN:tests -->

### 50.1 How to run the demo-runnable cases in the prototype

1. Open `prototype/ambedkar_kiosk.html`.
2. Press `V`, or use Device console → *Evidence and evaluation screen*.
3. Rows marked **DEMO-RUNNABLE** have a **Run** button. It drives the UI through the scenario (e.g. HW-03 triggers the reset routine; DOC-01 searches "caste" and opens WS-001 at the cited passage).
4. A **Run** in the prototype shows that the *interface path* exists. It is **not** a pass of the physical or backend test.

### 50.2 Test record template

```markdown
### Test HW-02 — PIR output and single wake
- Date / tester: 2026-10-__ / ________
- Hardware: Pi 5 (8 GB) rev ____, PIR module ______ (VCC __ V)
- Pi OS release: ________ · agent version: ____ · UI bundle: ____
- Procedure: (as protocol)
- Measurements: PIR OUT high = ____ V (meter model ____)
- Observed: wakes once? [ ] yes [ ] no — notes: ______
- Result: PASS / FAIL / BLOCKED
- Evidence: photo_hw02_meter.jpg, log excerpt lines ____
```

---

## 51. Evaluation Metrics

| Metric | Definition | Implementation | Report with |
|---|---|---|---|
| **Search Precision@5** | Answer-bearing or relevant items in the top five, averaged over expert-labelled queries. Relevance is defined before evaluation. | `metrics.precision_at_k` | Per-query table + failing examples |
| **Hit@5** | Share of queries with ≥ 1 relevant result in the top five (the design document's acceptance phrasing) | `metrics.hit_at_k` | Same |
| **MRR** | Mean reciprocal rank of the first relevant result | `metrics.reciprocal_rank` | Same |
| **Answer support** | Share of factual generated answers for which a reviewer can verify **every** factual claim against the cited spans. Report all abstentions and unsupported answers. | Human review sheet | Numerator, denominator, abstentions, unsupported |
| **Citation validity** | Share of produced citation links that resolve to the intended permitted item/page/time | `metrics.citation_validity` + link checker | Count of broken links |
| **Abstention on out-of-scope** | Share of the unanswerable queries that got `not_verified` | Benchmark runner | List of any non-abstentions (serious) |
| **OCR CER / WER** | Edit distance vs manually transcribed ground truth ÷ ground-truth length, **per script and document class**. Document the sampling method. | `metrics.cer`, `metrics.wer` | Table by script/class; sampling method |
| **Hardware** | Cold-boot time, approach→Home time, button response, thermal behaviour, recoverability after unplugging the network | Stopwatch, logs, `vcgencmd` | Raw measurements, conditions |
| **Visitor outcomes** | Time to find a sample item, completion rate, optional anonymous one-question satisfaction prompt | Anonymous counters, observation | Medians, n, context |

<div align="center">
<img src="diagrams/26_pilot_targets.png" alt="Pilot targets" width="900"/>
</div>

---

## 52. Reference Implementation Results

These results come from **this repository's code run on the 14-item demo corpus**. They show that the rules and metric pipeline work end to end. They are **not** an evaluation of any archive, model or OCR engine.

### 52.1 Automated tests

<!-- GEN:testrun -->

The block above is the **verbatim output of `scripts/record_test_run.py`** (stored in `docs/test_run.txt`), not hand-typed. The package targets Python ≥ 3.10. `test_contracts.py` also checks that the JSON Schemas in `contracts/` accept what the reference code actually emits. It is skipped if `jsonschema` isn't installed.

#### What each test guards

| Test file | Test | Guards requirement | Guards risk (§ 63) | What would go wrong without it |
|---|---|---|---|---|
| `test_rights.py` | `test_closed_states_block_everything[unknown · permission_pending · withdrawn]` | FR-02, NFR-01 | 1 | An item with unclear rights appears on the kiosk |
| | `test_unpublished_never_public` | FR-10 | 1, 8 | A draft or in-review item leaks before curator approval |
| | `test_link_only_lists_but_does_not_mirror` | FR-02 | 1 | A link-only item gets copied, indexed or cached |
| | `test_permissions_are_independent` | FR-02 | 1 | Display permission silently implies AI or download permission |
| | `test_restricted_staff_only` | NFR-06 | 1 | Staff-only material reaches the public role |
| | `test_withdrawn_status_overrides_rights` | FR-10 | 1 | A takedown is ignored because the rights field still says "approved" |
| | `test_matrix_shape` | NFR-09 | — | A new state or action is added without a decision for every cell |
| `test_corpus_retrieval.py` | `test_demo_corpus_counts` | NFR-09 | — | The export drifts from the prototype unnoticed |
| | `test_printed_page_differs_from_pdf_index` | FR-03, NFR-01 | 2 | Citations point to the wrong page |
| | `test_pending_and_link_only_not_indexed` | FR-02, FR-04 | 1 | Search returns items that can't be shown |
| | `test_alias_expansion` | FR-04 | 3 | Searching "Babasaheb" misses records that say "Ambedkar" |
| | `test_known_query_top5` | FR-04 | — | A basic known-item search regresses |
| | `test_media_passages_carry_timestamps` | FR-06 | 2 | Media citations invent page numbers instead of times |
| `test_answer_contract.py` | `test_answerable_question_is_cited` | FR-05 | 2 | Answers appear without citations |
| | `test_out_of_scope_abstains` | FR-05, NFR-01 | 2 | The assistant invents an answer outside the corpus |
| | `test_offline_is_unavailable_not_fake` | FR-09 | 4 | The kiosk fakes an answer while offline |
| | `test_fabricated_passage_id_rejected` | NFR-01 | 2 | A model-invented passage ID becomes a citation |
| | `test_citation_built_from_catalogue_not_model` | NFR-01 | 2 | A model-written title or page is shown as fact |
| | `test_prompt_injection_flagged` | NFR-06 | 2 | Instructions inside documents steer the model unnoticed |
| | `test_pending_item_never_cited` | FR-02, FR-05 | 1, 2 | A pending item is quoted through the assistant |
| | `test_personal_trivia_abstains` | FR-05 | 2 | Personal trivia is answered by guesswork |
| `test_kiosk_state.py` | `test_pir_ignored_during_warmup` | FR-08 | 5 | False wakes right after boot |
| | `test_pir_wakes_once_not_loop` | FR-08, NFR-03 | — | The kiosk keeps waking in a loop (HW-02) |
| | `test_idle_warning_then_reset_clears_session_keeps_cache` | NFR-05 | — | The next visitor sees the previous visitor's session |
| | `test_extend_returns_to_active` | NFR-03, NFR-04 | 6 | Slow readers are thrown out |
| | `test_home_same_reset_as_timeout` | FR-08, NFR-05 | — | HOME and timeout clear different things |
| | `test_network_loss_disables_assistant_only` | FR-09, NFR-08 | 4 | Network loss blanks the whole kiosk |
| `test_manifest.py` | `test_only_cacheable_items` | FR-02, FR-09 | 1, 9 | Non-cacheable items are copied to the Pi |
| | `test_tamper_detected` | NFR-06 | 9 | An edited manifest adds items to the cache |
| | `test_fail_closed_after_grace` | FR-09, NFR-06 | 1, 9 | A stale cache keeps showing withdrawn content indefinitely |
| | `test_update_is_atomic_and_revokes` | FR-10, NFR-07 | 1 | A takedown doesn't reach the kiosk, or a crash leaves a half-updated cache |
| | `test_rollback_rejected` | NFR-06 | 9 | Replaying an old manifest restores withdrawn items |
| `test_metrics_sizing_agent.py` | `test_cer_wer` | FR-03 | 3 | OCR quality is reported with a wrong formula |
| | `test_ranking_metrics` | FR-04 | — | Search quality is reported with a wrong formula |
| | `test_storage_matches_design_doc` | NFR-10 | 7 | Storage planning diverges from the design document |
| | `test_bridge_refuses_cloud_url` | NFR-05, NFR-06 | — | GPIO events are sent off-device |
| | `test_bridge_cooldown_and_failure_counting` | FR-08, NFR-07 | 4 | Network errors crash the GPIO loop |
| | `test_event_service_static_no_traversal` | NFR-06 | 9 | The local UI server exposes files outside the UI directory |
| | `test_offline_cache_schema_runs_and_matches_readme` | FR-09, NFR-09 | 4 | The documented cache schema doesn't run, or drifts from the file |
| `test_contracts.py` | `test_answer_outputs_match_ask_schema` | FR-05, NFR-09 | 2 | API consumers and the reference disagree on the answer shape |
| | `test_answered_without_citation_is_invalid` | NFR-01 | 2 | The schema accepts an uncited "answered" response |
| | `test_manifest_matches_schema` | FR-09 | 9 | The Pi and the server disagree on the manifest shape |
| | `test_design_doc_ingest_example_matches_schema` | FR-01 | 1 | The ingest schema drifts from the design document's example |
| `test_benchmark_demo.py` | `test_demo_benchmark_has_no_unsupported_answers` | FR-05, NFR-01 | 2 | A retrieval or threshold change makes the assistant answer an unanswerable or misattributed question |

### 52.2 Retrieval on the demo corpus

Queries are the first key of each of the prototype's eight curated Q&A routes. The relevant results are the passages the prototype cites for that route, or any segment of a cited media item.

<div align="center">
<img src="diagrams/33_retrieval_benchmark_demo.png" alt="Retrieval benchmark (demo)" width="900"/>
</div>

<!-- GEN:retrieval -->

**Reading these results honestly:**

* With only eight queries, one query changes Hit@5 by 0.125. These numbers can't separate the methods statistically.
* **Hybrid did not beat lexical on MRR here.** On a corpus this small, the trigram stand-in adds noise. That is a reason to **benchmark real embeddings on a real test set** (Phase 4), not to assume that hybrid is better.
* **"poona pact" fails in every mode.** The cited passage never uses those words. The fix is curated metadata or relations, not a cleverer ranking ([§ 32.2](#322-what-the-demo-benchmark-revealed)).

### 52.3 Answer contract on the prototype's suggested questions

The prototype shows six suggested questions. Running them through `answer()` with the deterministic `extractive_generator`, a stand-in that quotes the top eligible excerpt, gives:

| Suggested question | Status | Cited passage | Comment |
|---|---|---|---|
| What did Ambedkar say about constitutional morality? | `answered` | `CR001-P-b` | Matches the prototype's route |
| What is Annihilation of Caste about? | `answered` | `WS001-P-d` | The prototype cites `WS001-P-b`; both are in the same item. The curator decides which passage best supports the answer. |
| When was the Constitution of India adopted? | `answered` | `CR001-P-a` | The prototype cites `CR001-P-e` / `MP001-P-a`. A different passage in the same record was chosen; review needed. |
| What happened at Nagpur in October 1956? | `answered` | `AV-001-T00` | Media segment → timestamp citation |
| Tell me about the Poona Pact. | `not_verified` | — | See the retrieval finding above. An honest abstention is better than an invented answer. |
| What was Dr. Ambedkar's favourite colour? | `not_verified` | — | Intended abstention case |

> The extractive stand-in **quotes** the top passage. A real model will **summarise**. The contract makes sure that, whatever the model writes, the only citations shown are verified, catalogue-built ones.

### 52.4 Demo benchmark with unanswerable and misattribution probes

`data/benchmark_demo.json` is a small benchmark in the [§ 53.3](#533-benchmark-file-format) format:

* **8 answerable questions** in natural language, one per prototype Q&A route. Relevance labels are **the prototype's own citations** for that route.
* **10 unanswerable questions**: trivia, events after 1956, anachronisms, personal data, off-topic.
* **3 misattribution probes**: quotes by other people, and a distorted version of a real formulation.

<div align="center">
<img src="diagrams/39_benchmark_outcomes.png" alt="Demo benchmark outcomes" width="900"/>
</div>

`scripts/run_benchmark.py` runs every question through `HybridIndex.search` and `answer()` with the extractive stand-in generator, and records `diagrams/benchmark_results.json`. The table is generated from that file:

<!-- GEN:benchmark -->

**What this shows, and what it doesn't:**

* ✅ **No probe got an answer.** All 13 unanswerable and misattribution probes abstained, and `test_demo_benchmark_has_no_unsupported_answers` now guards this. This is the property the design document cares most about: *abstain rather than invent*.
* 🟡 **"Other passage, same item" (3 of 8)** isn't necessarily wrong. The labels list only the one passage each prototype route cites, while the stand-in quotes the top-ranked passage of the same record. For example, Q-007 cites the English masthead summary (`WS002-P-b`) instead of the Marathi masthead (`WS002-P-a`). A curator must decide whether each is acceptable support. That is exactly the human answer-support review of [§ 51](#51-evaluation-metrics), which a script can't replace.
* 🔴 **One false abstention (Q-004, the Poona Pact)**, the same vocabulary gap as in [§ 32.2](#322-what-the-demo-benchmark-revealed).
* ⚠️ **Q-021 abstained at coverage 0.43, close to the 0.5 threshold.** The distorted quote shares most of its words with a real passage. Lowering `ASK_MIN_COVERAGE` to "fix" the Poona Pact case would put this probe at risk. The threshold has to be tuned on the full benchmark with **unsupported answers weighted far more heavily than false abstentions**.
* The MRR here (0.667) differs from § 52.2 (0.656) because these are natural-language questions, not route keywords. With n = 8, neither number supports a claim about quality.

### 52.5 OCR metric pipeline on sample strings

<div align="center">
<img src="diagrams/32_ocr_cer_demo.png" alt="OCR CER demo" width="900"/>
</div>

<!-- GEN:ocr -->

These "unreviewed OCR" strings are **hand-made samples embedded in the prototype** to show the reviewed-vs-OCR toggle. They are **not engine output**. High values, such as the CR-002 p.38 and WS-005 rows, mean the sample OCR text isn't aligned with the first reviewed passage on that page. They don't mean the "OCR is bad". The table shows that `metrics.cer/wer` run correctly on the data. A real OCR-01 run needs ground-truth transcriptions of **sampled** pages, by script.

### 52.6 Storage arithmetic

`sizing.master_gib(1000) = 24.4 GiB` and `sizing.logical_copies_gib(1000) = 73.2 GiB`. Both match the design document's worked example (test `test_storage_matches_design_doc`). See [§ 62](#62-storage-sizing).

### 52.7 Reproducing every number in this section

| Number(s) | Produced by | Stored in |
|---|---|---|
| Test listing (§ 52.1) | `python scripts/record_test_run.py` | `docs/test_run.txt` |
| Retrieval Hit@5 / MRR per method (§ 52.2) | `python scripts/generate_diagrams.py` | `diagrams/computed_metrics.json` |
| Suggested-question outcomes (§ 52.3) | `answer()` + `extractive_generator` in `reference/heritage_core/answer_contract.py` | — (deterministic) |
| Benchmark outcomes (§ 52.4, Figure 39) | `python scripts/run_benchmark.py` | `diagrams/benchmark_results.json` |
| OCR CER/WER (§ 52.5) | `python scripts/generate_diagrams.py` | `diagrams/computed_metrics.json` |
| Storage (§ 52.6, § 62) | `reference/heritage_core/sizing.py` | — (deterministic) |

No number in Part I is typed by hand. The README tables are injected from these files at build time, and CI fails if they drift.

---

## 53. Benchmark Set Design

The design document proposes this benchmark set:

* **about 40–60 questions** spanning the five categories, including **10 unanswerable queries** and **several deliberate misattributions**
* **30–50 sampled scanned pages** across the relevant scripts and qualities
* **all included timeline claims** checked by a curator

> These counts are **project planning suggestions, not a representative statistical sample** of the full archive.

### 53.1 Question mix (suggested)

| Bucket | Count (suggested) | Example pattern (placeholder) | Expected behaviour |
|---|---:|---|---|
| Exact title / quotation lookup | 8–10 | "Where does the text '…' appear?" | Correct item + printed page |
| Speaker / date (debates) | 6–8 | "What did [speaker] say on [date]?" | Correct speaker; don't attribute others' words |
| Concept without the source vocabulary | 8–10 | Paraphrased idea | Relevant passage in the top 5 (tests dense retrieval) |
| Media | 4–6 | "When in the recording is … mentioned?" | Timestamp citation |
| Timeline / event | 4–6 | "What happened in [year] at [place]?" | Event card + its evidence |
| Multilingual | 4–6 | Hindi/Marathi query for English content | Result + translation badge; original accessible |
| **Unanswerable** | **10** | Trivia, personal preferences, events after 1956, things outside the corpus | `not_verified` |
| **Deliberate misattribution** | 4–6 | "Quote where Ambedkar said X" when someone else said X, or nobody did | Abstain or correct the attribution **from evidence**; never confirm |
| Injection | 2 | Documents containing instructions | Instructions ignored (RAG-03) |

### 53.2 Page sample (suggested)

| Class | Pages | Notes |
|---|---:|---|
| Printed English (clean) | 8–12 | Baseline |
| Printed English (aged / periodical) | 6–10 | |
| Printed Devanagari (Marathi/Hindi) | 8–12 | Native-reader ground truth |
| Handwritten / manuscript | 4–8 | Report the human-review burden, not only CER |
| Mixed layout (tables, marginalia) | 4–8 | |

### 53.3 Benchmark file format

```json
{
  "benchmark_version": "2026-10-01",
  "corpus_version": "manifest-v42",
  "questions": [
    {"id": "Q-001", "bucket": "exact", "language": "en",
     "text": "…", "relevant": ["PASSAGE-ID-1", "PASSAGE-ID-2"], "answerable": true,
     "labelled_by": "curator:…", "labelled_at": "2026-09-30"},
    {"id": "Q-041", "bucket": "unanswerable", "language": "en", "text": "…", "relevant": [], "answerable": false}
  ]
}
```

---
