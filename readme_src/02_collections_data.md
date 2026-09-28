# Part B: Collections, Rights and Data

## 9. Collection Strategy

All five categories share **one common item model**, and each category adds its own type-specific fields. The model uses these terms:

* A **collection** is a group.
* An **item** is a work, record or media object.
* An **asset** is one particular file.
* A **page** or **transcript segment** is citable evidence.
* A **timeline event** is interpretation backed by evidence.

> [!CAUTION]
> A scan **does not become public** just because its URL is publicly visible elsewhere.

### 9.1 The five collection categories

| # | Collection | Small demo selection | Required identifying evidence | Showcase feature | Item `kind` |
|---|---|---|---|---|---|
| 1 | **Writings and speeches** | A few permission-cleared PDFs or page selections | Title, creator, edition, volume, publisher, printed page vs PDF page | Viewer + read/listen | `writing` |
| 2 | **Constitutional records** | Selected debates or verified excerpts | Debate date, official source, speaker, volume and printed page | Speaker/date filter + page citation | `constitutional` |
| 3 | **Manuscripts and photographs** | A few licensed scans or photos | Holding institution or photographer, accession/source URL, reproduction rights | Zoom and curator-supplied description | `manuscript_photo` |
| 4 | **Audio and video** | Cleared short recordings or interviews | Rights holder, creator, recording date, original vs synthetic status, timestamps | Captions + transcript seek | `media` |
| 5 | **Interpretive material** | Ten or more reviewed timeline cards | Event date, author/editor, evidence links, review date | Touch timeline → primary source | `interpretive` (+ `timeline_event`) |

### 9.2 Type-specific fields

| Field | writing | constitutional | manuscript_photo | media | interpretive |
|---|:---:|:---:|:---:|:---:|:---:|
| `creator` + role (`AUTHOR`, `EDITOR`…) | ● | ○ | ● (photographer) | ● | ● (editor) |
| `speaker` (verified) | ○ | ● | — | ● | — |
| `edition_label`, `volume_label` | ● | ● | — | — | — |
| `publisher` | ● | ● (e.g. official report) | — | — | — |
| `session_date` | — | ● | — | — | — |
| `holding_institution`, `accession_ref` | ○ | ○ | ● | ○ | — |
| `recording_date`, `recording_source` | — | — | — | ● | — |
| `media_kind` (`authentic`, `narration`, `interview`, `documentary`) | — | — | — | ● | — |
| `content_warning_if_appropriate` | ○ | ○ | ○ | ● | ○ |
| `transformations` (crop, enhance, transcribe, translate) | ● | ● | ● | ● | — |
| `event_date` or uncertainty interval | — | — | — | — | ● |
| `evidence[]` (≥ 1 approved) | — | — | — | — | ● |

● required · ○ optional · — not applicable

### 9.3 Candidate source inventory (not permission)

| Candidate source | Listed content | What the project may do **before** permission | What needs a recorded permission |
|---|---|---|---|
| Dr. Ambedkar Foundation publication catalogue | Collected works and translations | Catalogue entry, outbound link (`link_only`) | Mirroring PDFs, page images, AI processing, offline caching |
| Parliament Digital Library: historical debates catalogue | Constituent Assembly debates | Catalogue entry, outbound link | Mirroring, page images, AI processing |
| Wikimedia Commons and similar | Photographs with licence statements on the file page | Use as licensed, **with attribution**, after checking jurisdiction and original provenance | Anything beyond the stated licence |
| Holding institutions (manuscripts, photos) | Physical or digital holdings | Link-only listing, withheld details if requested | Scanning, display, download, derivatives |
| Oral-history interviewees | Modern recordings | Nothing public | Signed agreement covering display, AI processing and retention |

---

## 10. Rights Gate

Rights are **not one flag**. Display, download, translation/derivative and AI processing are **separate decisions**. A separate offline-cache decision is added because an offline Pi cannot receive urgent withdrawals.

### 10.1 Rights states

<div align="center">
<img src="diagrams/12_rights_states.png" alt="Rights states" width="860"/>
</div>

| State | Meaning | Public listing | Public search / AI / cache |
|---|---|:---:|:---:|
| `unknown` | Not assessed | ✗ | ✗ |
| `permission_pending` | Request sent or in negotiation | ✗ | ✗ |
| `public_display_approved` | Written permission recorded for display, with further flags for the other uses | ✓ (if published) | per flag |
| `restricted_to_staff` | Staff may view in the admin UI only | ✗ | ✗ |
| `link_only` | Catalogue card + outbound source reference only; no mirrored content | ✓ | ✗ |
| `withdrawn` | Takedown or permission revoked | ✗ | ✗ (cache purged on reconnect) |

> [!IMPORTANT]
> Material in `unknown` or `permission_pending` **must not** appear in public results and **must not** be sent to third-party AI providers.

