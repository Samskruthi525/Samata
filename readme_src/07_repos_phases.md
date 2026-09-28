# Part H: Repositories and Development

## 44. Repository Architecture

<div align="center">
<img src="diagrams/28_repo_map.png" alt="Repository map" width="920"/>
</div>

The project uses **one documentation-and-contracts repository** (this one) and **five implementation repositories**. The shared trust rules are written once, in `reference/heritage_core`, and every service runs the same test vectors. Rules are not re-implemented differently in each repository.

| Repository | Language / stack | Purpose | Depends on | Status |
|---|---|---|---|---|
| **`ambedkar-heritage-archive-main`** (this) | Markdown, Python (docs + reference), JSON | README, architecture, contracts, reference rules + tests, UI prototype, demo corpus, figures | — | ✅ |
| `heritage-kiosk-agent` | Python 3.11+, GPIO Zero + lgpio, systemd | GPIO bridge, loopback event relay, health probe, manifest sync, cache DB | `heritage_core` (vendored wheel), contracts | 🧪 core files in `kiosk-agent/` here |
| `heritage-kiosk-ui` | React + TypeScript, Vite, i18n, Playwright | Static kiosk UI, served locally on the Pi | contracts (OpenAPI types) | 🧪 single-file prototype here |
| `heritage-archive-api` | Python 3.11+, FastAPI, PostgreSQL + pgvector, SQLAlchemy/psycopg | Public, device and admin routes; rights gate; RAG; manifest signing | `heritage_core`, contracts | 📐 |
| `heritage-ingest-worker` | Python, OCR/ASR engines (`TBD`), job table | Fixity, OCR, ASR, derivatives, embeddings | `heritage_core`, contracts | 📐 |
| `heritage-infra` | IaC (tool `TBD`), shell | Environments, backups, monitoring, secrets wiring (names only) | — | 📐 |

### 44.1 Why this split?

| Concern | Decision |
|---|---|
| Different deployment targets (Pi vs cloud vs static) | Separate repos with separate release cadences |
| Shared trust rules | One Python package (`heritage_core`), versioned, consumed as a wheel |
| Shared API shapes | `contracts/` holds OpenAPI + JSON Schemas. The UI generates TS types; the API validates against them. |
| Avoid duplicated code | The UI never re-implements rights logic. It displays what the API returns and uses the offline cache DB built by the agent. |
| Small team | A monorepo would also work. If you choose one, keep the same folder boundaries as packages. |

### 44.2 Repository links

| Repository | URL (placeholder) |
|---|---|
| Main | `https://github.com/YOUR-ORG/ambedkar-heritage-archive-main` |
| Kiosk agent | `https://github.com/YOUR-ORG/heritage-kiosk-agent` |
| Kiosk UI | `https://github.com/YOUR-ORG/heritage-kiosk-ui` |
| Archive API | `https://github.com/YOUR-ORG/heritage-archive-api` |
| Ingest worker | `https://github.com/YOUR-ORG/heritage-ingest-worker` |
| Infra | `https://github.com/YOUR-ORG/heritage-infra` |

Replace `YOUR-ORG` once the organisation is decided. See also [`repository-links.md`](repository-links.md).

---

## 45. Folder Structures

### 45.1 This repository (`ambedkar-heritage-archive-main`)

