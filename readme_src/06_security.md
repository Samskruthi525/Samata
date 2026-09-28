# Part G: Security, Privacy and Governance

## 40. Security Controls

**Assume the physical Pi is untrusted.** Visitors can touch it, disconnect cables or try to exit Chromium. Kiosk mode, system permissions and an enclosure help, but **security-critical authorisation still lives in the cloud.**

| Control | Prototype implementation | Why it matters |
|---|---|---|
| **Transport** | HTTPS to the cloud; loopback-only Pi UI event endpoint | Prevents network interception and remote access to the hardware endpoint |
| **Device access** | A unique, short-lived or revocable, scoped credential per kiosk | A compromised Pi cannot administer the archive |
| **Admin access** | Distinct identity, MFA if available, review workflow | Visitors cannot publish or change rights |
| **Rights filter** | Enforced before both keyword and vector retrieval, and before download | Stops private material leaking into search, model context or the offline cache |
| **Secret handling** | Server secrets only on the backend; Pi config protected by OS permissions | No AI key in the React bundle or the public repository |
| **Prompt safety** | OCR and uploaded text treated as untrusted evidence, not instructions | A scanned document must not control the assistant |
| **Media handling** | Validate type and size, sanitise filenames, isolate workers | Reduces the ingestion attack surface |
| **Session privacy** | Delete the local query buffer and list on reset; voice capture is opt-in | A shared kiosk must not reveal the previous visitor's activity |
| **Incident response** | Withdraw item → block cloud access → invalidate the cache manifest | Respects takedowns; handles the offline-expiry limitation |

### 40.1 Kiosk hardening checklist (📐)

| # | Item | How |
|---|---|---|
| K-1 | Dedicated non-admin user runs Chromium | `useradd kiosk`; autologin for that user only |
| K-2 | No terminal or keyboard escape | Remove terminal launchers; disable `Ctrl+Alt+T`, `Alt+F4`, `Ctrl+W` via a Chromium policy/kiosk flags; a physical keyboard is not exposed |
| K-3 | Chromium restarts on exit | systemd user service or autostart wrapper with a restart loop |
| K-4 | Chromium policies | Disable dev tools, downloads, password manager, extensions and URL bar navigation; allow-list `127.0.0.1` |
| K-5 | SSH | Key-only, no password login, restricted to the operator network or disabled at the venue |
| K-6 | Updates | Scheduled window; version-pinned agent and UI bundle |
| K-7 | File permissions | `/etc/heritage-kiosk/*.env` mode 0600, owner `pi`/`kiosk`; cache DB 0600 |
| K-8 | Device credential | Scoped `kiosk:read kiosk:ask`; revocable server-side; rotated on reimage |
| K-9 | USB ports | Physically inaccessible to visitors |
| K-10 | Screen blanking | Disabled **only if** the venue needs it; recovery after power loss verified |

### 40.2 Secrets inventory

| Secret | Lives in | Never in |
|---|---|---|
| Model / OCR / ASR provider keys | Cloud secret manager → API/worker env | Git, the kiosk, the UI bundle |
| Database credentials | Cloud secret manager | Git, the kiosk |
| Manifest signing key | KMS (Ed25519, future) / secret manager (HMAC, prototype) | Git |
| Device credential | Pi `/etc/heritage-kiosk/device.env` (0600) | Git, the UI bundle, logs |
| Admin passwords / MFA seeds | Identity provider | Anywhere in this project |

