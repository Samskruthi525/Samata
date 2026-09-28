# Part K: Planning, Risk and Delivery

## 61. Cost Drivers

> *"A precise rupee budget requires current quotations, campus equipment availability, cloud usage, labour rates, collection size and licensing agreements. Giving a single 'cost of the complete archive' now would be misleading."* (design document § 14)

This README therefore gives **no rupee totals**. It gives the **units to quote** and the **factors that drive each one**, so the team can build a quote-backed budget.

### 61.1 Decision-oriented cost worksheet

| Cost category | Unit to quote | Main scale factor | Prototype approach | Quote (₹) |
|---|---|---|---|---|
| **Kiosk hardware** | Per working kiosk | Screen size, enclosure, power, cooling, accessibility parts | Borrow a touchscreen if available; Pi 5 + official PSU + cooler + PIR + button | `TBD` (vendor quote) |
| **Scanning / transcription** | Per page, or per hour of source media | Condition, language/script, handwriting, review depth | Start with public/cleared **sample** items only | `TBD` |
| **Storage / backup** | Per GiB-month and per recovery copy | Preservation-master size, video source size, copy count | Tiny cleared corpus; measure a pilot batch before buying anything ([§ 62](#62-storage-sizing)) | `TBD` |
| **Search / embedding** | Per page/chunk ingested, or server runtime | Corpus size, model, re-index frequency | Small corpus; re-index only on publish | `TBD` |
| **Generative AI / speech** | Per question / minute of speech, or server runtime | Visitor traffic, TTS/ASR mode, provider contract | **Cap cloud API calls**; pre-generate narration for short approved stories | `TBD` |
| **Staff** | Person-weeks | Curatorial review, UX, engineering, security, support | Four students for six weeks + curator review time | Academic |

### 61.2 Hardware quote sheet (fill in from real quotes)

| # | Part | Qty | Vendor A (₹) | Vendor B (₹) | Chosen | Notes |
|---|---|---:|---:|---:|---|---|
| 1 | Raspberry Pi 5 (RAM `TBD`: 4 GB / 8 GB) | 1 | | | | RAM choice follows the UI profiling in Phase 2 |
| 2 | Official 27 W USB-C PSU | 1 | | | | Don't substitute a phone charger |
| 3 | Active cooler | 1 | | | | |
| 4 | microSD (A2 class) or NVMe SSD + HAT | 1 | | | | SSD improves robustness; costs more |
| 5 | Touch display (size `TBD`) | 1 | | | | Borrow if possible |
| 6 | PIR module (3.3 V-compatible OUT, or level shifter) | 1 | | | | Measure OUT before use |
| 7 | Large arcade-style HOME button | 1 | | | | Accessibility: large, tactile, labelled |
| 8 | LED + resistor | 1 | | | | See [§ 69](#69-discrepancies-between-source-documents) for the resistor value |
| 9 | Jumpers / header / strain relief | set | | | | |
| 10 | Headphone jack / small speaker (optional) | 1 | | | | Quiet environments |
| 11 | Enclosure (lockable) | 1 | | | | Physical security ([§ 41](#41-threat-model)) |
| | **Total** | | | | | |

### 61.3 Prototype cost control (design document)

1. Borrow a touchscreen if available.
2. Start with public/cleared sample items.
3. Cap cloud API calls (`ASK_DAILY_CAP`, `ASK_PER_DEVICE_PER_MIN`).
4. Pre-generate narration for short approved stories.
5. **Measure cost before scaling** to all archival assets.
6. **Don't store a giant preservation master on the Pi** just to prove an embedded concept.

---

## 62. Storage Sizing

<div align="center">
<img src="diagrams/24_storage_scenarios.png" alt="Storage scenarios" width="900"/>
</div>

```text
master_storage_GiB = scanned_pages × measured_mean_MiB_per_page / 1024
```

Then **add separately**: access derivatives, audio/video, database, snapshots.

| Pages | 10 MiB/page | 25 MiB/page | 60 MiB/page | 25 MiB/page × 3 logical copies |
|---:|---:|---:|---:|---:|
| 1,000 | 9.8 GiB | **24.4 GiB** | 58.6 GiB | **73.2 GiB** |
| 5,000 | 48.8 GiB | 122.1 GiB | 293.0 GiB | 366.2 GiB |
| 10,000 | 97.7 GiB | 244.1 GiB | 585.9 GiB | 732.4 GiB |
| 50,000 | 488.3 GiB | 1,220.7 GiB | 2,929.7 GiB | 3,662.1 GiB |

Computed with `reference/heritage_core/sizing.py`. The 1,000-page row matches the design document's worked example (≈ 24.4 GiB masters; ≈ 73.2 GiB for three copies), and this is checked by `test_storage_matches_design_doc`.

> [!WARNING]
> **These are illustrative assumptions.** 25 MiB/page is **for illustration only**. Real master sizes vary with capture format, resolution, image content and compression. The figures **exclude** media and database overhead. The "three copies" bars show **replicated logical bytes**. They are **not** vendor billing, geo-resilience or an actual backup design. **Measure a pilot batch** of real documents before buying a server.

### 62.1 Offline bundle on the Pi

The Pi only holds the **access derivatives** of the approved public subset, never masters.

| Component | Estimate method | Prototype |
|---|---|---|
| Page access images | pages × measured access-JPEG size | A few dozen pages |
| Captions / transcripts | Small text files | KB |
| Short media clips (if cached) | minutes × bitrate of the access derivative | Keep clips short; stream the rest when online |
| FTS5 index | ≈ proportional to cached text | KB–MB |
| Headroom | ≥ 2× the bundle, for atomic swaps (old + new side by side) | Required |

---

## 63. Risk Register

<div align="center">
<img src="diagrams/25_risk_matrix.png" alt="Risk matrix" width="900"/>
</div>

> [!NOTE]
> The design document's Figure 12 is labelled *"team starting assumptions before mitigation, not an empirical risk assessment. Re-score with stakeholders."* Its numeric scores could not be extracted from the PDF. The **likelihood/impact values in the figure above are this README's own starting assumptions** in the same spirit, and should be re-scored at the first stakeholder workshop.

| # | Risk | Trigger / consequence | Mitigation | Owner | L | I | Score (before) |
|---|---|---|---|---|:---:|:---:|:---:|
| 1 | Unclear reuse rights | The public kiosk reproduces an unapproved PDF/recording | Rights register; `unknown` is not public; link rather than mirror where required ([§ 10](#10-rights-gate)) | Content lead | 3 | 5 | 15 |
| 2 | False quote, speaker or page | AI undermines historical trust | Retrieved IDs + server-assembled citations; expert question tests; abstain ([§ 33](#33-rag-answer-contract)) | Research lead | 3 | 5 | 15 |
| 3 | OCR corrupts historical names | Bad search and misleading exact quotes | Separate print vs handwriting pipelines; manual correction; show the scan; **no exact quoting of unreviewed text** | Research lead | 4 | 3 | 12 |
| 4 | Network or cloud outage | Kiosk appears broken | Small versioned offline bundle; offline banner; reconnect test ([§ 23](#23-offline-behaviour-contract)) | Embedded lead | 3 | 3 | 9 |
| 5 | GPIO overvoltage / poor supply | Board damage or an unstable demo | Measure sensor output; recommended PSU; no exposed wiring ([§ 18](#18-electrical-and-physical-safety)) | Embedded lead | 2 | 4 | 8 |
| 6 | Unusable or inaccessible touch layout | Visitor exclusion; poor exhibit experience | Test with keyboard, captions, seated approach, contrast and real visitor sessions ([§ 38](#38-accessibility)) | UX lead | 3 | 4 | 12 |
| 7 | Cost expands unexpectedly | Cloud/AI bills exceed budget | Daily call caps, caching, lifecycle rules, monitoring ([§ 55.4](#554-cost-guard-rails-at-deploy-time)) | Backend lead | 2 | 3 | 6 |
| 8 | Historical timeline overstates claims | Interpretive harm | Curator writes/reviews each event; evidence attached; correction/version procedure ([§ 30](#30-editorial-timeline-workflow)) | Curator | 2 | 4 | 8 |
| 9 | Pi theft or tampering | Cached content or token compromised | Cache only public material; limit credentials; lock the enclosure ([§ 41](#41-threat-model)) | Embedded lead | 2 | 3 | 6 |

### 63.1 Additional risks this README adds (not in the design document)

| # | Risk | Why it matters | Mitigation |
|---|---|---|---|
| 10 | Placeholder content shown as real | The prototype contains placeholder quotes, page numbers and a placeholder venue label | Appendix G checklist: every public item is curator-verified; remove the venue label unless it's authorised |
| 11 | Uncleared images in the prototype | Two embedded images say *"licence to be cleared before deployment"* ([§ 72](#72-credits-and-source-register)) | Replace or clear them before any public showing, including screenshots in publications |
| 12 | Single curator bottleneck | Gates A, C and D all need curator time | Book review slots in Phase 0; reduce the corpus rather than skip review |
| 13 | Demo-day network | Venue Wi-Fi is captive or blocked | Rehearse the offline path (Gate E); bring an Ethernet cable / hotspot |

---

## 64. Demonstration Script

The design document specifies a **ten-minute assessment demonstration**. The prototype contains the same script as its *Demo script* checklist (keys `d1`…`d9`, [Appendix F](#appendix-f-interface-string-keys)).

| Time | Segment | What to do | What to say / point at | Prototype support | Fallback if it fails |
|---|---|---|---|---|---|
| 0:00–1:00 | **Physical overview** | Show the real Pi, touch input, accessible button, PIR, safe power, connection diagram | "The conceptual images are illustrative." | Printed wiring diagram ([§ 17](#17-gpio-connection-schedule)) | Photo of the wiring |
| 1:00–2:00 | **Wake and browse** | Stand in front of the PIR; attract → Home; open all five collection tiles quickly | Wakes once, no loud playback | Device console → *PIR* | Touch to wake |
| 2:00–3:30 | **Verify a source** | Search a known term; open a source item | Title, rights, volume/edition, **printed page**, original scan | Search "caste" → WS-001 | Open from Explore |
| 3:30–4:30 | **Interact with history** | Open a curator-reviewed timeline event and its linked page or photograph | Evidence link; review state | Timeline → 26 Nov 1949 | Story "republic" |
| 4:30–5:30 | **Media** | Play a short, licensed clip with captions/transcript | **Authentic recording vs narration** badges | AV-001 | Transcript only |
| 5:30–7:30 | **Assistant** | Ask one answerable question → open its citation; ask one out-of-corpus question → abstention | "It refuses rather than invents." | Suggested question 1, then "favourite colour" | Show a screenshot of the abstention |
| 7:30–8:30 | **Embedded control** | Press the physical HOME button during playback | Stops and clears the session | Device console → *HOME* | — |
| 8:30–9:30 | **Offline resilience** | Disconnect Wi-Fi; browse a locally cached public item | Live AI **unavailable**, without pretending otherwise | Device console → *Wi-Fi off* | — |
| 9:30–10:00 | **Explain trust** | Show the rights register and **one test-result sheet with real measurements** | "Not aspirational charts." | Evidence screen (`V`) | Printed test sheet |

> [!IMPORTANT]
> In the prototype, the assistant step uses **scripted keyword routes**, not a live model ([§ 69](#69-discrepancies-between-source-documents)). Say so if asked. The live RAG contract is demonstrated by `reference/` and, once built, by the Phase 5 API.

---

## 65. Handover Bundle

The design document lists six items for the handover. This table maps each one to its location.

| # | Handover item (design document § 16.2) | Where it lives | Status |
|---|---|---|---|
| 1 | Live demo kiosk with stable auto-start; **labelled wiring record** and **sensor-voltage measurements** | Physical kiosk; `handover/wiring/` (photos + HW-02 record) | ⏳ Phase 6 |
| 2 | Source repository, dependency versions, setup instructions, deployment configuration templates **without secrets** | This repository + implementation repos; `.env.example`; [§ 54](#54-raspberry-pi-setup), [§ 55](#55-cloud-deployment) | ✅ docs / 📐 services |
| 3 | Curated five-category sample inventory and rights/attribution register | Rights register export (CSV) + [§ 12](#12-demo-corpus-inventory) | 🧪 demo corpus; ⏳ real register |
| 4 | Original-to-derivative mapping, citation reference sheet, documented page/timestamp alignment | `asset` table export; alignment sheet ([§ 14](#14-identifier-and-citation-policy)) | 📐 |
| 5 | QA report: test questions, OCR samples, user feedback, security/offline results, known limitations | `handover/qa-report.md` built from [§ 50](#50-test-protocol)–[§ 53](#53-benchmark-set-design) records | ⏳ |
| 6 | Recovery method: disk/OS image, database backup, offline bundle version, **contact for item withdrawal** | [§ 57](#57-backups-and-restore) + restore-drill log; takedown contact in [§ 31](#31-curation-and-publication-workflow) | 📐 procedure / ⏳ drill |

### 65.1 Handover folder layout (suggested)

```text
handover/
├── README.md                     # index + versions (Pi OS image, agent, UI, manifest, corpus)
├── wiring/                       # labelled photos, HW-02 meter photo, final connection table
├── rights/                       # register CSV export, permission records (or references to them)
├── qa-report.md                  # all test records, benchmark results, failures included
├── benchmark/                    # questions.json, labels, run outputs
├── alignment/                    # page/timestamp alignment sheets
├── recovery/                     # restore-drill log, image checksum, backup locations (no secrets)
└── contacts.md                   # roles: takedown contact, curator, technical owner
```

---

## 66. Prototype versus Future Capability

Legend: ✅ implemented here · 🧪 demonstrated in the HTML prototype (simulated where noted) · 📐 specified, not built · ⏳ future / institutional.

| Capability | Academic prototype (six weeks) | Institutional future | Status here |
|---|---|---|---|
| Kiosk hardware | One Pi 5, touchscreen, PIR, HOME button, LED | Multi-kiosk fleet, audited enclosure, accessibility hardware | 🧪 / ⏳ |
| GPIO → UI events | Bridge + loopback relay (+ static UI) | Unix-socket relay; signed agent packages | ✅ code / ⏳ |
| Kiosk UI | Single-file HTML prototype | React + TS build, fully localised, audited | 🧪 / 📐 |
| Languages | EN, HI, MR complete; **TE partial (70/236 keys)** | More Indian languages, native review, sign-language media where justified | 🧪 / ⏳ |
| Collections | 14 demo records (placeholders) | Permission-backed corpus under a collection policy | 🧪 / ⏳ |
| Rights gate | Fail-closed matrix, tested | Legal agreements, expiry tracking, audit | ✅ / ⏳ |
| Search | BM25 + trigram stand-in + RRF on the demo corpus | Real embeddings in pgvector; tuned reranker; IIIF Content Search | ✅ reference / 📐 |
| AI assistant | Prototype: **scripted keyword routes**. Reference: contract with a deterministic stand-in generator. | Server-side LLM under the same contract; benchmark-gated | 🧪 / ✅ contract / 📐 |
| Citations | Catalogue-built, page/timestamp-exact | Same + persistent identifiers, IIIF deep links | ✅ reference |
| OCR | Metric code; sample strings | Per-script pipelines, human review workflow | ✅ metrics / 📐 |
| Offline | Manifest rules tested; prototype banner + cached badges | Signed (Ed25519) manifests, key rotation, fleet reporting | ✅ rules / 📐 |
| Curation | Prototype workflow screen (simulated) | Two-person review, MFA admin, audit log | 🧪 / 📐 |
| Visitor analytics | Simulated ledger | Privacy-reviewed aggregate counters only | 🧪 (simulated) / ⏳ |
| "Take it with you" QR | Non-scannable demo that expires | Short-lived signed link to public citations only | 🧪 / ⏳ |
| Preservation | Design only | NDSA-scored storage, fixity, restore drills | 📐 / ⏳ |
| Accessibility | Design targets (WCAG 2.2 AA, GIGW 3.0) | **Independent audit** | 📐 / ⏳ |
| Security | Controls specified; loopback-only relay tested | Pen test, WAF, device identity, incident response | ✅ partial / ⏳ |

---

## 67. Scale-up Roadmap

<div align="center">
<img src="diagrams/31_scaleup_roadmap.png" alt="Scale-up roadmap" width="900"/>
</div>

**Phases 2–3 are not part of the class demo.**

| Phase | Scope (design document § 17) | Entry condition | Exit evidence |
|---|---|---|---|
| **1 Academic proof** | One Pi kiosk, small cleared corpus, reviewed multilingual samples, fixed evaluation set | This README's Phases 0–7 | Handover bundle ([§ 65](#65-handover-bundle)); gates A–E passed |
| **2 Institution pilot** | Permission agreements; collection policy; multi-kiosk fleet; on-site or approved hybrid infrastructure; professional digitisation and restoration drills; security and accessibility audit | A named institutional partner **with written agreement** | Audit reports; restore-drill logs; pilot metrics with real denominators |
| **3 Wider archive** | IIIF where useful; distributed curatorial workflows; name authority and knowledge graph; more Indian languages; research accounts where justified; legally authorised external collection links | Pilot evaluation accepted | Coverage and permissions that actually justify wider claims |

> *"The most important scale-up resource is curatorial capacity and rights management, not a larger model. Only advertise 'full archive access' when the corpus coverage and permissions actually warrant that claim."* (design document § 17)

---

## 68. Known Limitations

### 68.1 Of the prototype (HTML)

1. **Scripted Q&A.** "Ask the Archive" matches keywords against eight curated routes (`ASK_SET`). It is not retrieval or generation. Anything else gets "NOT VERIFIED FROM THIS ARCHIVE".
2. **Placeholder content.** Transcriptions, some quotations and page numbers are placeholders flagged in the data. The prototype's own text says *"All page images here are generated placeholders."*
3. **Simulated hardware and network.** PIR, HOME and Wi-Fi are simulated by the Device console. The page doesn't listen to `/device/stream`.
4. **Simulated analytics.** The visitor ledger (24 sessions, 91 % satisfaction, …) is invented demo data.
5. **Partial Telugu.** 70/236 interface keys; the rest fall back to English. No string has been reviewed by a native speaker.
6. **Demo QR.** The "Take it with you" code is not scannable.
7. **Images with open licences-to-clear.** Two embedded photographs carry *"licence to be cleared before deployment"* credit lines.
8. **No persistence.** Curator actions, the reading list and ratings live only in memory.

### 68.2 Of the reference implementation

1. **The "dense" retriever is a character-trigram stand-in**, not a neural embedding. It exists to exercise the fusion logic.
2. **The evidence-coverage heuristic** (`min_coverage = 0.5`) is simple lexical coverage. It gives false abstentions (e.g. "Poona Pact") and could give false acceptances on adversarial phrasing. It must be tuned against the real benchmark.
3. **Prompt-injection detection is pattern-based** and only flags. The real defence is the contract itself: IDs must come from the retrieved set, and citations are built from the catalogue.
4. **HMAC manifest signing** (a shared key) is a prototype stand-in. Future versions use asymmetric signatures, so a stolen Pi can't forge a manifest.
5. **Eight-query benchmark.** The benchmark exercises the pipeline; it is not an evaluation.

### 68.3 Of this documentation

1. The design document's risk scores and some chart values couldn't be extracted from the PDF; figures 25–26 use this README's assumptions and are labelled so.
2. Pi OS package names and autostart mechanisms change between releases. The commands must be checked against the image actually used.
3. The cloud provider, model provider, embedding model and OCR engine are all `TBD`.

---

## 69. Discrepancies Between Source Documents

The two source documents (the PDF design document and the HTML prototype) mostly agree. Where they differ, this README **follows the design document for engineering values** and records the difference here rather than hiding it.

| # | Topic | Design document (PDF) | HTML prototype | This README's position |
|---|---|---|---|---|
| D-1 | LED series resistor | **1 kΩ** | **330 Ω** (wiring panel) | Both are plausible for a 3.3 V GPIO LED; 1 kΩ is dimmer and draws less current. **Use 1 kΩ** unless visibility testing shows it's too dim, then record the value actually fitted. |
| D-2 | HOME debounce | `bounce_time=0.15` (150 ms) | Log line says "debounced 50 ms" | **150 ms** in code (`pi_gpio_bridge.py`); the prototype log text is cosmetic |
| D-3 | MP-002 / AV-002 rights | Unknown/pending ⇒ not public | Records are `public_display_approved` + `published` + cached, but their source names read *"pending rights clearance"* / *"clearance pending"* | **Treat as not public** until a permission record exists. The demo corpus keeps the prototype values so its UI can be reproduced; the rights register must be corrected before any public use. |
| D-4 | Venue | No institution named; no partnership claimed | The attract screen shows a venue label (a named international centre) | **Placeholder.** Remove it, or obtain written authorisation before showing it publicly. |
| D-5 | AI Q&A | Server-side RAG with retrieval, verification and abstention | Scripted keyword routing to eight answers | Prototype = interface demonstration; `reference/answer_contract.py` = the contract; Phase 5 = the real service |
| D-6 | Visitor outcomes | Anonymous, privacy-reviewed counters | Simulated ledger with specific numbers | Simulated; never quote those numbers as results |
| D-7 | Quotations | "Replace all demo placeholder titles, exact quotes, page identifiers and media links with curator-verified material" | Several quotes marked "wording to be verified" | Curator verification is a Gate D precondition |
| D-8 | Search target | "Citable item in the top 5" for sampled questions | Evidence screen shows **≥ 80 %** | 80 % is a **placeholder target**, to be agreed with the supervisor and curator |
| D-9 | Image rights | "A searched image or source page is not, by itself, an archival licence" | Two images credited *"licence to be cleared before deployment"*; the status bar says "SAMPLE, RIGHTS-CLEARED PLACEHOLDERS ONLY" | The status text overstates. Clear or replace those two images. |
| D-10 | Languages | "Reviewed multilingual samples" | EN/HI/MR complete, TE partial (70/236) | Report TE as partial; native review for all |
| D-11 | Bridge script path | `/home/pi/archive/scripts/pi_gpio_bridge.py` | — | This repository uses `kiosk-agent/pi_gpio_bridge.py`; unit files updated to match |
| D-12 | Unit dependency | `heritage-gpio.service` has `After=network.target` only | — | Adds `After=/Wants=heritage-events.service` so the relay starts first |

---