```text
ambedkar-heritage-archive-main/
├── README.md                         # GENERATED — edit readme_src/ instead
├── LICENSE                           # MIT for code (proposed default, §74); content has its own rights
├── .gitignore                        # blocks .env, keys, masters/, *.tif
├── .env.example                      # variable NAMES + safe placeholders only
├── requirements-docs.txt             # matplotlib, numpy, pytest, jsonschema (+ optional playwright)
├── repository-links.md
├── .github/workflows/ci.yml          # tests → figures → README build → diff check
├── readme_src/                       # README source parts, concatenated in order
│   ├── 00_header.md                  # banner, status, TOC, quick start
│   ├── 01_understanding.md           # Part A  §1–8
│   ├── 02_collections_data.md        # Part B  §9–15
│   ├── 03_embedded.md                # Part C  §16–24
│   ├── 04_cloud.md                   # Part D  §25–31
│   ├── 05_search_ui.md               # Parts E–F §32–39
│   ├── 06_security.md                # Part G  §40–43
│   ├── 07_repos_phases.md            # Part H  §44–48
│   ├── 08_verification.md            # Part I  §49–53
│   ├── 09_operations.md              # Part J  §54–60
│   ├── 10_planning.md                # Part K  §61–69
│   └── 11_reference.md               # Part L  §70–74 + Appendices A–H
├── scripts/
│   ├── generate_diagrams.py          # every figure (matplotlib only) + computed_metrics.json
│   ├── build_readme.py               # concatenate + inject GEN blocks + check files/images/anchors
│   ├── readme_tables.py              # data-driven tables and embedded files (GEN markers)
│   ├── record_test_run.py            # verbatim pytest listing → docs/test_run.txt
│   ├── run_benchmark.py              # benchmark file → diagrams/benchmark_results.json
│   ├── export_demo_corpus.js         # prototype HTML → data/*.json (Node ≥ 18)
│   └── capture_screenshots.py        # headless Chromium screenshots of the prototype
├── prototype/
│   └── ambedkar_kiosk.html           # working single-file kiosk UI prototype
├── data/
│   ├── demo_corpus.json              # 14 items · 14 events · KM · stories · tests · Q&A routes · image credits
│   ├── i18n_strings.json             # interface strings per language (EN/HI/MR/TE)
│   └── benchmark_demo.json           # 8 answerable + 13 negative probes (§52.4)
├── reference/
│   ├── conftest.py
│   ├── heritage_core/
│   │   ├── __init__.py
│   │   ├── rights.py                 # rights gate (fail-closed)
│   │   ├── corpus.py                 # typed loading of the demo corpus
│   │   ├── retrieval.py              # BM25 + trigram stand-in + RRF, rights-first
│   │   ├── answer_contract.py        # RAG contract: verify IDs, catalogue citations, abstain
│   │   ├── manifest.py               # signed, versioned, expiring offline manifest
│   │   ├── kiosk_state.py            # visitor state machine
│   │   ├── metrics.py                # CER, WER, P@k, MRR, citation validity
│   │   └── sizing.py                 # storage scenarios
│   └── tests/                        # pytest suite (listing in §52.1)
├── kiosk-agent/
│   ├── pi_gpio_bridge.py             # PIR/HOME → loopback endpoint
│   ├── local_event_service.py        # POST /device/event → SSE /device/stream (+ optional static UI)
│   ├── cache_schema.sql              # offline cache (SQLite + FTS5), tested
│   ├── start-kiosk.sh                # Chromium kiosk relaunch loop
│   ├── autostart/heritage-kiosk.desktop
│   └── systemd/
│       ├── heritage-events.service
│       └── heritage-gpio.service
├── contracts/
│   ├── ask-response.schema.json
│   ├── offline-manifest.schema.json
│   ├── ingest-manifest.schema.json
│   ├── openapi-excerpt.yaml
│   └── examples/ingest-demo-item-001.json
├── schema/
│   └── archive.sql                   # catalogue schema (from §27; parses with the PostgreSQL parser)
├── architecture/README.md            # pointers into README sections
├── documentation/README.md           # operator-facing pointers
├── diagrams/                         # generated PNGs + computed_metrics.json
└── docs/
    ├── screenshots/                  # generated prototype screenshots
    └── test_run.txt                  # recorded test listing
```

### 45.2 `heritage-kiosk-agent`

