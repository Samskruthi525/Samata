# Part L: Reference

## 70. Glossary

Terms marked † come from the design document's glossary (Appendix D). The others are defined here for consistency across the repositories.

| Term | Meaning in this project |
|---|---|
| **Abstention** | The assistant's explicit "I could not verify this from the available archive" response (`not_verified`). It is a correct outcome, not an error. |
| **Access derivative** | Resized page image / PDF, lower-bandwidth video, playback audio and caption file. Only derivatives approved by rights policy are served to visitors. |
| **Accessibility target** | WCAG 2.2 AA and GIGW 3.0, used as **evaluation targets**. No certified conformance is claimed. |
| **Alias expansion** | Query rewriting from a curated alias table (e.g. *Babasaheb* ↔ *Ambedkar*) before lexical search. |
| **ASR** † | Automatic speech recognition: a draft transcript, **not proof of the speaker's words**. |
| **Attract screen** | The silent idle screen shown when no visitor is present (state `ATTRACT`). |
| **Authentic recording** | A badge for audio/video of the historical event or person itself, as opposed to **modern narration**. |
| **Badge** | A visible label of provenance and processing: ORIGINAL SCAN, REVIEWED TEXT, UNREVIEWED OCR, AI SUMMARY, AI TRANSLATION, AUTHENTIC RECORDING, MODERN NARRATION ([§ 37](#37-source-badges)). |
| **BCM numbering** | Broadcom GPIO numbers (e.g. BCM17), as opposed to physical header pin numbers (e.g. pin 11). GPIO Zero uses BCM. |
| **BM25** | A standard lexical ranking function; the lexical leg of hybrid retrieval. |
| **CER / WER** | Character / word error rate: edit distance vs ground truth ÷ ground-truth length. Reported **per script and document class**. |
| **Checksum / fixity** † | A value computed from bytes to detect changes. **Not by itself a backup.** |
| **Citation (catalogue-built)** | A citation assembled by the server from catalogue metadata for a verified passage ID. It is never copied from model text. |
| **Citation validity** | Share of citation links that resolve to the intended permitted item/page/time. |
| **Cooldown (PIR)** | Minimum interval between two PIR wake events (`KIOSK_PIR_COOLDOWN_S`); prevents wake loops. |
| **Curator** | The historian, librarian, faculty member or designated person who validates historical claims and publishes content. Engineers do not mark historical accuracy as reviewed. |
| **Debounce** | Ignoring contact bounce on a mechanical button (`bounce_time=0.15` s). |
| **Demo corpus** | The 14 sample records embedded in the prototype and exported to `data/demo_corpus.json`. **Placeholders**, not a verified archive. |
| **Dense retrieval** | Vector-similarity search over embeddings. In `reference/` it is a **character-trigram stand-in**. |
| **Derivative** † | An access or processing copy created from a retained source. |
| **Device console** | The prototype's left-edge panel that simulates PIR, HOME, Wi-Fi and idle timeout. |
| **Device token** | A per-kiosk scoped credential for public read + manifest routes. It can't reach admin routes. |
| **Evidence coverage** | The reference heuristic: the best passage must contain ≥ `min_coverage` of the query's content terms, otherwise the assistant abstains. |
| **Fail closed** | When in doubt (unknown rights, expired manifest, bad signature), show less rather than more. |
| **FTS5** | SQLite's full-text search extension; used for the small offline keyword search on the Pi. |
| **Gate (A–E)** | Decision points in the six-week plan that must pass before the dependent work proceeds ([§ 47](#47-development-phases)). |
| **GIGW 3.0** | Guidelines for Indian Government Websites 3.0, used as an accessibility/usability reference. |
| **GPIO** † | The Pi's general-purpose electrical input/output pins; **3.3 V logic on Pi 5**. |
| **Grace period (manifest)** | Time after `expires_at` during which the cache is still shown (`KIOSK_MANIFEST_GRACE_H`). After that, the kiosk fails closed. |
| **Hit@k** | Share of queries with at least one relevant result in the top *k*. |
| **HOME button** | A physical button that runs the same session reset as the idle timeout, without destroying the cache. |
| **Hybrid retrieval** | Lexical + dense results fused (RRF), then optionally reranked. |
| **IIIF** † | Standards for interoperable presentation and delivery of digitised objects (Image, Presentation, Content Search APIs). |
| **Ingest** | Inventory → rights → capture → SHA-256 → extract → align → review → publish ([§ 28](#28-digitisation-and-ocr-pipeline)). |
| **Kiosk agent** | The Python service on the Pi: GPIO bridge, health checks, manifest sync, session clearing. |
| **Knowledge map** | A curated graph of works, events, people and places ([§ 34](#34-knowledge-map)). Its edges are editorial claims and need evidence. |
| **lgpio** | The GPIO library GPIO Zero uses on Pi 5. |
| **Link-only** | Rights state in which an item may be listed and linked to its holder, but not mirrored, indexed or cached. |
| **Loopback-only** | Bound to `127.0.0.1`, so unreachable from the network. |
| **Manifest (offline)** | A signed, versioned, expiring list of the items/assets the kiosk may cache. |
| **MRR** | Mean reciprocal rank of the first relevant result. |
| **NDSA Levels** | NDSA Levels of Digital Preservation: a framework to evaluate fixity, storage, metadata, security and formats. |
| **OCR** † | Optical character recognition: a text-extraction **candidate** from a scan. |
| **Offline bundle** † | A limited, rights-cleared, versioned exhibition subset on the Raspberry Pi. |
| **Passage** † | A searchable, citable span associated with an original page or timestamp. |
| **PDF page index** | 0-based position of a page in the file. **Not** the printed page number; the two are stored separately. |
| **pgvector** | PostgreSQL extension for vector columns and similarity search. |
| **PIR** | Passive infrared motion sensor used to wake the kiosk. |
| **Precision@5** | Share of the top five results that are relevant, averaged over labelled queries. |
| **Preservation master** † | The original or designated high-quality retained archival object. Not the kiosk thumbnail. |
| **Printed page** | The page label printed on the source (e.g. "978", "xii"). This is what citations show to people. |
| **Processing derivative** | OCR/ASR candidates, layout data, embeddings, thumbnails, internal annotations. Regenerable; versioned when they underpin citations. |
| **Prompt injection** | Instructions hidden in documents that try to steer the model. Treated as untrusted evidence. |
| **RACI** | Responsible, Accountable, Consulted, Informed ([§ 48](#48-team-and-responsibilities)). |
| **RAG** † | Retrieval-augmented generation: the model answers using selected retrieved evidence. |
| **Reranker** | A model that re-scores the top fused results. Optional; must earn its place on the benchmark. |
| **Reviewed text** | A transcription checked by a person against the scan. Only reviewed text may be quoted exactly. |
| **Rights gate** † | An explicit decision that an item may be displayed, processed and downloaded under specified conditions. |
| **Rights register** | The record of rights state and permissions per item ([§ 10](#10-rights-gate)). |
| **RRF** | Reciprocal rank fusion: combines ranked lists by summing 1/(k + rank). |
| **Session reset** | Stop playback, clear the mic buffer, reading list, QR, question state, navigation and viewer, then return to ATTRACT. |
| **SSE** | Server-Sent Events; how the local relay pushes device events to the UI. |
| **Story** | A curated two-minute sequence of stops (e.g. *republic*, *voice*, *dhamma*). |
| **Takedown** | Withdrawal of an item on request; removes it from listing, search, AI context, reading lists and caches. |
| **Unreviewed OCR** | Machine text not yet checked. It is shown with a badge and never quoted as exact. |
| **Warm-up (PIR)** | Period after power-on during which PIR output is unreliable and ignored. |

---

## 71. FAQ

<details>
<summary><b>Does this project host all of Dr. Ambedkar's works?</b></summary>

No. It is an academic prototype with a small, rights-gated sample corpus. It doesn't claim to own, digitise, host or hold rights to every associated work. Candidate sources (for example the Dr. Ambedkar Foundation's collected-works catalogue and the Parliament Digital Library debates) are *sources to request permission from*, not content we can mirror.
</details>

<details>
<summary><b>Is the "Ask the Archive" feature in the prototype real AI?</b></summary>

No. The HTML prototype routes questions by keyword to eight curated answers, and says "NOT VERIFIED FROM THIS ARCHIVE" for anything else. The real design is server-side RAG under the contract in [§ 33](#33-rag-answer-contract), implemented and tested in `reference/heritage_core/answer_contract.py`.
</details>

<details>
<summary><b>How do you stop the AI from inventing quotes?</b></summary>

Five mechanisms work together:

1. Only permitted, retrieved passages are sent to the model.
2. The model must return passage IDs.
3. The server rejects any ID outside the retrieved set.
4. The server builds citations from the catalogue.
5. Unreviewed OCR is never quoted as exact.

If the evidence is weak, the system abstains. See `test_fabricated_passage_id_rejected` and `test_citation_built_from_catalogue_not_model`.
</details>

<details>
<summary><b>Why is the hybrid retriever worse than lexical on your benchmark?</b></summary>

Because the benchmark has eight queries and the "dense" leg is a trigram stand-in. The result is reported as measured ([§ 52.2](#522-retrieval-on-the-demo-corpus)). It tells us to benchmark real embeddings, not to assume hybrid wins.
</details>

<details>
<summary><b>What happens when the internet goes down?</b></summary>

The kiosk keeps showing the cached, approved exhibit with an offline banner. Search runs locally over cached text, and the assistant shows "unavailable". Nothing pretends to be online. If the cache's manifest expires beyond its grace period, the cache is hidden too (fail closed).
</details>

<details>
<summary><b>Why can't the browser read the GPIO pins directly?</b></summary>

Browsers have no GPIO access, and giving them any would be a security problem. The Python bridge reads the pins and posts to a loopback-only relay. The UI subscribes to that relay over SSE.
</details>

<details>
<summary><b>Does the kiosk record visitors?</b></summary>

No personal data is collected. There is no camera, and the PIR only detects presence. Query text is not stored. Sessions are wiped on reset. Heartbeats carry only counts and device health. The prototype's "visitor ledger" is simulated.
</details>

<details>
<summary><b>Why not just use a bigger model?</b></summary>

Because the bottleneck is curation and rights, not model size (design document § 17). A bigger model can't make an unapproved document public or verify a page number.
</details>

<details>
<summary><b>Can I use the photographs from the prototype?</b></summary>

Not without your own rights review. The credit lines are listed in [§ 72](#72-credits-and-source-register). Two images are marked "licence to be cleared before deployment".
</details>

<details>
<summary><b>Why is the LED resistor different in the PDF and the HTML?</b></summary>

It is a discrepancy between the sources (D-1 in [§ 69](#69-discrepancies-between-source-documents)). Use 1 kΩ unless visibility testing says otherwise, and record the value you fitted.
</details>

<details>
<summary><b>Is it WCAG compliant?</b></summary>

WCAG 2.2 AA and GIGW 3.0 are **targets**. The prototype includes contrast, text-size, captions and keyboard controls, but no audit has been done and no conformance is claimed.
</details>

<details>
<summary><b>Can this run on a Raspberry Pi 4?</b></summary>

Probably, for the UI and agent. The design targets Pi 5, and GPIO libraries differ between models (Pi 5 needs lgpio-backed GPIO Zero). Test it and record the result. Don't assume it works.
</details>

<details>
<summary><b>Why a separate repository for the reference rules?</b></summary>

So that every service (API, worker, agent, UI tests) checks against the **same test vectors** for rights, citations and manifests, and nobody re-implements the trust rules differently ([§ 44](#44-repository-architecture)).
</details>

<details>
<summary><b>Who can publish content?</b></summary>

Only authorised staff with MFA, through draft → in_review → approved_1 → published. The publisher must be a different person from the first reviewer. Engineers can't mark historical accuracy as reviewed.
</details>

<details>
<summary><b>How quickly does a takedown reach the kiosk?</b></summary>

At the next manifest sync (`KIOSK_SYNC_INTERVAL_S`, or immediately on reconnect). The worst case is bounded by the manifest expiry plus grace, because an expired manifest hides the cache.
</details>

<details>
<summary><b>Where did the charts come from?</b></summary>

Every chart and diagram is generated by `scripts/generate_diagrams.py` (matplotlib). Demo-corpus charts are computed from `data/demo_corpus.json` by the reference code. Target/assumption charts are labelled as such. No chart is hand-drawn or AI-generated.
</details>

---

## 72. Credits and Source Register

### 72.1 Item source register (demo corpus)

Each prototype record carries a `sourceRef` (SR-01 … SR-14). The table is generated from `data/demo_corpus.json`:

<!-- GEN:sources -->

> The source names are the prototype's own labels. For SR-08 and SR-11 the labels say clearance is *pending*, while the records are marked approved and cached. See D-3 in [§ 69](#69-discrepancies-between-source-documents). Before any public use, each row needs a real permission record ID.

### 72.2 Images embedded in the prototype

These credit lines are exactly as embedded in `prototype/ambedkar_kiosk.html`:

<!-- GEN:credits -->

> The prototype's own About text states that *"all page images here are generated placeholders"*. The page facsimiles are placeholders; the photographs above are the embedded historical images. **Screenshots in this README show these images inside the prototype**, and their reuse elsewhere needs the same review.

### 72.3 Design document image-use register

| Asset (design document) | Origin / credit | Status and use |
|---|---|---|
| Raspberry Pi 5 photograph | SimonWaldherr, "Raspberry Pi 5.jpg", Wikimedia Commons | **CC BY 4.0**; downsampled preview in the PDF. Keep the credit and licence link. **Not used in this README.** |
| Portrait of Dr. B. R. Ambedkar | "Dr. Bhimrao Ambedkar.jpg", Wikimedia Commons, photographer unknown | The file page lists it as public domain; review jurisdiction and provenance before wider reuse |
| Museum concept image | AI-generated for the design document | Concept art, **not** a real museum or historical source. **Not used here.** |
| Prototype concept image | AI-generated for the design document | Concept art, **not** a photograph of built hardware. **Not used here.** |
| Figures | Generated by the design document's Python plotting script | Proposal diagrams; charts labelled illustrative |

This README's figures were **regenerated independently** by `scripts/generate_diagrams.py`. No image from the PDF was copied.

### 72.4 Technical and archival references consulted by the design document

| Topic | Reference |
|---|---|
| Hardware | Raspberry Pi 5 hardware specification; Raspberry Pi power documentation |
| GPIO | GPIO Zero documentation (lgpio on Pi 5; installation via APT) |
| Collections | Dr. Ambedkar Foundation publication catalogue; Parliament Digital Library historical-debates catalogue |
| Interoperability | IIIF published API catalogue |
| Imaging | FADGI cultural-heritage still-image technical guidelines (2023), used as a quality reference, not a blanket DPI rule |
| Preservation | NDSA Levels of Digital Preservation |
| Accessibility | WCAG 2.2 overview; Guidelines for Indian Government Websites (GIGW) 3.0 |

> *"A searched image or source page is not, by itself, an archival licence for every item reachable from that site."* (design document § 18)

### 72.5 Project credits

| Role | Name |
|---|---|
| Embedded / physical build | `TBD` |
| Kiosk UI / accessibility | `TBD` |
| Cloud / catalogue / rights | `TBD` |
| Search / AI / OCR + curation coordination | `TBD` |
| Curator / historical reviewer | `TBD` |
| Supervisor | `TBD` |

---

## 73. Contributing

### 73.1 Ground rules

1. **No secrets in git**, ever. Use `.env.example` for names; values come from the secret store. Secret scanning runs in CI.
2. **No content without a rights record.** Don't add PDFs, images, audio or transcriptions to any repository unless the rights register says they can be there. Prefer references to the object store.
3. **Don't mark historical accuracy as reviewed** if you are not the designated curator.
4. **Don't hand-edit `README.md`.** Edit `readme_src/`, then run `python scripts/build_readme.py`.
5. **Don't hand-draw charts.** Add a function to `scripts/generate_diagrams.py`, label it DEMO CORPUS / TARGETS / DESIGN DIAGRAM, and regenerate.
6. **Trust rules change in `reference/heritage_core` first**, with a test. Services then consume the change.

### 73.2 Workflow

```bash
git switch -c feat/short-description
python -m pytest reference -q                  # must pass
python scripts/generate_diagrams.py            # if data or figures changed
python scripts/record_test_run.py              # refresh the §52 test listing
python scripts/build_readme.py                 # must report no missing images/anchors
git commit -m "feat: …"                        # conventional commits
```

Pull request checklist:

- [ ] Tests added or updated
- [ ] README regenerated (not hand-edited)
- [ ] No secrets, no uncleared content
- [ ] User-facing strings added in **all** i18n files, marked for native review
- [ ] Accessibility considered (keyboard path, contrast, captions)
- [ ] Discrepancies or new assumptions recorded in [§ 69](#69-discrepancies-between-source-documents) or marked `TBD`

### 73.3 Reporting a content problem

If you find an incorrect quote, a wrong page or date, or a rights concern, open an issue labelled `content-correction` or `rights-concern`. **Don't** post the disputed material itself in the issue. For takedown requests, use the takedown contact recorded in the handover bundle ([§ 65](#65-handover-bundle)).

---

## 74. License

| What | License | Notes |
|---|---|---|
| **Code** in this repository (`reference/`, `kiosk-agent/`, `scripts/`) | MIT (see [`LICENSE`](LICENSE)) | **Proposed default.** Confirm with the supervisor/institution before publishing. |
| **Documentation and generated figures** | Same as the code unless the institution decides otherwise | |
| **Prototype HTML** (`prototype/ambedkar_kiosk.html`) | The code is covered by the repository licence; **the embedded images and texts are not** | See [§ 72.2](#722-images-embedded-in-the-prototype) |
| **Historical content** (texts, scans, recordings, photographs) | **Not licensed by this repository** | Each item carries its own rights status in the rights register. Nothing here grants reuse rights. |

---

# Appendices

## Appendix A: Pi Setup Command Reference

> This is a reference procedure based on the design document's Appendix A. **Command syntax and package availability may vary with your Raspberry Pi OS release.** Record the release, hardware revision and screen model in the handover.

```bash
# ── 1. OS ───────────────────────────────────────────────────────────────
# Install Raspberry Pi OS (64-bit, desktop) with Raspberry Pi Imager:
#   hostname, non-default user, SSH (key only), Wi-Fi if required.
sudo apt update && sudo apt full-upgrade -y
sudo reboot

# ── 2. Dependencies (check installed defaults on your release) ─────────
sudo apt install -y python3-gpiozero python3-lgpio python3-venv chromium-browser
#   (newer releases may name the browser package `chromium`)
sudo apt install -y fonts-noto-core sqlite3 curl git     # Indic fonts, cache inspection, smoke tests

# ── 3. Python environment that can see Pi OS's hardware packages ──────
python3 -m venv --system-site-packages /home/pi/archive-env
/home/pi/archive-env/bin/python -c 'from gpiozero import Button; print("GPIO Zero ready")'

# ── 4. Code + UI ────────────────────────────────────────────────────────
mkdir -p /home/pi/archive && cd /home/pi/archive
git clone https://github.com/YOUR-ORG/ambedkar-heritage-archive-main.git src
ln -s src/kiosk-agent kiosk-agent
mkdir -p ui && cp src/prototype/ambedkar_kiosk.html ui/index.html
#   Later: build the React UI elsewhere; copy its static output into ui/.

# ── 5. Configuration (no admin secrets on the Pi) ──────────────────────
sudo install -d -m 0750 -o pi /etc/heritage-kiosk /var/lib/heritage-kiosk
sudo install -m 0600 -o pi src/.env.example /etc/heritage-kiosk/device.env
sudoedit /etc/heritage-kiosk/device.env

# ── 6. Services ─────────────────────────────────────────────────────────
sudo cp src/kiosk-agent/systemd/heritage-events.service /etc/systemd/system/
sudo cp src/kiosk-agent/systemd/heritage-gpio.service   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now heritage-events heritage-gpio

# ── 7. Kiosk browser autostart ──────────────────────────────────────────
mkdir -p ~/.config/autostart
cp src/kiosk-agent/autostart/heritage-kiosk.desktop ~/.config/autostart/
chmod +x src/kiosk-agent/start-kiosk.sh

# ── 8. Verify ───────────────────────────────────────────────────────────
pinout                                             # pin map on the device
systemctl is-active heritage-events heritage-gpio
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
vcgencmd measure_temp; vcgencmd get_throttled
journalctl -u heritage-gpio -n 50 --no-pager
```

*"If python3-lgpio or Chromium package names differ on your chosen OS image, follow the corresponding current Pi OS documentation rather than forcing an outdated pin library."* (design document, Appendix A)

---

## Appendix B: Ingestion Manifest Example

This example is **intentionally a fictional catalogue record** (design document, Appendix B). It does not claim ownership of any real Dr. Ambedkar work. **The published state is false until a permission record and a review record exist.**

<!-- GEN:ingestexample -->

It validates against [`contracts/ingest-manifest.schema.json`](contracts/ingest-manifest.schema.json) (test `test_design_doc_ingest_example_matches_schema`).

| Field | Rule |
|---|---|
| `id` | Stable, never reused, even after withdrawal |
| `rights.status` | Starts at `unknown` or `permission_pending`; only a permission record moves it on |
| `rights.public_display` / `ai_processing_allowed` | Independent decisions (`test_permissions_are_independent`) |
| `assets[role=master].sha256` | Computed on ingest by the worker, **never** typed by hand |
| `assets[role=access].uri` | Stays private until approved |
| `pages[].pdf_page_index` vs `printed_page_label` | Always both; they differ (`test_printed_page_differs_from_pdf_index`) |
| `pages[].reviewed` | `false` until a person has checked the text against the scan |

---

## Appendix C: Rebuilding the Documentation

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-docs.txt

node scripts/export_demo_corpus.js            # (optional) re-export data from the prototype HTML (Node ≥ 18)
python -m pytest reference -q                 # reference rules
python scripts/record_test_run.py             # verbatim test listing → docs/test_run.txt
python scripts/run_benchmark.py               # demo benchmark → diagrams/benchmark_results.json
python scripts/generate_diagrams.py           # every figure + diagrams/computed_metrics.json
python scripts/capture_screenshots.py         # (optional) prototype screenshots; needs playwright + chromium
python scripts/build_readme.py                # readme_src/*.md → README.md, checks images and anchors
```

| Script | Input | Output |
|---|---|---|
| `export_demo_corpus.js` | `prototype/ambedkar_kiosk.html` | `data/demo_corpus.json`, `data/i18n_strings.json` |
| `generate_diagrams.py` | `data/`, `reference/heritage_core` | `diagrams/*.png`, `diagrams/computed_metrics.json` |
| `capture_screenshots.py` | Prototype HTML | `docs/screenshots/*.png` |
| `record_test_run.py` | `reference/` | `docs/test_run.txt` |
| `run_benchmark.py` | `data/benchmark_demo.json` (or any file in the § 53.3 format) | `diagrams/benchmark_results.json` |
| `readme_tables.py` | All of the above + `contracts/` | Tables and embedded files for `<!-- GEN:… -->` markers |
| `build_readme.py` | `readme_src/*.md` | `README.md` + a check report |

The design document used `scripts/generate_visuals.py` and `scripts/build_document.py` to produce its PDF. This repository's scripts are independent re-implementations for the README and don't produce the PDF.

---

## Appendix D: JSON Schemas

These schemas are the **contracts between repositories**. They are embedded here from `contracts/`, and `reference/tests/test_contracts.py` checks that the reference implementation's real outputs validate against them.

<!-- GEN:schemas -->

---

## Appendix E: OpenAPI Excerpt

📐 **Specified, not implemented here.** It covers the routes whose behaviour is trust-critical. The endpoint list is in [§ 26](#26-api-specification).

<!-- GEN:openapi -->

Note the `404` on `/v1/items/{id}`: "unknown" and "not permitted" are **deliberately indistinguishable**, so the API doesn't reveal that a restricted item exists.

---

## Appendix F: Interface String Keys

The prototype's interface strings live in three dictionaries (`I18N`, `PART5_I18N`, `PART6_I18N`), merged per language. The UI's `t(key)` falls back to **English** when a key is missing. The coverage table below is generated from `data/i18n_strings.json`:

<!-- GEN:strings -->

**Findings:**

* **Hindi and Marathi** cover all 236 keys.
* **Telugu covers 70/236.** It covers the later-added screens (visitor outcomes, stories, test protocol, satisfaction prompt) but **not** the core navigation, categories, viewer or assistant, so a Telugu visitor sees mostly English. Complete it before claiming Telugu support.
* **No string has been reviewed by a native speaker.** All translations are marked for review.

### F.1 Key conventions for the production UI

| Rule | Example |
|---|---|
| `snake_case`, prefixed by screen or component | `ask_title`, `session_extend`, `qr_title` |
| Placeholders in braces, never string concatenation | `results`: "{n} item(s) · rights-filtered" |
| No HTML in strings except `<b>` | `offline_banner` |
| Keyboard help keys start with `k_` | `k_home`, `k_explore`, `k_tl`, `k_ask`, `k_read`, `k_pages`, `k_help`, `k_close` |
| Historical titles are **catalogue data**, not UI strings | Titles come from the item record in its language, with a translation badge |
| One JSON file per language: `i18n/en.json`, `hi.json`, `mr.json`, `te.json` | CI fails if a key exists in `en.json` but not in the others, unless it's listed in `i18n/pending.json` |

---

## Appendix G: Pre-Demonstration Checklist

Print this and tick it on the day.

**Content and rights**

- [ ] Every item shown is curator-verified: title, exact quotes, page identifiers, dates, media links
- [ ] Rights register printed; every shown item has a permission record ID
- [ ] Venue label removed or authorised (D-4)
- [ ] Uncleared images replaced or cleared (D-9; § 72.2)
- [ ] MP-002 / AV-002 rights corrected or hidden (D-3)
- [ ] The assistant's answerable question and out-of-scope question rehearsed

**Hardware**

- [ ] Official PSU; no under-voltage flag (`vcgencmd get_throttled` = `0x0`, or recorded)
- [ ] PIR aimed; wakes once; not near heat sources or windows
- [ ] HOME button firmly mounted and labelled
- [ ] No exposed wiring; enclosure closed
- [ ] Printed wiring diagram and HW-02 record on hand

**Software**

- [ ] Cold boot → attract screen tested today (time: ____ s)
- [ ] Manifest version current; expiry after the demo date
- [ ] Offline path tested today (Wi-Fi off → cached item opens → assistant "unavailable")
- [ ] Chromium relaunch tested (`pkill chromium`)
- [ ] Screen blanking disabled; volume at a reasonable level; captions on

**Evidence**

- [ ] One test-result sheet with **real measurements**
- [ ] The benchmark results table, failures included
- [ ] This README's § 69 discrepancy list, in case questions come up

**Fallbacks**

- [ ] Laptop with the prototype HTML (Device console) ready
- [ ] Screenshots of each demo step (`docs/screenshots/`)
- [ ] Ethernet cable / hotspot

---

## Appendix H: Figure Index

Every image in this README, how it was made, and where it first appears:

<!-- GEN:figures -->

---

<div align="center">

**Dr. B. R. Ambedkar Digital Heritage Archive**: an academic prototype.

*Replace all demo placeholder titles, exact quotes, page identifiers and media links with curator-verified material before a live public demonstration.*

</div>
