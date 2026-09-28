# Part C: The Embedded Kiosk

## 16. Hardware Bill of Materials

> [!NOTE]
> Get **current local quotations**. Prices are deliberately left out: the design document says a precise rupee budget needs current quotations, what equipment the campus already has, and the licensing situation. See [§ 61](#61-cost-drivers).

| # | Part | Qty | Prototype specification and trade-off | Essential? | Verified by |
|---|---|:---:|---|:---:|---|
| 1 | **Raspberry Pi 5** | 1 | 8 GB preferred for Chromium plus the local service. 4 GB may work with smaller page assets. | **Yes** | HW-01, HW-04 |
| 2 | **Raspberry Pi 27 W USB-C supply** or a verified equivalent | 1 | The recommended supply for Pi 5. Evaluate the real load and the USB peripheral draw. | **Yes** | HW-01 (no low-power warning) |
| 3 | **Active cooler + vented case** | 1 each | Continuous video and browser use needs thermal validation | **Yes** | HW-04 |
| 4 | **HDMI capacitive touchscreen** | 1 | About 10–15 inches with USB touch input. Verify power, mounting and Linux compatibility. | **Yes** | HW-01 (touch calibration) |
| 5 | **Storage** | 1 | 64–128 GB quality microSD. An SSD is recommended when large media is cached often. | **Yes** | Cache sync test |
| 6 | **Momentary large-button switch** | 1 | Accessible HOME button. Needs physical mounting and strain relief. | **Yes** | HW-03 |
| 7 | **3.3 V-compatible PIR module/output** | 1 | Motion wake. Confirm the chosen module's VCC and output with its datasheet **and a meter**. | **Yes** | HW-02 |
| 8 | **USB speaker / headphones** | 1 | Avoid public auto-play. Provide accessible audio controls. | **Yes** | ACCESS-01 |
| 9 | USB microphone | 1 | Optional push-to-talk. **Never** record continuously without the visitor knowing. | Optional | Privacy review |
| 10 | LED + **1 kΩ** resistor | 1 each | Status feedback. Never drive an LED from GPIO without a series resistor. | Optional | Visual |
| 11 | NFC reader + tagged cards | 1 + a few | Physical exhibit tokens. Start with a USB reader for simpler integration. | Optional | — |
| 12 | Ethernet, enclosure, cables, service switch | As needed | Separate display power if the display datasheet requires it. Route cables neatly. | **Yes** | Enclosure inspection |
| 13 | Level shifter (bidirectional or a simple divider) | 0–1 | Only if the measured PIR OUT is above 3.3 V | Conditional | HW-02 |
| 14 | Multimeter (tool) | 1 | Needed to measure sensor output before connecting it | **Yes** (tool) | HW-02 record |

### 16.1 Power budget worksheet (fill in with measured values)

| Load | Datasheet (typ.) | Measured idle | Measured peak | Supplied from |
|---|---|---|---|---|
| Pi 5 + active cooler | `TBD` | `TBD` | `TBD` | 27 W USB-C |
| Touchscreen | `TBD (model-specific)` | `TBD` | `TBD` | **Own PSU** if the datasheet requires |
| USB speaker | `TBD` | `TBD` | `TBD` | Pi USB |
| USB mic (optional) | `TBD` | `TBD` | `TBD` | Pi USB |
| SSD (optional) | `TBD` | `TBD` | `TBD` | Pi USB 3 |
| PIR module | `TBD` | `TBD` | `TBD` | Pi 5 V or 3.3 V pin **per module** |
| **Total on Pi supply** | | | | Must stay within the PSU and Pi USB budget |

> Don't assume the Pi's USB ports can safely power the screen plus a mic and an SSD. Measure with a USB power meter and record the numbers in the handover bundle.

---

## 17. GPIO Connection Schedule

<div align="center">
<img src="diagrams/03_gpio_wiring.png" alt="GPIO wiring overview" width="900"/>
<br/>
<img src="diagrams/04_header_map.png" alt="Header map" width="860"/>
</div>

| Peripheral | Connection (BCM / physical) | Safety / software setting |
|---|---|---|
| **HOME button** | One leg → **BCM27, physical 13**; other leg → **GND, physical 14** | `Button(27, pull_up=True, bounce_time=0.15)`; software debounce |
| **PIR OUT** | **BCM17, physical 11** | Measure the output high first. **Never** drive Pi GPIO above 3.3 V. |
| **PIR GND** | **GND, physical 6** | Common ground with the Pi. Use only the module's required VCC, e.g. 5 V if specified. |
| **PIR VCC** | Power as specified by that module | Some PIR modules need 5 V VCC but give a 3.3 V OUT. Check the exact board pinout. |
| Optional LED | **BCM22, physical 15** → **1 kΩ** → LED → **GND, physical 20** | Observe polarity. Optional; not needed to prove the project. |
| Touchscreen video | Pi micro-HDMI → touchscreen HDMI | Match resolution and orientation. The display may have separate power. |
| Touchscreen input | Pi USB → screen's USB touch port | Verify the touchscreen presents as standard USB HID |
| Microphone / speaker | Pi USB or display-supported audio | Prefer a headset option. Test the actual device selection. |

### 17.1 Pin-numbering sanity check

The most common failure in student builds is **confusing BCM numbers with physical pin numbers**. Before power-on:

```text
BCM17 == physical 11   (PIR OUT)
BCM27 == physical 13   (HOME)
BCM22 == physical 15   (LED, optional)
GND   == physical 6, 14, 20 (and others)
```

Check with `pinout` (from GPIO Zero) on the Pi itself, and photograph the finished wiring for the handover record.

### 17.2 Bench verification procedure (HW-02)

1. With the Pi **powered off and disconnected**, power the PIR module alone from a bench supply at its specified VCC.
2. Wave a hand in front of it. Measure **OUT to GND** with a multimeter and record the high voltage.
3. If OUT is **≤ 3.3 V**, connect it to BCM17. If it is higher, add a level shifter or divider and measure again.
4. Account for PIR **warm-up after power-on**. Many modules need tens of seconds; see the module datasheet (`TBD`).
5. Connect to the Pi. Run `python3 -c "from gpiozero import MotionSensor; m=MotionSensor(17); m.wait_for_motion(); print('motion')"`.
6. Record in the test sheet: module part number, VCC, measured OUT high, date, tester.

---

## 18. Electrical and Physical Safety

> [!CAUTION]
> This is a **low-voltage DC** project. Build **no** AC or mains wiring. Buy certified, enclosed adaptors instead of constructing a supply.

| # | Checklist item | Why |
|---|---|---|
| S-1 | **Power OFF and disconnect** the Pi before wiring GPIO | Shorts during wiring damage the SoC |
| S-2 | Confirm **BCM vs physical header numbers** | Wrong numbering can damage components or make the demo fail |
| S-3 | Use continuity testing and a multimeter to confirm the **sensor pin order and high output voltage** before connecting to GPIO. If OUT exceeds 3.3 V, use a level shifter. | Pi 5 GPIO is 3.3 V logic and not 5 V tolerant |
| S-4 | Give the screen its **specified supply**. Don't assume the Pi's USB can power the screen plus mic and SSD. | Brown-outs cause SD corruption and random reboots |
| S-5 | Secure the touchscreen and Pi behind a **vented panel with cable strain relief**. Visitors must not reach pins or power connections. | Public exhibit safety and tamper resistance |
| S-6 | Account for **PIR warm-up** after boot. Don't wake repeatedly on every sensor trigger. Respect quiet mode and audio volume. | Avoids a wake loop and noise complaints |
| S-7 | Stand/table height and angle must allow **seated use**. Don't put every critical control high on a tall cabinet. | Accessibility ([§ 38](#38-accessibility)) |
| S-8 | Label the service switch and keep a **lockable** service panel | Operators can power-cycle safely |
| S-9 | Keep an **LED series resistor** on any LED | Protects GPIO from overcurrent |
| S-10 | **Ventilate** for continuous operation; validate with HW-04 | Throttling or shutdown ruins the demo |

---

## 19. Enclosure and Exhibition Ergonomics

These are design targets, not certified specifications.

| Topic | Guidance | Status |
|---|---|---|
| **Mounting height** | Put the touch area within comfortable reach for seated and standing visitors. Tilt the screen to reduce glare and suit seated sight lines. Validate with persona P4. | `TBD` from the venue test |
| **HOME button** | Large, high-contrast, tactile, reachable from a seated position. Label it with a text + icon "HOME". | 📐 |
| **PIR placement** | Aim at the approach zone, not a corridor with through-traffic. Avoid heat sources and direct sunlight. | `TBD` from the venue test |
| **Audio** | Headphone jack or hook at a reachable height. Speaker volume capped. Nothing plays until the visitor asks. | 📐 |
| **Ventilation** | Intake low, exhaust high. Keep the Pi's active cooler unobstructed. | Validate with HW-04 |
| **Cable management** | Strain relief on every cable; no dangling cables on the visitor side | 📐 |
| **Tamper resistance** | Service panel locked; no exposed USB ports on the visitor side; Chromium exit disabled | 📐 + [§ 40](#40-security-controls) |
| **Signage** | A small printed notice: "Answers are generated from archive sources and link to them. No personal data is stored." | 📐 |
| **Lighting** | Test real screen angles under venue lighting (ACCESS-01) | `TBD` |

---

## 20. Embedded Software Architecture

<div align="center">
<img src="diagrams/07_pi_processes.png" alt="Pi processes" width="900"/>
</div>

### 20.1 Processes on the Raspberry Pi

| # | Process | Implementation | Responsibilities | Status |
|---|---|---|---|---|
| 1 | **kiosk-agent** | Python + GPIO Zero (lgpio) under systemd | Reads GPIO. Monitors connectivity to `/v1/health`. Exposes a loopback-only event service. Refreshes approved offline bundles. Clears idle sessions. Reports device health **without collecting personally identifying visitor information.** | ✅ Bridge logic in [`kiosk-agent/pi_gpio_bridge.py`](kiosk-agent/pi_gpio_bridge.py); 📐 health and sync loop |
| 2 | **Local event service** | Python stdlib HTTP server on `127.0.0.1:8765` | `POST /device/event` from the bridge → Server-Sent Events on `GET /device/stream` to the UI. Allow-listed events only. | ✅ [`kiosk-agent/local_event_service.py`](kiosk-agent/local_event_service.py) |
| 3 | **Kiosk UI** | Static build (React + TS planned; the prototype is a single HTML file) | Touch navigation, document view, media controls, captions, source citations, screen-language choice, offline badges | 🧪 [`prototype/ambedkar_kiosk.html`](prototype/ambedkar_kiosk.html) |
| 4 | **Chromium kiosk** | `chromium-browser --kiosk` launched after graphical login | Points to the **locally served UI**, suppresses normal browser chrome, recovers after an accidental browser exit | 📐 [§ 54](#54-raspberry-pi-setup) |
| 5 | **Local content cache** | SQLite + assets | Only the currently approved public subset, with a signed/versioned manifest and expiry/revocation handling. SQLite FTS5 is enough for small offline keyword search. | ✅ Manifest rules in [`reference/heritage_core/manifest.py`](reference/heritage_core/manifest.py); 📐 SQLite schema below |

### 20.2 Boot order

<div align="center">
<img src="diagrams/06_boot_sequence.png" alt="Boot order" width="860"/>
</div>

```text
power → OS and network start → local agent / event service → UI asset server
      → Chromium full screen → PIR warm-up → ATTRACT screen
```

The system must stay **functional if the cloud is unavailable at boot** (NFR-08). Chromium loads `http://127.0.0.1:<ui-port>/`, never a cloud URL.

### 20.3 Session reset policy

<div align="center">
<img src="diagrams/38_session_reset.png" alt="Session reset" width="860"/>
</div>

After a configurable period of inactivity (prototype: **120 s**), the kiosk warns the visitor and offers to extend (prototype countdown: **20 s**). It then:

1. stops playback
2. clears the microphone buffer
3. clears the reading list and any QR hand-off
4. clears in-memory question state and the answer panel
5. clears browser navigation state, filters, the active story and the viewer state
6. returns to ATTRACT

The **physical HOME button runs the same reset** without destroying the local cache.

### 20.4 Offline cache schema (SQLite, 📐 specified)

```sql
-- /var/lib/heritage-kiosk/cache.db   (owner: kiosk user, mode 0600)
CREATE TABLE manifest_state (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  version INTEGER NOT NULL,
  issued_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  applied_at TEXT NOT NULL
);
CREATE TABLE cached_item (
  item_id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  rights_label TEXT NOT NULL,        -- attribution text shown in the viewer
  card_json TEXT NOT NULL,           -- display metadata (no private fields)
  manifest_version INTEGER NOT NULL
);
CREATE TABLE cached_asset (
  asset_id TEXT PRIMARY KEY,
  item_id TEXT NOT NULL REFERENCES cached_item(item_id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('access_image','access_pdf','caption','audio','video','thumb')),
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL
);
CREATE VIRTUAL TABLE cached_text USING fts5(
  passage_id UNINDEXED, item_id UNINDEXED, printed_page UNINDEXED, text,
  tokenize = 'unicode61 remove_diacritics 2'
);
```

Rules:

* The cache is rebuilt in a **temporary database file** and swapped in with an atomic rename, the same pattern as `manifest.apply_update`.
* Revoked items are deleted together with their assets and FTS rows **in the same transaction**.
* If `now > expires_at + grace`, the UI hides the cache entirely and shows "Offline exhibit unavailable — please ask staff" (fail closed).

---

## 21. Visitor State Machine

<div align="center">
<img src="diagrams/05_state_machine.png" alt="Visitor state machine" width="900"/>
</div>

The state machine is implemented in [`reference/heritage_core/kiosk_state.py`](reference/heritage_core/kiosk_state.py) and tested in [`reference/tests/test_kiosk_state.py`](reference/tests/test_kiosk_state.py).

| From | Event | Guard | To | Side effects |
|---|---|---|---|---|
| `BOOT` | `boot_done` | — | `ATTRACT` | Silent attract visual |
| `ATTRACT` | `visitor_approached` (PIR) | `uptime ≥ pir_warmup_s` **and** outside `pir_cooldown_s` | `ACTIVE` | Log `wake:pir`; **no loud playback** |
| `ATTRACT` | `touch` | — | `ACTIVE` | — |
| `ACTIVE` | `touch` / PIR | — | `ACTIVE` | Reset the idle timer (presence counts as activity) |
| `ACTIVE` | `tick` | `idle_for ≥ idle_s` | `IDLE_WARNING` | Show the countdown modal |
| `IDLE_WARNING` | `extend` | — | `ACTIVE` | Toast "session extended" |
| `IDLE_WARNING` | `tick` | `countdown ≤ 0` | `ATTRACT` via `RESETTING` | Full reset (reason `idle`) |
| any of `ATTRACT`, `ACTIVE`, `IDLE_WARNING` | `home_pressed` | — | `ATTRACT` via `RESETTING` | Full reset (reason `home`) |
| any | `net_down` / `net_up` | — | unchanged | `online` flag; assistant availability; manifest refresh on `net_up` |

### 21.1 Configurable parameters

| Parameter | Prototype / reference default | Env var (agent) | Notes |
|---|---|---|---|
| Idle timeout | 120 s | `KIOSK_IDLE_S` | Too short strands slow readers; too long leaks state to the next visitor |
| Countdown | 20 s | `KIOSK_COUNTDOWN_S` | Must be long enough to reach "extend" with assistive tech |
| PIR warm-up | 30 s (reference) | `KIOSK_PIR_WARMUP_S` | `TBD` from the module datasheet |
| PIR cooldown | 10 s (reference) | `KIOSK_PIR_COOLDOWN_S` | Stops a wake loop (HW-02 "wakes once, not in a loop") |
| HOME debounce | 0.15 s | — (code) | The design document's value. The prototype log says "debounced 50 ms"; see [§ 69](#69-discrepancies-between-source-documents). |

---

## 22. GPIO Bridge and Local Event Service

The browser **cannot read GPIO directly**. The event agent either pushes a WebSocket/SSE event to the local UI, or calls a **loopback-only** endpoint such as `http://127.0.0.1:8765/device/event`. The cloud should never receive raw motion data or button presses unless that is strictly necessary and reviewed.

### 22.1 Minimal GPIO pattern (from the design document)

```python
# On Pi OS: GPIO Zero with an lgpio-capable pin factory.
# notify_ui() is implemented by the local loopback service, not the cloud.
from gpiozero import Button, MotionSensor
from signal import pause

home = Button(27, pull_up=True, bounce_time=0.15)
pir = MotionSensor(17)
home.when_pressed = lambda: notify_ui("home_pressed")
pir.when_motion = lambda: notify_ui("visitor_approached")
pause()
```

### 22.2 The installable bridge (in this repository)

[`kiosk-agent/pi_gpio_bridge.py`](kiosk-agent/pi_gpio_bridge.py) adds:

| Feature | Detail |
|---|---|
| **Loopback enforcement** | `loopback_only()` rejects any URL whose host isn't a loopback IP or `localhost` (test `test_bridge_refuses_cloud_url`) |
| **PIR cooldown** | Repeated triggers inside `KIOSK_PIR_COOLDOWN_S` are suppressed (test `test_bridge_cooldown_and_failure_counting`) |
| **Fault tolerance** | Network errors are logged and counted, not raised, so the GPIO loop keeps running |
| **Testability** | The clock and sender are injectable; GPIO Zero is imported only in `main()` |
| **No secrets** | The bridge has no cloud credentials at all |

```python
class Bridge:
    def __init__(self, url, device_id="DEMO-KIOSK-01", cooldown_s=10.0, clock=time.monotonic, sender=None):
        self.url = loopback_only(url)          # raises for non-loopback hosts
        ...
    def on_motion(self) -> bool:
        now = self.clock()
        if self._last_motion is not None and now - self._last_motion < self.cooldown_s:
            return False                       # suppress wake loop
        self._last_motion = now
        return self.emit("visitor_approached")
    def on_home(self) -> bool:
        return self.emit("home_pressed")
```

### 22.3 Local event service

[`kiosk-agent/local_event_service.py`](kiosk-agent/local_event_service.py):

* binds `127.0.0.1` only, and additionally rejects POSTs whose client address isn't `127.0.0.1`
* accepts only `visitor_approached`, `home_pressed`, `net_down` and `net_up` (anything else returns 422)
* caps the body at 1 KiB (413)
* relays events to all subscribers of `GET /device/stream` as SSE
* logs nothing about visitors

UI subscription (kiosk UI side, 📐):

```ts
// src/device/useDeviceEvents.ts  (heritage-kiosk-ui)
export function subscribeDeviceEvents(onEvent: (e: {event: string}) => void) {
  const es = new EventSource("/device/stream");   // same-origin via the Pi's local asset server
  es.onmessage = (m) => onEvent(JSON.parse(m.data));
  es.onerror = () => { /* EventSource auto-reconnects; show nothing to the visitor */ };
  return () => es.close();
}
// usage
subscribeDeviceEvents(({event}) => {
  if (event === "visitor_approached") kiosk.wake();
  if (event === "home_pressed") kiosk.resetSession("home");
});
```

> [!TIP]
> **Hardening option:** replace the TCP loopback with a Unix domain socket owned by the kiosk user (mode 0660), with the UI asset server proxying `/device/stream`. That removes even local TCP exposure.

### 22.4 systemd unit

```ini
# /etc/systemd/system/heritage-gpio.service   (replace paths/user)
[Unit]
Description=Heritage archive kiosk GPIO agent
After=network.target heritage-events.service
Wants=heritage-events.service

[Service]
Type=simple
User=pi
Environment=KIOSK_EVENT_URL=http://127.0.0.1:8765/device/event
ExecStart=/home/pi/archive-env/bin/python /home/pi/archive/kiosk-agent/pi_gpio_bridge.py
Restart=always
RestartSec=3
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/heritage-events.service
[Unit]
Description=Heritage kiosk loopback event relay
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/home/pi/archive-env/bin/python /home/pi/archive/kiosk-agent/local_event_service.py
Restart=always
RestartSec=2
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

> Don't paste admin secrets into unit files. Don't run examples that connect to cloud services with an administrator password on the Pi.

---

## 23. Offline Behaviour Contract

<div align="center">
<img src="diagrams/08_offline_contract.png" alt="Offline contract" width="880"/>
</div>

| Feature | Cloud available | Cloud unavailable |
|---|---|---|
| Home and navigation | Current catalogue and approved tours | Cached cards + an obvious **"offline exhibit"** indicator |
| Document viewer | Access copy via API or signed URL | Cached public previews/text only; no unapproved masters |
| Search | Full hybrid search | Limited SQLite FTS5 on cached approved text |
| AI Q&A | Grounded server answer with citations | **Disabled.** Explain why and offer curated topics. |
| Video and audio | Stream the licensed web derivative | Locally cached clips only if rights permit |
| Admin publication | Available behind authenticated cloud admin | **Not available on the public Pi** |

> [!WARNING]
> **Cache revocation caveat.** An offline Pi can't receive an urgent withdrawal until it reconnects. Cache only **low-risk, clearly approved** items. Set a manifest expiry, and **fail closed** once it's past the approved grace period.

### 23.1 How the prototype shows it

<div align="center">
<img src="docs/screenshots/11_offline.png" alt="Offline banner" width="760"/>
</div>

When the device console simulates Wi-Fi loss, the prototype does the following:

1. Shows the **"Offline exhibit"** banner: *"Showing curator-approved cached items only. Live search and the research assistant are unavailable — the kiosk will not pretend otherwise."*
2. Switches the top-strip badge to **Offline**.
3. Disables Ask the Archive with an explanation.
4. Leaves the viewer if the open item isn't cached ("This item is not in the offline cache.").

---

## 24. Offline Manifest and Cache

<div align="center">
<img src="diagrams/35_manifest_lifecycle.png" alt="Manifest lifecycle" width="900"/>
</div>

The reference implementation lives in [`reference/heritage_core/manifest.py`](reference/heritage_core/manifest.py).

| Step | Function | Guarantees | Test |
|---|---|---|---|
| Build | `build(items, version, key, issued, ttl)` | Only items that pass `Action.OFFLINE_CACHE`; sorted; canonical JSON | `test_only_cacheable_items` |
| Sign | inside `build` | HMAC-SHA256 over the canonical body | `test_tamper_detected` |
| Verify | `verify(manifest, key, now, grace)` | Constant-time signature compare; expiry + grace → `ManifestError("... fail closed")` | `test_fail_closed_after_grace` |
| Apply | `apply_update(current, manifest, key, store)` | Rejects stale or rollback versions; writes temp → `fsync` → `os.replace`; returns revoked IDs | `test_update_is_atomic_and_revokes`, `test_rollback_rejected` |

### 24.1 Manifest format

```json
{
  "body": {
    "version": 42,
    "issued_at": "2026-09-26T00:00:00+00:00",
    "expires_at": "2026-10-03T00:00:00+00:00",
    "items": [
      {"item_id": "CR-001", "kind": "constitutional", "title": "Constituent Assembly Debates — 26 November 1949"},
      {"item_id": "WS-001", "kind": "writing", "title": "Annihilation of Caste"}
    ]
  },
  "sig": "hex-hmac-sha256-over-canonical-body"
}
```

A production manifest also lists **assets** (`asset_id`, `role`, `sha256`, `bytes`, a signed download URL valid for minutes). The agent downloads assets to a staging directory, verifies each checksum, and only then swaps the database.

### 24.2 Key handling

| Environment | Signing key location | Pi holds |
|---|---|---|
| Reference tests | Literal test bytes (`b"test-only-key-not-a-secret"`) | — |
| Prototype demo | Cloud secret store (`MANIFEST_SIGNING_KEY`) | The same HMAC key, readable only by the kiosk user (0600). **Acceptable for the class demo only.** |
| Pilot / production (⏳) | Ed25519 private key in a KMS/HSM | **Public** verification key only (ADR-13) |

### 24.3 Sync loop in the kiosk agent

```python
def sync_once(state, http, key, store, now):
    if not http.healthy():                          # GET /v1/health with a short timeout
        return state, "offline"
    m = http.get_json("/v1/offline-manifest")       # device credential in the Authorization header
    try:
        new_state, revoked = manifest.apply_update(state, m, key, store, now=now)
    except manifest.ManifestError as e:
        log.warning("manifest rejected: %s", e)     # keep the current cache (if still in date)
        return state, "rejected"
    purge_assets(revoked)                           # same transaction as the DB swap
    fetch_and_verify_assets(new_state)              # sha256 per asset
    return new_state, "updated"
```

Run it every `KIOSK_SYNC_INTERVAL_S` (default `CONFIGURABLE`, e.g. 900 s) and immediately on `net_up`.

---