```text
heritage-kiosk-agent/
├── pyproject.toml
├── src/heritage_agent/
│   ├── __main__.py                   # entry: runs bridge + sync loop + health reporter
│   ├── bridge.py                     # = kiosk-agent/pi_gpio_bridge.py (Bridge, loopback_only)
│   ├── events.py                     # = kiosk-agent/local_event_service.py
│   ├── sync.py                       # manifest pull, verify, atomic apply, asset fetch
│   ├── cache_db.py                   # SQLite schema (§20.4), FTS5 queries
│   ├── health.py                     # CPU temp, throttling flags, cache version (no visitor data)
│   └── config.py                     # env parsing, defaults, validation
├── systemd/
│   ├── heritage-gpio.service
│   ├── heritage-events.service
│   ├── heritage-sync.service
│   └── heritage-sync.timer
├── kiosk/
│   ├── chromium-kiosk.sh             # launches Chromium --kiosk on the local UI
│   └── chromium-policies.json
├── tests/
│   ├── test_bridge.py                # mock pin factory (GPIOZERO_PIN_FACTORY=mock)
│   ├── test_sync.py
│   └── vectors/                      # shared vectors from heritage_core
└── .env.example
```

### 45.3 `heritage-kiosk-ui`

```text
heritage-kiosk-ui/
├── package.json · tsconfig.json · vite.config.ts
├── src/
│   ├── main.tsx · App.tsx
│   ├── api/                          # generated from contracts/openapi.yaml
│   ├── device/useDeviceEvents.ts     # SSE subscription (§22.3)
│   ├── session/                      # idle timer, countdown, resetSession()
│   ├── screens/
│   │   ├── Attract.tsx · Home.tsx · Explore.tsx · Viewer.tsx · Timeline.tsx
│   │   ├── Stories.tsx · KnowledgeMap.tsx · Ask.tsx · Media.tsx · ReadingList.tsx
│   ├── components/Badge.tsx · CitationChip.tsx · OfflineBanner.tsx · Countdown.tsx
│   ├── i18n/en.json · hi.json · mr.json · te.json
│   └── styles/tokens.css             # palette from the prototype (:root variables)
├── e2e/                              # Playwright: HW-03 (simulated), NET-01, LANG-01, ACCESS-01 checks
└── public/
```

### 45.4 `heritage-archive-api`

```text
heritage-archive-api/
├── pyproject.toml · Dockerfile
├── app/
│   ├── main.py                       # FastAPI app, routers, middleware
│   ├── auth.py                       # device tokens (scopes) · admin identity + MFA
│   ├── rights.py                     # thin wrapper over heritage_core.rights
│   ├── routes/ health.py · collections.py · items.py · timeline.py · search.py · ask.py
│   │          · offline_manifest.py · admin.py
│   ├── rag/ index.py · model_client.py · verifier.py   # verifier = heritage_core.answer_contract
│   ├── storage.py                    # signed URLs (short TTL), never masters
│   ├── audit.py
│   └── settings.py                   # env-only config
├── migrations/0001_init.sql          # §27
├── tests/ unit/ · contract/ · vectors/ · security/ (SEC-01, rate limits)
└── .env.example
```

### 45.5 `heritage-ingest-worker`

```text
heritage-ingest-worker/
├── worker/
│   ├── main.py                       # job loop (SKIP LOCKED)
│   ├── jobs/ fixity.py · ocr.py · asr.py · derive.py · embed.py · thumb.py
│   ├── validate.py                   # type/size checks, filename sanitising
│   └── engines/                      # adapters; engine + version recorded per output
├── tests/
└── Dockerfile                        # no admin creds; read-only master mount
```

### 45.6 `heritage-infra`

```text
heritage-infra/
├── envs/ dev/ · staging/ · pilot/
├── modules/ database/ · storage/ · api/ · worker/ · monitoring/ · backup/
├── scripts/ backup_db.sh · restore_db.sh · fixity_audit.sh · rotate_device_token.sh
└── README.md                         # secret NAMES and where they are injected; never values
```

---

## 46. Configuration and Environment Variables