### 10.2 The gate as code

The gate is implemented in [`reference/heritage_core/rights.py`](reference/heritage_core/rights.py). It fails closed on anything unexpected.

```python
from heritage_core.rights import RightsPolicy, Action, permitted

pol = RightsPolicy.from_state("public_display_approved")   # AI, offline and download default to False
permitted(pol, "published", Action.VIEW_ACCESS_COPY)       # True
permitted(pol, "published", Action.AI_CONTEXT)             # False: a separate decision
permitted(pol, "in_review", Action.LIST)                   # False: not published
permitted(RightsPolicy.from_state("link_only"), "published", Action.SEARCH_INDEX)  # False
```

<div align="center">
<img src="diagrams/13_rights_matrix.png" alt="Rights matrix" width="760"/>
</div>

### 10.3 Where the gate is enforced

| Enforcement point | Action checked | Failure behaviour |
|---|---|---|
| Building the public lexical and vector index | `SEARCH_INDEX` | Passage never indexed |
| `/v1/ask` evidence assembly | `AI_CONTEXT` (re-checked after retrieval) | Passage dropped; possibly abstain |
| Citation verification | `VIEW_ACCESS_COPY` | Abstain if a cited item is no longer visible |
| `/v1/items`, `/v1/collections`, timeline | `LIST` | Item omitted |
| `/v1/items/{id}/pages/{index}` and signed URLs | `VIEW_ACCESS_COPY` | 404 (not 403, to avoid confirming existence) |
| `/v1/offline-manifest` | `OFFLINE_CACHE` | Item not in the manifest; the Pi purges it on next sync |
| Reading-list QR hand-off | `DOWNLOAD` | QR not offered |

### 10.4 Rights register minimum columns

| Column | Example (fictional) |
|---|---|
| `item_id` | `DEMO-ITEM-001` |
| `rights_holder` | "Holding institution (verify)" |
| `permission_record_uri` | `private://permissions/2026-09-xx-letter.pdf` |
| `public_display` / `download_allowed` / `derivative_allowed` / `ai_processing_allowed` / `offline_cache_allowed` | `true / false / false / true / false` |
| `attribution_text` | Exact credit line required by the rights holder |
| `restrictions` | "No commercial use; kiosk display only" |
| `review_date` | `2026-09-26` |
| `reviewed_by` | Curator identity (not a developer) |
| `withdrawal_contact` | Named contact for takedown |

---

## 11. Provenance and Attribution Rules

These six rules come straight from the design document. The data model enforces them wherever it can.