A CI secret scanner ([§ 56](#56-ci-and-cd)) blocks commits that look like keys. `.env.example` files contain **names only**.

---

## 41. Threat Model

<div align="center">
<img src="diagrams/36_threat_controls.png" alt="Threat to control mapping" width="860"/>
</div>

| # | Threat (from the design document and prototype review) | Likely vector | Primary controls | Residual risk |
|---|---|---|---|---|
| T-1 | **Stolen Pi token** | Physical theft; SD card copied | Scoped, revocable device credential; rate limit; public-only data on the device | Attacker can read public data until the token is revoked |
| T-2 | **Unauthorised source replication** | Scraping the API or cache | Rights filter; signed short-lived URLs; rate limits; link-only mode | Public-display items can still be photographed off the screen (acceptable) |
| T-3 | **Prompt injection hidden in documents** | OCR text containing instructions | Evidence-not-instructions; flagging; ID verification | Model may still phrase an answer oddly; the citation check limits harm |
| T-4 | **False citations** | Model hallucination | Server-side ID verification; catalogue-built citations; abstention | Answer text may paraphrase imperfectly; label it AI SUMMARY |
| T-5 | **Malicious PDF/media files** | Uploaded ingest files | Type/size validation; sanitised filenames; isolated workers without credentials | Parser zero-days; patch cadence |
| T-6 | **Overly long retention of spoken queries** | Mic buffers, logs | Push-to-talk only; buffers cleared on reset; query text not logged | Provider-side retention (contract) |
| T-7 | **Visitor exits Chromium** | Keyboard shortcuts, crashes | Kiosk flags, policies, restart loop, no keyboard | Crash → brief desktop flash before restart |
| T-8 | **Offline cache of a withdrawn item** | Pi offline during a takedown | Manifest expiry + grace; low-risk items only | Exposure window ≤ expiry + grace |
| T-9 | **Device calls admin API** | Token misuse | Separate identity system; scope check → 403 + audit (SEC-01) | — |
| T-10 | **Event spoofing on the Pi** | Local process POSTs `home_pressed` | Loopback + allow-list; Unix socket hardening option | Only local, low impact (reset) |

---

## 42. Privacy and Session Handling

| Data | Collected? | Retention | Notes |
|---|---|---|---|
| Visitor identity | **No.** No login for public browsing. | — | NFR-05 |
| Question text | Sent to `/v1/ask` for processing | **Not stored** by the API. The audit keeps only length, status and device ID. The prototype logs `"ask: query received (N chars; text not stored)"`. | Provider retention per contract (`TBD`) |
| Voice | Only with push-to-talk | Buffer cleared on reset; not recorded continuously | Optional hardware |
| Reading list | In memory on the kiosk | Cleared on HOME/timeout. The QR hand-off link expires by itself (the prototype QR is a non-scannable demo). | No email or persistent identity |
| Motion / button events | On the Pi only | Not sent to the cloud | — |
| Visitor outcome counters | Anonymous counts: durations, screen names, feature counters | Rolled up nightly (future) | *"No names, no camera, no question text, no search text."* |
| Satisfaction prompt | Optional 3-level tap, 15 s auto-dismiss | Counted anonymously | Can be skipped |
| Device health | CPU temperature, uptime, cache version | Operational logs, retention `TBD` | No visitor data |

> [!NOTE]
> For a real government or institutional deployment, a responsible legal/security team must evaluate the applicable Indian privacy obligations, licences, retention rules and hosting policies. **This academic proposal does not assert that using any particular cloud provider satisfies those requirements.**

---

## 43. Governance

| Area | Rule | Owner |
|---|---|---|
| Content inclusion | Nothing becomes public without a recorded rights decision and curator review (Gate A) | Content lead + curator |
| Historical accuracy | A historian, librarian, faculty member or designated curator validates selected historical claims | Curator |
| Publication | Two different people: content approval and rights/publish | Curator + approver |
| Withdrawal | Any approver can withdraw immediately; the reason is recorded | Approver |
| Corrections | Corrections create a new transcription version and an audit row. Masters are untouched. | Curator |
| AI behaviour | The benchmark must pass (Gate D) before open-ended Q&A is shown publicly. Red-team findings are logged. | Search/AI lead |
| Cost | Daily AI-call caps; monthly review | Backend lead |
| Accessibility | ACCESS-01 findings tracked to closure or documented as limitations | UX lead |
| Change management | Tagged releases; the Pi fleet updates only from signed, versioned artefacts | Embedded lead |
| Attribution | Credit lines never removed; image-use register kept current | Content lead |

---