All configuration comes from the environment. `.env.example` files list **names only**.

### 46.1 Kiosk agent (Pi)

| Variable | Default | Description |
|---|---|---|
| `KIOSK_EVENT_URL` | `http://127.0.0.1:8765/device/event` | Loopback endpoint (the bridge rejects non-loopback hosts) |
| `KIOSK_PIR_PIN` | `17` | BCM pin for PIR OUT |
| `KIOSK_HOME_PIN` | `27` | BCM pin for HOME |
| `KIOSK_LED_PIN` | `22` | BCM pin for the status LED; empty disables it |
| `KIOSK_PIR_COOLDOWN_S` | `10` | Suppress repeated PIR wakes |
| `KIOSK_PIR_WARMUP_S` | `30` | `TBD` per module datasheet |
| `KIOSK_IDLE_S` | `120` | Idle before the warning |
| `KIOSK_COUNTDOWN_S` | `20` | Warning countdown |
| `KIOSK_DEVICE_ID` | `DEMO-KIOSK-01` | Label only |
| `KIOSK_API_BASE` | `https://api.example.invalid` | Cloud API base (placeholder) |
| `KIOSK_DEVICE_TOKEN` | *(secret; in `/etc/heritage-kiosk/device.env`, 0600)* | Scoped device credential |
| `KIOSK_MANIFEST_KEY` | *(secret, prototype HMAC)* | Replaced by `KIOSK_MANIFEST_PUBKEY` (Ed25519) later |
| `KIOSK_MANIFEST_GRACE_H` | `24` | Grace after expiry before failing closed |
| `KIOSK_SYNC_INTERVAL_S` | `CONFIGURABLE` (e.g. 900) | Manifest sync period |
| `KIOSK_CACHE_DIR` | `/var/lib/heritage-kiosk` | Cache DB + assets |
| `GPIOZERO_PIN_FACTORY` | `lgpio` on Pi 5; `mock` for development | GPIO Zero backend |

### 46.2 Archive API

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL DSN (secret) |
| `OBJECT_STORE_BUCKET_MASTERS` / `…_DERIVATIVES` | Bucket names |
| `SIGNED_URL_TTL_S` | Short TTL for access-copy URLs (e.g. 300) |
| `MODEL_PROVIDER` / `MODEL_NAME` / `MODEL_API_KEY` | Model settings (key secret) |
| `EMBEDDING_MODEL` / `EMBEDDING_DIM` | Must match `passage.embedding` |
| `ASK_DAILY_CAP` | Global daily AI-call cap |
| `ASK_PER_DEVICE_PER_MIN` | Rate limit |
| `ASK_MIN_COVERAGE` | Evidence-sufficiency threshold (reference 0.5) |
| `MANIFEST_SIGNING_KEY` | HMAC (prototype) or KMS key ID (future) |
| `MANIFEST_TTL_H` | Manifest expiry |
| `ADMIN_IDP_ISSUER` / `ADMIN_IDP_AUDIENCE` | Admin identity provider |
| `LOG_LEVEL` | `INFO` by default; never log query text |

---

## 47. Development Phases

The academic prototype is delivered in **six one-week phases** (design doc §13), preceded by a short **Phase 0** and followed by **handover**. Every phase uses the same format:

* **Objective**
* **Entry criteria**
* **Work packages by role**
* **Deliverables**
* **Exit criteria (evidence)**
* **Risks**
* **Definition of done**

<div align="center">
<img src="diagrams/22_six_week_gantt.png" alt="Six-week plan" width="920"/>
<br/>
<img src="diagrams/23_decision_gates.png" alt="Decision gates" width="920"/>
</div>