| # | Rule | Enforcement |
|---|---|---|
| 1 | Keep **one immutable `source_uri` or accession reference** and a curator-entered description for each intake item | `archive_item.source_uri NOT NULL`; updates are audited |
| 2 | **Do not collapse** "authored by", "spoken by", "discusses", "edited by" and "portrays". These are different relations. | `relation` enum in the knowledge-map table; separate `creator` and `speaker` columns |
| 3 | Preserve **both the PDF index and the printed page label**. PDFs often include cover and front matter that the printed pagination doesn't reflect. | `page.pdf_page_index` and `page.printed_page_label` are separate columns. The demo shows CR-001 printed p. 978 = PDF index 6. |
| 4 | For debates, preserve the **session date** and the identity of the person **actually speaking**. Mentioning Ambedkar is not the same as his speaking. | `speaker` on `archive_item` and `transcript_segment`, verified flag |
| 5 | Record whether a photo or manuscript has been **cropped, enhanced, transcribed or translated**, and keep the original scan | `asset.role`, `asset.transformations[]`, master retained |
| 6 | A **curator must approve** event descriptions and displayed exact quotations. Generated summaries are marked generated and reviewable. | `review_status`, `answer_kind`, badge system ([§ 37](#37-source-badges)) |

### 11.1 Relation vocabulary

| Relation | Meaning | Example in the demo knowledge map |
|---|---|---|
| `AUTHORED` | Wrote the work | Ambedkar → *Annihilation of Caste* |
| `EDITED` | Edited or founded the publication | Ambedkar → *Mooknayak* |
| `SPOKE_AT` | Was the verified speaker at a session | Ambedkar → CAD 26 Nov 1949 |
| `CHAIRED` | Chaired the body | Ambedkar → Drafting Committee |
| `DISCUSSES` | Work discusses the subject | Work → subject |
| `DRAFTED` | Body drafted the record | Committee → Constitution |
| `PORTRAYS` | Image depicts the person | Photograph → person |
| `NARRATES` | Modern narration recounts an event | AV-001 → Dhamma Deeksha |
| `HELD_BY_CUSTODIAN` | Item is held by an institution | MP-003 |
| `EVIDENCED_BY` | Event supported by a page, passage or timestamp | timeline_event → page |

---

## 12. Demo Corpus Inventory

The prototype ships with a **small demonstration corpus**. It is exported verbatim to [`data/demo_corpus.json`](data/demo_corpus.json) so that the reference rules, the figures and this README all use the same data.

> [!WARNING]
> **The demo corpus is a placeholder.** The transcriptions are sample text. Several passages carry the note *"wording to be verified against the printed edition before production use."* Some source names are placeholders ("Image-use register — pending rights clearance"). Treat the whole corpus as fixture data for software tests, not as a historical resource.

<div align="center">
<img src="diagrams/20_demo_corpus.png" alt="Demo corpus composition" width="900"/>
</div>

### 12.1 Items

<!-- GEN:items -->

### 12.2 Citable passages (documents)

<!-- GEN:passages -->

### 12.3 Transcript segments (media)

<!-- GEN:segments -->

### 12.4 Observations from the inventory

| # | Observation | Consequence |
|---|---|---|
| O-1 | `AV-003` is `permission_pending`. The prototype hides it from the public listing; the curator console shows it with "rights gate locked". | ✅ Correct behaviour. The reference test `test_pending_item_never_cited` enforces it. |
| O-2 | `MP-003` is `link_only`. The prototype lists it as a card with a "LINK ONLY" badge and no mirrored content. | ✅ Matches the reference gate: `LIST` allowed, everything else denied |
| O-3 | `WS-005` (draft) and `MP-004` (in_review) are `public_display_approved` but not yet published | ✅ Not public until the second reviewer publishes ([§ 31](#31-curation-and-publication-workflow)) |
| O-4 | `MP-002` and `AV-002` are marked `public_display_approved`, but their source names say "pending rights clearance" / "clearance pending", and `AV-002` is also flagged for the offline cache | ⚠️ **Inconsistent demo data.** Under the rules in [§ 10](#10-rights-gate), pending clearance means `permission_pending`: not public and not cached. Fix before any public demo. See [§ 69](#69-discrepancies-between-source-documents). |
| O-5 | Five items are flagged for the offline cache (WS-001, CR-001, CR-003, MP-002, AV-002) | The reference manifest test asserts exactly this set. Remove MP-002 and AV-002 once O-4 is fixed. |
| O-6 | Media relevance for `AV-001` is item-level in the prototype's Q&A routes (no passage ID) | Production citations for media must point to `(item_id, start_ms, end_ms)` |

---

## 13. Data Model

<div align="center">
<img src="diagrams/14_data_model.png" alt="Logical data model" width="940"/>
</div>

### 13.1 Core entities and invariants

| Entity | Purpose | Key invariants |
|---|---|---|
| `collection` | Owning/curating body, collection name, scope, ingestion agreement | Every item belongs to exactly one collection |
| `rights_policy` | Allowed kiosk display, web display, downloads, derivative/translation use, permitted model processing, restrictions, review date | Separate booleans; `status` ∈ the rights states; `review_date` required when approved |
| `archive_item` | Item kind, title, author or speaker, subject tags, source URI or accession ID, date precision, language/script, edition/volume, review status | `source_uri NOT NULL`; creator roles distinct; `status` default `draft` |
| `asset` | Original and derivative files with different roles and URIs; media type, size, checksum, provenance, capture date, access control, version | A master's `sha256` is immutable; derivatives reference their master |
| `page` | Digital PDF index (base documented), printed page label, image URI, text, OCR confidence, reviewer | PDF index ≠ printed page; both stored |
| `passage` | Exact citable text span tied to a page, transcription version, review state, language, vector | Only `reviewed = true` passages may be quoted exactly |
| `transcript_segment` | Media item, start/end milliseconds, recognised words, speaker if verified, review status | `end_ms > start_ms` |
| `timeline_event` | Curator-authored claim, event date or uncertainty interval, review status, exhibition text | Public events need ≥ 1 approved evidence row |
| `event_evidence` | Join record pointing to an item, page, passage or timestamp | **Own primary key**, so one event can cite several passages of one item |
| `relation` (knowledge map) | Reviewed subject–predicate–object triples with evidence link, confidence and reviewer | Relation vocabulary from [§ 11.1](#111-relation-vocabulary) |
| `audit_log` | Who changed what, when, and why | Append-only |

### 13.2 Date precision

Historical dates vary in certainty. Every date is stored as a **label plus a machine interval**:

| `date_label` (displayed) | `date_from` | `date_to` | `date_precision` |
|---|---|---|---|
| `14 April 1891` | 1891-04-14 | 1891-04-14 | `day` |
| `1913` | 1913-01-01 | 1913-12-31 | `year` |
| `c.1935` | 1933-01-01 | 1937-12-31 | `circa` |
| `1946–c.1951` | 1946-01-01 | 1952-12-31 | `range_circa` |
| `YYYY-MM-DD (verify)` | NULL | NULL | `unverified` (never public) |

The timeline sorts by `date_from`. It **displays** `date_label`, so uncertainty stays visible.

---

## 14. Identifier and Citation Policy

### 14.1 Identifiers

* Assign **stable opaque IDs**. Never derive an ID only from a URL that may change.
* Store source URLs and accession numbers **separately** from IDs.
* Public items can have a human-readable permalink. **A permalink is not provenance.**
* The demo uses readable prefixes (`WS-`, `CR-`, `MP-`, `AV-`, `E-`, `SR-`) for teaching clarity. Production should use opaque IDs (for example ULIDs) and keep a separate display code.

| Object | Demo pattern | Production recommendation |
|---|---|---|
| Item | `WS-001` | ULID + display code |
| Passage | `WS001-P-b` | ULID; `(page_id, start_offset, end_offset, transcription_version)` unique |
| Transcript segment | `AV-001-T00` (reference) | ULID; `(item_id, start_ms, end_ms, version)` unique |
| Event | `E-1949` | ULID + display code |
| Source register | `SR-04` | Register row ID |

### 14.2 Checksums and transformations

For each scan, keep a **SHA-256 checksum of the bytes**. Record every transformation used to make access copies:

```json
{
  "asset_id": "01J8…",
  "role": "access",
  "derived_from": "01J7…(master)",
  "transformations": [
    {"op": "crop", "box": [120, 80, 2380, 3400], "by": "curator:rk", "at": "2026-09-20"},
    {"op": "resize", "max_px": 2400},
    {"op": "jpeg", "quality": 85}
  ],
  "sha256": "compute-on-write"
}
```

### 14.3 Citation format shown to visitors

The citation is **assembled by the server from catalogue metadata**. The model supplies only a passage ID.

```text
Constituent Assembly Debates — 26 November 1949
Official Report, Lok Sabha Secretariat · printed p. 978 · PDF page 7 (index 6)
Passage CR001-P-b · REVIEWED TEXT · [Open original page]
```

| Field | Source column | Never from |
|---|---|---|
| Title | `archive_item.title` | model text |
| Edition / volume | `archive_item.edition_label`, `volume_label` | model text |
| Printed page | `page.printed_page_label` | PDF index arithmetic |
| PDF page | `page.pdf_page_index` (+1 for display, base documented) | model text |
| Timestamp | `transcript_segment.start_ms` | model text |
| Link | `/v1/items/{id}/pages/{index}` or `/v1/items/{id}/media?t=` | model text |

> [!NOTE]
> The reference test `test_citation_built_from_catalogue_not_model` feeds in a model response claiming "page 9999". It asserts that the displayed citation still carries the catalogue's printed page.

---

## 15. Preservation versus Access

<div align="center">
<img src="diagrams/15_preservation_tiers.png" alt="Preservation tiers" width="880"/>
</div>

| Tier | Contents | Rules |
|---|---|---|
| **Preservation master** | The original institutional file, or a carefully captured archival scan | Record the checksum at ingest and at later fixity checks. **Never** overwrite it for OCR correction or web optimisation. Never served to the kiosk. |
| **Access derivative** | Resized page tile/JPEG or PDF, lower-bandwidth video, playback audio, caption file | Only derivatives the rights policy approves are served to visitors, via short-lived signed URLs or the offline bundle |
| **Processing derivative** | OCR/ASR candidate, layout data, embeddings, thumbnails, internal annotations | Can be regenerated, but **version** them when they underpin citations |
| **Backups** | At least one independent restoration path | A RAID array or a second disk inside the same kiosk is **not** an independent backup. Evaluate with the NDSA Levels of Digital Preservation (fixity, storage, metadata, security, formats). |

### 15.1 NDSA-style self-assessment (prototype target)

| Area | Prototype target | Future (institution) |
|---|---|---|
| Storage | Two copies of the demo masters in different locations (cloud bucket + offline drive held by the content lead) | Three or more copies, geographically separated, different storage technologies |
| Integrity | SHA-256 on ingest; manual fixity check before the demo | Scheduled fixity audits with alerting |
| Control | Named individuals with write access; audit log | Role-based access, separation of duties |
| Metadata | Descriptive + rights + technical in PostgreSQL; nightly export | Preservation metadata standard, replicated |
| Content | Accept only a few formats (TIFF/PDF/JPEG, WAV/MP4) | Format migration policy |

### 15.2 IIIF (deferred)

The IIIF Image and Presentation APIs suit interoperable page-image delivery and compound objects. The IIIF Content Search API can expose search results inside the page-view context. **These come after the base prototype works.** Implementing the whole IIIF stack is not a prerequisite for a class demo. See ADR-16.

---