**Roles** (suggested four-person team, [§ 48](#48-team-and-responsibilities)):

| Code | Role |
|---|---|
| **EMB** | Embedded / physical build |
| **UI** | Kiosk UI / accessibility |
| **CLD** | Cloud / catalogue / rights |
| **AI** | Search / AI / OCR + curation coordination |
| **CUR** | External curator / historian / faculty reviewer |

### Phase summary

| Phase | Week | Theme | Exit artefact (design doc) | Gate |
|---|---|---|---|---|
| 0 | before W1 | Setup | Repos, accounts, rights register template, hardware order | — |
| 1 | W1 | Foundations | Working touch display; documented connection sheet; five-category sample manifest | **A** (content, started), **B** (hardware) |
| 2 | W2 | Skeleton end-to-end | Cloud `/health` and public items; Pi wakes and resets | — |
| 3 | W3 | Evidence surfaces | Open at least one original page and one captioned media item | **C** (retrieval readiness) |
| 4 | W4 | Search | Top-five search benchmark and linkable results | — |
| 5 | W5 | Trustworthy answers + offline | Cite-and-open question flow; Wi-Fi-off exhibit | **D** (AI) |
| 6 | W6 | Validation | Test report, source/rights register, final prototype and handover | **E** (presentation) |
| 7 | after W6 | Handover | Handover bundle ([§ 65](#65-handover-bundle)) | — |

---

### Phase 0: Setup (before Week 1)

**Objective.** Remove blockers so Week 1 can start building.

**Entry criteria.** Team formed; supervisor and curator identified.

| Role | Work packages |
|---|---|
| EMB | Order the Pi 5 (8 GB), 27 W PSU, active cooler, case, touchscreen, microSD/SSD, PIR, button, LED + 1 kΩ, meter access. Check lead times. |
| UI | Review `prototype/ambedkar_kiosk.html`; list what carries over to React; set up the `heritage-kiosk-ui` scaffold |
| CLD | Create cloud account(s) with budget alerts; create the repos; set up the secret store; copy the rights register template ([§ 10.4](#104-rights-register-minimum-columns)) |
| AI | Draft the candidate item list across the five categories with the curator; draft the benchmark question categories ([§ 53](#53-benchmark-set-design)) |
| CUR | Agree the review responsibilities and turnaround time |

**Deliverables.** Repositories with CI running the reference tests; hardware order confirmation; rights register v0; candidate list v0.

**Exit criteria.** `python -m pytest reference -q` passes in CI on every repository that vendors `heritage_core`.

**Risks.** Hardware delivery delay → borrow a touchscreen; the design document explicitly suggests borrowing to control cost.

**Definition of done.** Everyone can clone, run the tests and open the prototype.

---

### Phase 1 (Week 1): Foundations

**Objective.** Finalise the sample list and rights register; bring up the hardware safely.

**Entry criteria.** Hardware delivered (or borrowed); rights register template exists.

| Role | Work packages |
|---|---|
| EMB | Install Pi OS with Raspberry Pi Imager; `apt full-upgrade`; install `python3-gpiozero python3-lgpio python3-venv chromium-browser` ([Appendix A](#appendix-a-pi-setup-command-reference)). Test the screen, touch calibration and audio. **Measure PIR OUT high on the bench (HW-02 step 1–3)** before any GPIO connection. Wire the HOME button (BCM27/pin 13 ↔ GND/pin 14). Record the connection sheet with photos. |
| UI | Define the design tokens from the prototype `:root`; build the Attract and Home skeleton; set up i18n files (en, hi, mr, te) with the keys from [Appendix F](#appendix-f-interface-string-keys) |
| CLD | Provision PostgreSQL (with pgvector if available) and private object storage; apply `migrations/0001_init.sql` in dev |
| AI | Build the five-category sample manifest (≥ 1 item per category, ≥ 10 timeline cards) using [Appendix B](#appendix-b-ingestion-manifest-example); request permissions |
| CUR | Review the candidate list; mark which items can be public, link-only or excluded |

**Deliverables.**
* Working touch display.
* **Documented connection sheet**: pin table, photos, measured PIR voltage.
* **Five-category sample manifest** with rights states.
* Hardware checklist items S-1…S-10 ticked.

**Exit criteria (evidence).**
* HW-01: stable boot, no low-power warning, touch works. Record the date and the Pi OS release.
* **Gate B passed**: PIR OUT ≤ 3.3 V (or shifted) measured and recorded; display power verified.
* **Gate A started**: every candidate item has a rights state; nothing is `public_display_approved` without a permission record.

**Risks.**
* 5 V PIR output → level shifter.
* A touchscreen that doesn't present as USB HID → swap the model.
* Slow rights responses → fall back to `link_only` plus a small set of cleared items.

**Definition of done.** The screen shows the Pi desktop, touch works, the button and PIR are verified with the GPIO Zero one-liners, and the manifest is saved in the repo (no secrets).

---

### Phase 2 (Week 2): Skeleton end-to-end

**Objective.** Get a thin vertical slice working: the cloud serves public items and the Pi wakes and resets.

**Entry criteria.** Gate B passed; database provisioned.

| Role | Work packages |
|---|---|
| EMB | Install `pi_gpio_bridge.py` + `local_event_service.py` as systemd services ([§ 22.4](#224-systemd-unit)). Add PIR cooldown and warm-up. Launch Chromium in kiosk mode pointing at the **local** UI. Verify NFR-08 (boot with the network unplugged). |
| UI | Subscribe to `/device/stream`; implement `wake()` and `resetSession()` per [§ 20.3](#203-session-reset-policy); build Explore browse cards against `/v1/collections` and `/v1/items` |
| CLD | Implement `/v1/health`, `/v1/collections`, `/v1/items`, `/v1/items/{id}` with the rights gate (`public_item` view). Add the admin draft form (`POST /v1/admin/items`, status `draft`). Issue a device token with scopes `kiosk:read`. |
| AI | Load the approved sample items; compute SHA-256 for each master; store access derivatives |
| CUR | Review the first item descriptions |

**Deliverables.** A PIR wake and HOME reset that are real (not simulated); a public items API; an admin draft form.

**Exit criteria (evidence).**
* HW-03: HOME returns Home, stops playback and clears state. Record 10 trials.
* HW-02 (second half): approaching the kiosk wakes the UI **once**, not in a loop.
* `curl /v1/items` returns only published, rights-approved items (DOC-02 precursor).
* SEC-01 precursor: the device token gets 403 on `/v1/admin/*`.

**Risks.** Chromium flags changing between Pi OS releases → document the release and flags used.

**Definition of done.** Walking up to the kiosk shows Home with real categories from the cloud, and the physical button resets it.

---

### Phase 3 (Week 3): Evidence surfaces

**Objective.** Make evidence inspectable: pages, alignment, captions and timeline links.

**Entry criteria.** Items served; derivatives stored.

| Role | Work packages |
|---|---|
| EMB | Measure cold-boot → ATTRACT time and PIR → Home latency (record them; no targets are invented). Start the HW-04 soak (continuous run). |
| UI | Document viewer: scan + reviewed text side by side, printed page vs PDF index, zoom, reviewed/OCR toggle, "go to source". Media player: captions on by default, transcript seek, AUTHENTIC/NARRATION badge. Timeline screen. |
| CLD | `/v1/items/{id}/pages/{index}`, `/v1/items/{id}/media`, `/v1/timeline`; signed URLs with a short TTL |
| AI | OCR/extract the sample pages; align passages to pages; produce `.vtt` + transcript segments; attach timeline evidence (`event_evidence`, own ID) |
| CUR | Review the transcriptions of cited passages; approve the timeline card texts |

**Deliverables.** At least one original page opened from a result, and at least one captioned media item with transcript seek.

**Exit criteria (evidence).**
* DOC-01: a known title/quotation opens the correct verified item and printed page, not just matching PDF text.
* AV-01: a transcript cue jumps to the correct timestamp; captions are available.
* **Gate C passed**: page alignment and readable access copies validated **before** the chatbot is enabled.

**Risks.**
* OCR quality on Devanagari → show the page image with "transcription pending".
* Page off-by-one between PDF index and printed page → test with the alignment sheet.

**Definition of done.** Every public passage resolves to a visible page image or timestamp.

---

### Phase 4 (Week 4): Search

**Objective.** Hybrid search over reviewed passages, with a fixed expert-reviewed question set.

**Entry criteria.** Gate C passed.

| Role | Work packages |
|---|---|
| EMB | Build the offline cache DB (SQLite FTS5) from a hand-made manifest; test offline keyword search |
| UI | Search box with filters (category, year, language, sort); result → viewer at the target page/time |
| CLD | `/v1/search`; index build job; rights filter at index build **and** query time |
| AI | Choose the embedding model (record the name, version and dimension); populate `passage.embedding`; implement fusion (RRF) and reviewed boost as in `heritage_core.retrieval`; assemble the **fixed question set** ([§ 53](#53-benchmark-set-design)); run P@5/MRR |
| CUR | Label the relevant passages for each benchmark question **before** evaluation |

**Deliverables.** A top-five search benchmark with results and linkable hits.

**Exit criteria (evidence).**
* A benchmark table with P@5, Hit@5, MRR and **failing examples listed**.
* No `permission_pending` or `link_only` passage appears in any result (automated check).

**Risks.** Alias gaps (like "poona pact" in the demo) → add curated aliases, tags and relations; re-run.

**Definition of done.** The search results table is in the test report, with the corpus version and model version.

---

### Phase 5 (Week 5): Trustworthy answers and offline

**Objective.** A cited Q&A flow with abstention; the permission filter; a signed offline bundle; translation labels; security checks.

**Entry criteria.** Search benchmark recorded.

| Role | Work packages |
|---|---|
| EMB | Manifest sync loop ([§ 24.3](#243-sync-loop-in-the-kiosk-agent)); atomic apply; revocation purge; fail-closed display; NET-01/NET-02 rehearsal |
| UI | Ask screen: AI SUMMARY badge, citation chips, NOT VERIFIED state, offline-disabled state; translation badge; offline banner |
| CLD | `/v1/offline-manifest` (signed); `/v1/admin/items/{id}/publish` and `/withdraw` with two-person enforcement; audit; rate limits and the daily AI cap; secret scan of the UI bundle |
| AI | `/v1/ask` implementing [§ 33](#33-rag-answer-contract) with `heritage_core.answer_contract` verification; guard instruction; injection test document (RAG-03); run RAG-01/RAG-02 on the benchmark |
| CUR | Check that the cited passages genuinely support the answers (answer-support metric) |

**Deliverables.** Cite-and-open question flow; Wi-Fi-off exhibit.

**Exit criteria (evidence).**
* **Gate D passed**:
  * 100 % of produced citations resolve to permitted page/time (citation validity).
  * All out-of-scope questions abstain.
  * No citation to a non-retrieved passage.
  * The reviewer-verified answer-support rate is recorded.
* NET-01: the cached exhibit is usable, the offline state is clear, no frozen spinner.
* NET-02: reconnecting with a newer manifest updates atomically; revoked items are removed.
* SEC-01: an admin call from the device identity is denied and an audit entry is written.
* DOC-02: an item in `permission_pending` is absent from listing, search, Q&A context and the offline bundle.

**Risks.**
* Model cost → caching, caps.
* Model over-answering → tighten the coverage threshold; fall back to "links without a declarative answer".

**Definition of done.** The assistant can be shown in public with confidence that it will abstain rather than invent.

---

### Phase 6 (Week 6): Validation and rehearsal

**Objective.** Visitor and accessibility tests, error polish, metrics capture, and a demo rehearsal **in the venue**.

**Entry criteria.** Gates A–D passed.

| Role | Work packages |
|---|---|
| EMB | Complete the HW-04 soak for the agreed demo period; record thermal behaviour; image the SD card (recovery method) |
| UI | ACCESS-01 (keyboard, screen-reader inspection, headphones, contrast, text size, timeout); fix findings or document them as limitations |
| CLD | Backups and a restore test ([§ 57](#57-backups-and-restore)); monitoring alert test |
| AI | Final benchmark run; OCR-01 per-script CER/WER on the sampled pages; LANG-01 |
| ALL | Visitor sessions with personas P1–P5; time-to-find, completion rate, optional satisfaction tap; rehearse the ten-minute script ([§ 64](#64-demonstration-script)) twice, once with Wi-Fi off |
| CUR | Final sign-off of the displayed quotations and timeline texts |

**Deliverables.** Test report; source/rights register; final prototype; handover bundle draft.

**Exit criteria (evidence).**
* **Gate E passed**: network-off demo and visitor reset tested **in the venue**, not only at a desk.
* Every protocol test has an observed result, date and tester in [§ 50](#50-test-protocol).

**Risks.**
* Venue lighting or glare → adjust the angle.
* Venue Wi-Fi captive portal → use Ethernet or a pre-authorised network.

**Definition of done.** The ten-minute demo runs start to finish twice without intervention.

---

### Phase 7: Handover (after Week 6)

**Objective.** Leave a system someone else can run, recover and withdraw content from.

| Deliverable | Detail |
|---|---|
| Live demo kiosk | Stable auto-start; labelled wiring record and sensor-voltage measurements |
| Source repositories | Dependency versions, setup instructions and deployment configuration templates **without secrets** |
| Content | Curated five-category sample inventory and rights/attribution register |
| Evidence mapping | Original-to-derivative mapping, citation reference sheet, documented page/timestamp alignment |
| QA report | Test questions, OCR samples, user feedback, security/offline results and known limitations |
| Recovery | Disk/OS image, database backup, offline bundle version and a **contact for item withdrawal** |

---

### Post-prototype phases (⏳, not part of the class demo)

| Phase | Scope | Prerequisites |
|---|---|---|
| **P2 — Institution pilot** | Permission agreements; collection policy; multi-kiosk fleet; on-site or approved hybrid infrastructure; professional digitisation; restoration drills; security and accessibility audit | Institutional partner, legal review, budget |
| **P3 — Wider archive** | IIIF where useful; distributed curatorial workflows; name authority and knowledge graph; more Indian languages; research accounts where justified; legally authorised external collection links | P2 success, curatorial capacity |

See [§ 67](#67-scale-up-roadmap).

---

## 48. Team and Responsibilities

The suggested four-person team is: (1) embedded/physical build, (2) kiosk UI/accessibility, (3) cloud/catalogue/rights, (4) search/AI/OCR plus curation coordination. A historian, librarian, faculty member or designated curator validates selected historical claims.

### 48.1 RACI

R = Responsible · A = Accountable · C = Consulted · I = Informed

| Activity | EMB | UI | CLD | AI | CUR | Supervisor |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Hardware purchase and wiring | **R/A** | I | I | I | — | C |
| Electrical safety checks | **R/A** | I | — | — | — | C |
| Kiosk OS and Chromium kiosk | **R/A** | C | I | — | — | I |
| Kiosk UI and accessibility | C | **R/A** | I | C | C | I |
| Rights register | I | I | **R** | C | **A** | I |
| Catalogue, API, security | I | C | **R/A** | C | — | I |
| OCR, alignment, embeddings | — | — | C | **R/A** | C | I |
| Historical review | — | — | — | C | **R/A** | I |
| RAG contract and benchmark | — | C | C | **R/A** | C | C |
| Offline manifest and sync | **R** | C | **A** | I | — | I |
| Test report | R | R | R | R | C | **A** |
| Demo rehearsal | R | R | R | R | C | **A** |

---
