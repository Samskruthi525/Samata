#!/usr/bin/env python3
"""
Generate every diagram and chart used in README.md.

    python scripts/generate_diagrams.py            # writes PNGs into diagrams/

matplotlib + numpy only (no Graphviz, no web services) so CI can rebuild the
documentation reproducibly. Three kinds of figure are produced and each is
stamped accordingly:

* DESIGN          - architecture / flow diagrams (proposals, not measurements)
* DEMO CORPUS     - computed from data/demo_corpus.json (the 14-item sample
                    embedded in the HTML prototype). Not a representative archive.
* TARGET / ASSUMPTION - planning values from the design document. Not results.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))
from heritage_core import corpus as corpus_mod, sizing  # noqa: E402
from heritage_core.rights import permission_matrix, Action  # noqa: E402
from heritage_core.retrieval import HybridIndex, tokens  # noqa: E402
from heritage_core.metrics import cer, wer, hit_at_k, reciprocal_rank  # noqa: E402

OUT = ROOT / "diagrams"
OUT.mkdir(exist_ok=True)
DATA = corpus_mod.load()
RAW = json.loads((ROOT / "data" / "demo_corpus.json").read_text(encoding="utf-8"))

# ----------------------------------------------------------------- palette (from the kiosk CSS)
C = {
    "blue": "#12275A", "blue2": "#1E3A7A", "chakra": "#1F4FB8", "tint": "#E8EDF8",
    "ivory": "#FBF7EE", "ivory2": "#F3EDDF", "ink": "#1A1A24", "ink2": "#4B4D5C", "mute": "#7A7C8A",
    "saffron": "#F0862B", "saffron_d": "#C8651A", "saffron_t": "#FDEBD9",
    "green": "#1E8A4C", "green_t": "#DDF2E5", "gold": "#C9A24A", "gold_t": "#F6ECCF",
    "rose": "#A93A4E", "rose_t": "#F7DEE3", "teal": "#137C7C", "teal_t": "#D8EFEF",
    "violet": "#5B3F9E", "violet_t": "#E7E0F5", "grey": "#D9DCE3",
}
KIND_COL = {"writing": C["saffron_d"], "constitutional": C["chakra"], "manuscript_photo": C["rose"],
            "media": C["violet"], "interpretive": C["green"]}
KIND_LBL = {"writing": "Writings & speeches", "constitutional": "Constitutional records",
            "manuscript_photo": "Manuscripts & photographs", "media": "Audio & video",
            "interpretive": "Interpretive material"}

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "font.family": "DejaVu Sans",
    "font.size": 10, "axes.edgecolor": "#444", "axes.titleweight": "bold", "axes.titlesize": 13,
    "savefig.dpi": 150, "savefig.bbox": "tight",
})

STAMPS = {
    "design": "DESIGN DIAGRAM - proposal, not a measurement",
    "demo": "DEMO CORPUS (14 sample items) - not a representative evaluation",
    "target": "TARGETS / ASSUMPTIONS - not experimental results",
}


def stamp(fig, kind="design"):
    col = {"design": "#555", "demo": "#b00020", "target": "#b00020"}[kind]
    fig.text(0.995, 0.004, STAMPS[kind], ha="right", va="bottom", fontsize=7.5, color=col,
             alpha=0.9, family="monospace")


def save(fig, name, kind="design"):
    stamp(fig, kind)
    fig.savefig(OUT / name)
    plt.close(fig)
    print(f"  wrote diagrams/{name}")


def canvas(w=14, h=8, title=None, xlim=(0, 100), ylim=(0, 60)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=15, color=C["blue"], pad=12, loc="left")
    return fig, ax


def box(ax, x, y, w, h, text, fc=None, ec=None, fs=9.5, color=None, bold=False, r=0.8, lw=1.4, ha="center", z=2):
    fc = fc or C["ivory"]
    ec = ec or C["blue"]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))
    tx = x + w / 2 if ha == "center" else x + 1
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs, color=color or C["ink"],
            fontweight="bold" if bold else "normal", zorder=z + 1, wrap=True, linespacing=1.25)


def arrow(ax, p1, p2, text=None, color=None, ls="-", fs=8, rad=0.0, lw=1.5, tpos=0.5, toff=(0, 0.9)):
    color = color or C["ink2"]
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=13, color=color, lw=lw,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=1))
    if text:
        mx = p1[0] + (p2[0] - p1[0]) * tpos + toff[0]
        my = p1[1] + (p2[1] - p1[1]) * tpos + toff[1]
        ax.text(mx, my, text, ha="center", va="center", fontsize=fs, color=color,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9), zorder=4)


def zone(ax, x, y, w, h, label, fc, ec, fs=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=1.2",
                                fc=fc, ec=ec, lw=1.6, ls="--", zorder=0))
    ax.text(x + 1, y + h - 1.2, label, fontsize=fs, color=ec, fontweight="bold", va="top", zorder=1)


def chakra(ax, cx, cy, r, color, lw=1.5, spokes=24, alpha=1.0):
    ax.add_patch(Circle((cx, cy), r, fill=False, ec=color, lw=lw * 1.4, alpha=alpha))
    ax.add_patch(Circle((cx, cy), r * 0.14, fc=color, ec=color, alpha=alpha))
    for k in range(spokes):
        a = 2 * np.pi * k / spokes
        ax.plot([cx, cx + r * np.cos(a)], [cy, cy + r * np.sin(a)], color=color, lw=lw * 0.7, alpha=alpha)


# ======================================================================== figures
def fig_banner():
    fig, ax = plt.subplots(figsize=(14, 3.6))
    ax.set_xlim(0, 140); ax.set_ylim(0, 36); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 140, 36, fc=C["blue"], ec="none"))
    for i, col in enumerate([C["saffron"], "white", C["green"]]):
        ax.add_patch(Rectangle((i * 140 / 3, 34.6), 140 / 3, 1.4, fc=col, ec="none"))
    chakra(ax, 122, 16, 14, "white", lw=1.2, alpha=0.18)
    chakra(ax, 18, 17, 10.5, C["gold"], lw=1.4, alpha=0.95)
    ax.text(34, 24.5, "Dr. B. R. Ambedkar", color="white", fontsize=28, fontweight="bold", family="DejaVu Serif")
    ax.text(34, 15.5, "Digital Heritage Archive", color=C["gold"], fontsize=24, family="DejaVu Serif")
    ax.text(34, 8.2, "Raspberry Pi 5 visitor kiosk  +  source-grounded cloud archive", color="white", fontsize=12.5)
    ax.text(34, 3.4, "EVIDENCE-LED  ·  RIGHTS-GATED  ·  OFFLINE-HONEST  ·  ACCESSIBLE  ·  ACADEMIC PROTOTYPE",
            color="#C9D3EA", fontsize=9.5, family="monospace")
    fig.savefig(OUT / "00_banner.png", dpi=150, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print("  wrote diagrams/00_banner.png")


def fig_system_context():
    fig, ax = canvas(15, 8.6, "Figure 1 - System context: who touches the archive, and through what")
    box(ax, 38, 24, 26, 14, "Dr. B. R. Ambedkar\nDigital Heritage Archive\n\nRaspberry Pi kiosk\n+ cloud archive & AI", fc=C["blue"],
        ec=C["blue"], color="white", fs=11, bold=True)
    actors = [
        (2, 46, "Walk-in visitor\n(no account)", "Touch · PIR wake · HOME button\nshort stories, auto reset"),
        (2, 26, "Student", "Topic browse · summaries\nlabelled as summaries"),
        (2, 6, "Researcher", "Edition · printed page ·\ntranscript confidence"),
        (76, 46, "Curator / historian", "Review queue · rights gate ·\nversions · withdrawal"),
        (76, 26, "IT / exhibition operator", "Kiosk mode · watchdog ·\nhealth · offline bundle"),
        (76, 6, "Accessibility user", "Keyboard · captions ·\ncontrast · reachable mount"),
    ]
    for x, y, a, n in actors:
        box(ax, x, y, 22, 9, f"{a}\n", fc=C["ivory"], fs=9.8, bold=True)
        ax.text(x + 11, y + 2.4, n, ha="center", va="center", fontsize=7.6, color=C["ink2"])
        c = (x + 22, y + 4.5) if x < 50 else (x, y + 4.5)
        t = (38, 31) if x < 50 else (64, 31)
        arrow(ax, c, t, color=C["chakra"] if x < 50 else C["saffron_d"])
    ext = [(26, 52.5, "Holding institutions\n(Foundation catalogue,\nParliament Digital Library)"),
           (54, 52.5, "Rights holders /\npermission records")]
    for x, y, t in ext:
        box(ax, x, y, 21, 7, t, fc=C["gold_t"], ec=C["gold"], fs=8)
        arrow(ax, (x + 10.5, y), (51, 38), color=C["gold"], ls="--")
    box(ax, 40, 3, 22, 7, "Model / OCR / ASR providers\n(server-side only, eligible\npassages only)", fc=C["violet_t"], ec=C["violet"], fs=8)
    arrow(ax, (51, 24), (51, 10), "AI_CONTEXT-eligible\nevidence only", color=C["violet"], fs=7.5)
    save(fig, "01_system_context.png")


def fig_split_architecture():
    fig, ax = canvas(15, 9.2, "Figure 2 - Split architecture: the Pi is the embedded visitor device; the cloud holds the archive", ylim=(0, 64))
    zone(ax, 1, 2, 38, 58, "EDGE - Raspberry Pi 5 kiosk (untrusted public device)", C["tint"], C["chakra"])
    zone(ax, 46, 2, 53, 58, "CLOUD - archive, retrieval and AI (trusted boundary)", C["saffron_t"], C["saffron_d"])
    box(ax, 4, 47, 15, 7, "PIR sensor\nBCM17 · pin 11", fc="white", fs=8.5)
    box(ax, 21, 47, 15, 7, "HOME button\nBCM27 · pin 13", fc="white", fs=8.5)
    box(ax, 4, 36, 32, 7, "kiosk-agent (Python, GPIO Zero + lgpio)\nhealth probe · manifest sync · idle reset", fs=8.5)
    box(ax, 4, 25, 32, 7, "loopback event service 127.0.0.1:8765\nPOST /device/event  →  SSE /device/stream", fs=8.5)
    box(ax, 4, 14, 32, 7, "Kiosk UI (static React build)\nin Chromium --kiosk", fs=8.5, fc=C["ivory"])
    box(ax, 4, 4, 15, 7, "Offline cache\nSQLite FTS5 + assets", fc=C["green_t"], ec=C["green"], fs=8)
    box(ax, 21, 4, 15, 7, "HDMI touch · USB\naudio · status LED", fc="white", fs=8)
    for a, b in [((11.5, 47), (11.5, 43)), ((28.5, 47), (28.5, 43)), ((20, 36), (20, 32)), ((20, 25), (20, 21))]:
        arrow(ax, a, b)
    arrow(ax, (11.5, 14), (11.5, 11), color=C["green"])
    arrow(ax, (28.5, 14), (28.5, 11))
    box(ax, 49, 47, 22, 7, "API gateway\nHTTPS reverse proxy", fs=9)
    box(ax, 74, 47, 22, 7, "FastAPI services\npublic · device · admin routes", fs=9)
    box(ax, 49, 36, 22, 7, "PostgreSQL\ncatalogue · rights · audit", fs=9)
    box(ax, 74, 36, 22, 7, "Search\nPostgreSQL FTS + pgvector", fs=9)
    box(ax, 49, 25, 22, 7, "Private object storage\nmasters · derivatives", fs=9)
    box(ax, 74, 25, 22, 7, "Worker jobs\nOCR · ASR · embeddings", fs=9)
    box(ax, 49, 14, 22, 7, "RAG answer service\ncitation verifier", fs=9, fc=C["violet_t"], ec=C["violet"])
    box(ax, 74, 14, 22, 7, "Admin / curator UI\nseparate identity + MFA", fs=9, fc=C["rose_t"], ec=C["rose"])
    box(ax, 49, 4, 47, 6, "Observability: /v1/health · structured logs · uptime alert · daily AI-call caps", fs=8.5, fc="white")
    arrow(ax, (36, 17.5), (49, 50.5), "HTTPS · scoped device credential", color=C["chakra"], fs=8, rad=-0.15, tpos=0.45)
    arrow(ax, (49, 48.5), (36, 38), "signed offline manifest", color=C["green"], fs=8, rad=-0.15, tpos=0.55, toff=(0, -1.5))
    arrow(ax, (71, 50.5), (74, 50.5))
    for a, b in [((85, 47), (85, 43)), ((60, 47), (60, 43)), ((85, 36), (85, 32)), ((60, 36), (60, 32)), ((71, 17.5), (74, 17.5))]:
        arrow(ax, a, b, color=C["ink2"])
    arrow(ax, (85, 36), (60, 21), color=C["violet"], rad=0.1)
    save(fig, "02_split_architecture.png")


def fig_gpio_wiring():
    fig, ax = canvas(15, 8.4, "Figure 3 - Connection overview (design reference, NOT a PCB schematic)", ylim=(0, 60))
    ax.add_patch(FancyBboxPatch((36, 12), 28, 38, boxstyle="round,pad=0.02,rounding_size=1.5", fc="#2E7D4F", ec="#184D30", lw=2))
    ax.text(50, 47, "Raspberry Pi 5", color="white", ha="center", fontsize=13, fontweight="bold")
    ax.text(50, 44, "3.3 V GPIO - NOT 5 V tolerant", color="#FFE8A0", ha="center", fontsize=8.5)
    pins = [(11, "BCM17", "PIR OUT", 40), (6, "GND", "PIR GND", 36), (13, "BCM27", "HOME", 32),
            (14, "GND", "HOME GND", 28), (15, "BCM22", "LED (opt.)", 24), (20, "GND", "LED GND", 20)]
    for phys, bcm, use, y in pins:
        ax.add_patch(Rectangle((36.5, y - 1), 11, 2.2, fc="#FFD54A" if "BCM" in bcm else "#333", ec="black", lw=0.6))
        ax.text(42, y + 0.1, f"pin {phys} · {bcm}", ha="center", va="center", fontsize=7.3,
                color="black" if "BCM" in bcm else "white")
    box(ax, 2, 36, 22, 8, "PIR module\nVCC per datasheet (often 5 V)\nOUT must be ≤ 3.3 V", fc=C["saffron_t"], ec=C["saffron_d"], fs=8.3)
    box(ax, 2, 25, 22, 8, "Momentary large HOME button\npull_up=True · bounce 0.15 s", fc=C["tint"], fs=8.3)
    box(ax, 2, 15, 22, 7, "Status LED + 1 kΩ series\n(optional; observe polarity)", fc=C["green_t"], ec=C["green"], fs=8.3)
    box(ax, 12, 47, 14, 6, "Level shifter\nif OUT > 3.3 V", fc=C["rose_t"], ec=C["rose"], fs=8)
    arrow(ax, (24, 42), (36.5, 40), "OUT", color=C["saffron_d"])
    arrow(ax, (24, 38), (36.5, 36), "GND", color="#333")
    arrow(ax, (24, 30.5), (36.5, 32), "leg A", color=C["chakra"])
    arrow(ax, (24, 27), (36.5, 28), "leg B", color="#333")
    arrow(ax, (24, 19), (36.5, 24), "anode via 1 kΩ", color=C["green"], fs=7)
    arrow(ax, (24, 16.5), (36.5, 20), "cathode", color="#333", fs=7)
    arrow(ax, (19, 47), (19, 44), color=C["rose"], ls="--")
    box(ax, 72, 40, 25, 8, "HDMI capacitive touchscreen\n10-15 in · own PSU if datasheet says", fc="white", fs=8.3)
    box(ax, 72, 29, 25, 7, "USB speaker / headphones\n(no public auto-play)", fc="white", fs=8.3)
    box(ax, 72, 19, 25, 7, "USB microphone (optional)\npush-to-talk only", fc="white", fs=8.3)
    box(ax, 72, 9, 25, 7, "27 W USB-C PSU (official or\nverified equivalent)", fc=C["gold_t"], ec=C["gold"], fs=8.3)
    arrow(ax, (64, 45), (72, 45), "micro-HDMI", fs=7.5)
    arrow(ax, (72, 42), (64, 40), "USB HID touch", fs=7.5)
    arrow(ax, (64, 32), (72, 32.5), "USB", fs=7.5)
    arrow(ax, (64, 24), (72, 22.5), "USB", fs=7.5)
    arrow(ax, (72, 12.5), (64, 15), "USB-C power", fs=7.5, color=C["gold"])
    ax.text(50, 4.5, "Power OFF before wiring · measure PIR OUT with a meter first · confirm BCM vs physical numbering · no exposed mains",
            ha="center", fontsize=9, color=C["rose"], fontweight="bold")
    save(fig, "03_gpio_wiring.png")


def fig_header_map():
    fig, ax = plt.subplots(figsize=(13, 4.2))
    ax.set_xlim(-1, 21); ax.set_ylim(-1.8, 3.2); ax.axis("off")
    ax.set_title("Figure 4 - 40-pin header: pins used by the kiosk (physical numbering; BCM in labels)", loc="left", color=C["blue"])
    names = {1: "3V3", 2: "5V", 4: "5V", 6: "GND", 9: "GND", 14: "GND", 17: "3V3", 20: "GND", 25: "GND",
             30: "GND", 34: "GND", 39: "GND", 11: "BCM17", 13: "BCM27", 15: "BCM22"}
    used = {11: ("PIR OUT", C["saffron"]), 6: ("PIR GND", "#333"), 13: ("HOME", C["chakra"]),
            14: ("HOME GND", "#333"), 15: ("LED", C["green"]), 20: ("LED GND", "#333")}
    for p in range(1, 41):
        col = (p - 1) // 2
        row = 1 if p % 2 == 1 else 2
        fc = used[p][1] if p in used else ("#E57373" if names.get(p, "").startswith("5V") else
                                           "#FFB74D" if names.get(p) == "3V3" else "#9E9E9E" if names.get(p) == "GND" else "#ECEFF1")
        ax.add_patch(Circle((col, row), 0.36, fc=fc, ec="black", lw=0.8))
        ax.text(col, row, str(p), ha="center", va="center", fontsize=6.8, color="white" if p in used else "black")
        if p in used:
            ax.text(col, row + (0.75 if row == 2 else -0.8), f"{used[p][0]}\n{names.get(p, '')}", ha="center",
                    va="center", fontsize=7, color=used[p][1] if used[p][1] != "#333" else "#333", fontweight="bold")
    ax.text(0, -1.5, "Red = 5 V rail (never to GPIO) · Orange = 3.3 V · Grey = GND · Coloured = used by kiosk. "
            "Some PIR boards need 5 V VCC while providing 3.3 V OUT - check the exact board.", fontsize=8.5, color=C["ink2"])
    save(fig, "04_header_map.png")


def fig_state_machine():
    fig, ax = canvas(15, 8.4, "Figure 5 - Visitor state machine on the Pi (mirrors reference/heritage_core/kiosk_state.py)")
    S = {"BOOT": (4, 26), "ATTRACT": (26, 26), "ACTIVE": (52, 26), "IDLE_WARNING": (78, 40), "RESETTING": (78, 10)}
    col = {"BOOT": C["grey"], "ATTRACT": C["tint"], "ACTIVE": C["green_t"], "IDLE_WARNING": C["saffron_t"], "RESETTING": C["rose_t"]}
    for k, (x, y) in S.items():
        box(ax, x, y, 17, 8, k, fc=col[k], fs=10.5, bold=True)
    arrow(ax, (21, 30), (26, 30), "boot_done", fs=7.5)
    arrow(ax, (43, 32), (52, 32), "PIR (after warm-up,\noutside cooldown)\nor TOUCH", fs=7.5, toff=(0, 3))
    arrow(ax, (69, 33), (78, 42), f"idle ≥ {120} s", fs=7.5, toff=(-2, 1))
    arrow(ax, (78, 40), (69, 31), "EXTEND /\ntouch", fs=7.5, rad=0.25, toff=(3, -1))
    arrow(ax, (86.5, 40), (86.5, 18), "countdown 20 s\nexpires", fs=7.5, toff=(6, 0))
    arrow(ax, (69, 27), (78, 16), "HOME\n(BCM27)", fs=7.5, color=C["rose"], toff=(-2, -1))
    arrow(ax, (78, 12), (34.5, 26), "clear session: stop media, reading list,\nquestion buffer, navigation - KEEP cache", fs=7.5,
          color=C["rose"], rad=-0.25, tpos=0.5, toff=(0, -6))
    ax.text(52, 52, "Orthogonal flag: online / offline", fontsize=10, color=C["chakra"], fontweight="bold", ha="center")
    ax.text(52, 48.5, "NET_DOWN  →  assistant disabled with explanation, offline badge shown, browsing continues from cache\n"
            "NET_UP    →  manifest refresh (atomic), revoked items removed", fontsize=8.5, ha="center", color=C["ink2"], family="monospace")
    ax.text(3, 5, "Defaults from the HTML prototype: IDLE_MS = 120 000, COUNT_S = 20.\nPIR warm-up and cooldown are TBD per module (reference uses 30 s / 10 s).",
            fontsize=8.5, color=C["ink2"])
    save(fig, "05_state_machine.png")


def fig_boot_sequence():
    fig, ax = plt.subplots(figsize=(14, 4.6))
    steps = ["Power", "Raspberry Pi OS + network", "kiosk-agent (systemd)", "local event service", "UI asset server",
             "Chromium --kiosk", "PIR warm-up", "ATTRACT screen"]
    for i, s in enumerate(steps):
        ax.barh(len(steps) - 1 - i, 1, left=i, color=[C["grey"], C["tint"], C["chakra"], C["chakra"], C["teal"],
                                                     C["saffron"], C["gold"], C["green"]][i], edgecolor="white")
        ax.text(i + 0.5, len(steps) - 1 - i, s, ha="center", va="center", fontsize=8.5,
                color="white" if i in (2, 3, 4, 5, 7) else "black")
    ax.set_yticks([]); ax.set_xticks(range(len(steps) + 1)); ax.set_xticklabels(["t0"] + ["?"] * len(steps))
    ax.set_xlabel("Order only - durations are TBD and must be measured on the assembled kiosk (test HW-01, cold-boot time)")
    ax.set_title("Figure 6 - Boot order: the kiosk must reach ATTRACT even if the cloud is unreachable", loc="left", color=C["blue"])
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, "06_boot_sequence.png")


def fig_pi_processes():
    fig, ax = canvas(15, 7.6, "Figure 7 - Processes on the Raspberry Pi and what each may touch", ylim=(0, 54))
    procs = [
        (2, 30, "kiosk-agent (Python)", "GPIO read (PIR/HOME)\n/health probe · manifest sync\nidle policy · device health\nNO visitor PII", C["tint"]),
        (27, 30, "local event service", "127.0.0.1 only\nPOST /device/event\nSSE /device/stream\nallow-listed events", C["tint"]),
        (52, 30, "Kiosk UI (React static)", "touch navigation · viewer\ncaptions · citations\nlanguage · offline badges", C["ivory"]),
        (77, 30, "Chromium kiosk", "full screen · no chrome\nrestart on exit\nloads LOCAL UI (not cloud)", C["saffron_t"]),
    ]
    for x, y, t, d, fc in procs:
        box(ax, x, y, 21, 16, "", fc=fc)
        ax.text(x + 10.5, y + 13, t, ha="center", fontsize=10, fontweight="bold", color=C["blue"])
        ax.text(x + 10.5, y + 6.3, d, ha="center", va="center", fontsize=8.2, color=C["ink2"])
    arrow(ax, (23, 38), (27, 38), "events")
    arrow(ax, (48, 38), (52, 38), "SSE")
    arrow(ax, (77, 38), (73, 38), "renders")
    box(ax, 27, 8, 46, 12, "Local content cache\nSQLite (FTS5) + approved public assets\nsigned, versioned manifest · expiry · revocation on reconnect", fc=C["green_t"], ec=C["green"], fs=9)
    arrow(ax, (12, 30), (30, 20), "writes (atomic)", color=C["green"])
    arrow(ax, (62, 30), (62, 20), "reads", color=C["green"])
    box(ax, 2, 8, 21, 12, "systemd\nRestart=always\nNoNewPrivileges=true", fc="white", fs=9)
    box(ax, 77, 8, 21, 12, "Cloud API (HTTPS)\nscoped, revocable\ndevice credential", fc=C["saffron_t"], ec=C["saffron_d"], fs=9)
    arrow(ax, (77, 14), (73, 14), color=C["saffron_d"], ls="--")
    save(fig, "07_pi_processes.png")


def fig_offline_contract():
    rows = ["Home & navigation", "Document viewer", "Search", "AI Q&A", "Video & audio", "Admin publication"]
    online = ["Current catalogue + approved tours", "Access copy via API / signed URL", "Full hybrid search",
              "Grounded answer with citations", "Stream licensed web derivative", "Behind authenticated cloud admin"]
    offline = ["Cached cards + 'offline exhibit' badge", "Cached public previews/text only", "SQLite FTS5 on cached text",
               "DISABLED - explain why, offer topics", "Cached clips only if rights permit", "Not available on public Pi"]
    lvl = [2, 1, 1, 0, 1, 0]
    fig, ax = plt.subplots(figsize=(14, 5.2))
    ax.axis("off")
    ax.set_title("Figure 8 - Offline behaviour contract (design doc §5.3)", loc="left", color=C["blue"])
    colours = {2: C["green_t"], 1: C["gold_t"], 0: C["rose_t"]}
    for i, r in enumerate(rows):
        y = len(rows) - i
        ax.add_patch(Rectangle((0, y), 3, 0.9, fc=C["tint"], ec="white"))
        ax.text(0.1, y + 0.45, r, va="center", fontsize=9.5, fontweight="bold", color=C["blue"])
        ax.add_patch(Rectangle((3, y), 4.5, 0.9, fc=C["green_t"], ec="white"))
        ax.text(3.1, y + 0.45, online[i], va="center", fontsize=9)
        ax.add_patch(Rectangle((7.5, y), 4.5, 0.9, fc=colours[lvl[i]], ec="white"))
        ax.text(7.6, y + 0.45, offline[i], va="center", fontsize=9)
    ax.text(3.1, len(rows) + 1.2, "CLOUD AVAILABLE", fontweight="bold", color=C["green"])
    ax.text(7.6, len(rows) + 1.2, "CLOUD UNAVAILABLE", fontweight="bold", color=C["rose"])
    ax.set_xlim(0, 12); ax.set_ylim(0.6, len(rows) + 1.8)
    ax.text(0, 0.7, "Caveat: an offline Pi cannot receive an urgent withdrawal until it reconnects -> cache only low-risk approved items; fail closed after expiry + grace.",
            fontsize=8.5, color=C["rose"])
    save(fig, "08_offline_contract.png")


def fig_cloud_services():
    fig, ax = canvas(15, 8, "Figure 9 - Cloud service boundaries (prototype implementation → production consideration)", ylim=(0, 58))
    rows = [("API gateway", "HTTPS reverse proxy → FastAPI", "rate limits · device identity · WAF as required"),
            ("Catalogue & permissions", "PostgreSQL", "institutional identity · audit trail"),
            ("Search", "PostgreSQL FTS + pgvector", "dedicated engine only if benchmarks warrant"),
            ("Files", "private object storage · short-lived links", "preservation store · backup · fixity"),
            ("OCR / transcription jobs", "Python worker + job table", "queue retries · reviewer assignment · versioned models"),
            ("AI Q&A", "server-only retrieval + model call", "curator benchmark · red-team · cost controls"),
            ("Admin UI", "same backend · separate auth routes", "two-person review for sensitive publication"),
            ("Observability", "health · structured logs · uptime alert", "security monitoring · retention · change mgmt")]
    for i, (a, b, c) in enumerate(rows):
        y = 50 - i * 6.2
        box(ax, 1, y, 22, 5, a, fc=C["blue"], color="white", bold=True, fs=9)
        box(ax, 25, y, 34, 5, b, fc=C["ivory"], fs=9)
        box(ax, 63, y, 36, 5, c, fc=C["saffron_t"], ec=C["saffron_d"], fs=9)
        arrow(ax, (59, y + 2.5), (63, y + 2.5), color=C["saffron_d"])
    ax.text(25, 56.3, "PROTOTYPE", fontweight="bold", color=C["blue"])
    ax.text(63, 56.3, "PRODUCTION CONSIDERATION (future, not built)", fontweight="bold", color=C["saffron_d"])
    save(fig, "09_cloud_services.png")


def fig_trust_boundaries():
    fig, ax = canvas(15, 8, "Figure 10 - Trust boundaries: the kiosk is a public device, not a trusted administrator", ylim=(0, 58))
    zone(ax, 1, 4, 26, 50, "PUBLIC / PHYSICAL", C["rose_t"], C["rose"])
    zone(ax, 31, 4, 36, 50, "CLOUD PUBLIC & DEVICE ROUTES", C["tint"], C["chakra"])
    zone(ax, 71, 4, 28, 50, "PRIVILEGED", C["gold_t"], C["gold"])
    box(ax, 4, 38, 20, 8, "Visitor at kiosk\n(touch, cables, Chromium)", fs=8.5, fc="white")
    box(ax, 4, 24, 20, 8, "Pi: device token\n(scoped, revocable)", fs=8.5, fc="white")
    box(ax, 4, 10, 20, 8, "Offline cache\n(public subset only)", fs=8.5, fc="white")
    box(ax, 34, 38, 30, 8, "Gateway: TLS · rate limit ·\ndevice identity check", fs=8.5, fc="white")
    box(ax, 34, 24, 30, 8, "Rights filter on EVERY request\n(list · search · AI · download · cache)", fs=8.5, fc="white")
    box(ax, 34, 10, 30, 8, "RAG service: eligible passages only;\ndocument text = evidence, never instructions", fs=8.5, fc="white")
    box(ax, 74, 38, 22, 8, "Curator / approver\nseparate identity + MFA", fs=8.5, fc="white")
    box(ax, 74, 24, 22, 8, "Preservation masters\n(never served to kiosk)", fs=8.5, fc="white")
    box(ax, 74, 10, 22, 8, "Secrets: model keys,\nDB creds (backend only)", fs=8.5, fc="white")
    arrow(ax, (24, 28), (34, 42), "HTTPS", color=C["chakra"])
    arrow(ax, (49, 38), (49, 32))
    arrow(ax, (49, 24), (49, 18))
    arrow(ax, (24, 28), (74, 42), "admin call from device token → DENIED (SEC-01)", color=C["rose"], ls="--", tpos=0.62, toff=(0, 2.5), fs=8)
    save(fig, "10_trust_boundaries.png")


def fig_ingest_pipeline():
    fig, ax = canvas(16, 6.6, "Figure 11 - Intake, rights, preservation, extraction, review and publication are separate stages", ylim=(0, 44))
    st = [("1 Inventory &\ncondition", "ID · record type ·\ncustody · handling"),
          ("2 Rights gate", "scan · display ·\ndownload · AI - each\ndecided separately"),
          ("3 Capture /\nimport", "born-digital kept\nbyte-for-byte;\nFADGI as reference"),
          ("4 Fixity", "SHA-256 · capture\nsettings · independent\nbackup"),
          ("5 Extract", "embedded text / OCR /\nhuman for handwriting;\nengine + confidence"),
          ("6 Align", "paragraph → page\nimage; media text\n→ timestamps"),
          ("7 Review", "names · numbers ·\nquotes · citations;\nflag uncertainty"),
          ("8 Publish /\nindex", "only rights-approved\nreviewed subset →\nsearch · timeline · cache")]
    w = 11.3
    for i, (t, d) in enumerate(st):
        x = 1 + i * (w + 1.1)
        fc = C["rose_t"] if i == 1 else C["green_t"] if i == 7 else C["tint"]
        box(ax, x, 22, w, 11, t, fc=fc, fs=9, bold=True)
        ax.text(x + w / 2, 14.5, d, ha="center", va="center", fontsize=7.8, color=C["ink2"])
        if i:
            arrow(ax, (x - 1.1, 27.5), (x, 27.5))
    ax.text(1, 5, "Gate: status 'unknown' or 'permission_pending' STOPS at stage 2 - never enters public index, AI context or offline bundle (test DOC-02).",
            fontsize=9, color=C["rose"], fontweight="bold")
    save(fig, "11_ingest_pipeline.png")


def fig_rights_states():
    fig, ax = canvas(15, 7.6, "Figure 12 - Rights states (catalogue) and review status (publication) are separate axes", ylim=(0, 56))
    rs = {"unknown": (3, 40), "permission_pending": (3, 24), "public_display_approved": (36, 40),
          "link_only": (36, 24), "restricted_to_staff": (36, 8), "withdrawn": (69, 24)}
    fc = {"unknown": C["grey"], "permission_pending": C["gold_t"], "public_display_approved": C["green_t"],
          "link_only": C["tint"], "restricted_to_staff": C["violet_t"], "withdrawn": C["rose_t"]}
    for k, (x, y) in rs.items():
        box(ax, x, y, 26, 8, k, fc=fc[k], fs=9.5, bold=True)
    arrow(ax, (16, 40), (16, 32), "request permission", fs=7.5)
    arrow(ax, (29, 28), (36, 44), "written permission\nrecorded", fs=7.5)
    arrow(ax, (29, 28), (36, 28), "link rather\nthan mirror", fs=7.5)
    arrow(ax, (29, 26), (36, 12), "staff-only", fs=7.5)
    arrow(ax, (62, 44), (69, 30), "takedown", fs=7.5, color=C["rose"])
    arrow(ax, (62, 28), (69, 28), "", color=C["rose"])
    ax.text(69, 46, "Review status (per item):", fontsize=9.5, fontweight="bold", color=C["blue"])
    ax.text(69, 36, "draft → in_review → approved_1\n→ published (2nd reviewer)\n→ withdrawn", fontsize=9, family="monospace", color=C["ink2"])
    ax.text(3, 3, "Public = rights ∈ {public_display_approved} AND status = published. link_only: catalogue card + outbound reference only.",
            fontsize=8.8, color=C["ink2"])
    save(fig, "12_rights_states.png")


def fig_rights_matrix():
    m = permission_matrix()
    states = list(m)
    acts = [a.value for a in Action]
    grid = np.array([[1 if m[s][a] else 0 for a in acts] for s in states])
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.imshow(grid, cmap=matplotlib.colors.ListedColormap([C["rose_t"], C["green_t"]]), aspect="auto")
    ax.set_xticks(range(len(acts))); ax.set_xticklabels(["list", "view access\ncopy", "search\nindex", "AI\ncontext", "offline\ncache", "download"])
    ax.set_yticks(range(len(states))); ax.set_yticklabels(states)
    for i in range(len(states)):
        for j in range(len(acts)):
            ax.text(j, i, "ALLOW" if grid[i, j] else "deny", ha="center", va="center", fontsize=8.5,
                    color=C["green"] if grid[i, j] else C["rose"], fontweight="bold")
    ax.set_title("Figure 13 - Rights gate for a PUBLISHED item (computed by heritage_core.rights.permitted)\n"
                 "Assumes ai/offline flags granted, download not granted - each flag is a separate decision", loc="left",
                 color=C["blue"], fontsize=11)
    save(fig, "13_rights_matrix.png")


def fig_data_model():
    fig, ax = canvas(16, 9.4, "Figure 14 - Reduced logical data model (timeline events must cite evidence through a join)", ylim=(0, 66))
    ents = {
        "collection": (2, 50, ["id PK", "owner / custodian", "scope", "ingestion agreement"]),
        "rights_policy": (2, 26, ["id PK", "status", "public_display", "download_allowed", "ai_processing_allowed", "review_date"]),
        "archive_item": (30, 38, ["id PK", "collection_id FK", "rights_id FK", "kind", "title", "creator / speaker", "source_uri", "edition / volume", "status"]),
        "asset": (30, 6, ["id PK", "item_id FK", "role (master/access/processing)", "sha256", "media_type", "version"]),
        "page": (58, 44, ["id PK", "item_id FK", "pdf_page_index", "printed_page_label", "reviewed_text", "ocr_status"]),
        "passage": (84, 44, ["id PK", "page_id FK", "exact_text", "start/end offset", "reviewed", "embedding vector(N)"]),
        "transcript_segment": (58, 16, ["id PK", "item_id FK", "start_ms / end_ms", "words", "speaker (verified)", "reviewed"]),
        "timeline_event": (84, 6, ["id PK", "event_date_label", "label", "display_text", "status"]),
        "event_evidence": (84, 24, ["id PK (own ID)", "event_id FK", "item_id FK", "page_id / passage_id", "time_start_ms"]),
    }
    geo = {}
    for n, (x, y, f) in ents.items():
        h = 2.4 + 1.9 * len(f)
        ax.add_patch(Rectangle((x, y), 15 if n != "archive_item" else 17, h, fc="white", ec=C["blue"], lw=1.3))
        ax.add_patch(Rectangle((x, y + h - 2.4), 15 if n != "archive_item" else 17, 2.4, fc=C["blue"], ec=C["blue"]))
        ax.text(x + 0.5, y + h - 1.2, n, color="white", fontsize=8.8, fontweight="bold", va="center")
        for i, fld in enumerate(f):
            ax.text(x + 0.5, y + h - 3.4 - i * 1.9, fld, fontsize=7.4, va="center",
                    color=C["saffron_d"] if "PK" in fld else C["chakra"] if "FK" in fld else C["ink"])
        geo[n] = (x, y, 15 if n != "archive_item" else 17, h)

    def mid(n, side):
        x, y, w, h = geo[n]
        return {"l": (x, y + h / 2), "r": (x + w, y + h / 2), "t": (x + w / 2, y + h), "b": (x + w / 2, y)}[side]
    for a, sa, b, sb, lab in [("collection", "r", "archive_item", "l", "1:N"), ("rights_policy", "r", "archive_item", "l", "1:N"),
                              ("archive_item", "r", "page", "l", "1:N"), ("page", "r", "passage", "l", "1:N"),
                              ("archive_item", "b", "asset", "t", "1:N"), ("archive_item", "r", "transcript_segment", "l", "1:N"),
                              ("timeline_event", "t", "event_evidence", "b", "1:N (≥1 approved)"),
                              ("event_evidence", "l", "archive_item", "r", "N:1")]:
        arrow(ax, mid(a, sa), mid(b, sb), lab, fs=7, color=C["ink2"])
    save(fig, "14_data_model.png")


def fig_preservation():
    fig, ax = canvas(15, 6.4, "Figure 15 - Preservation master vs access vs processing derivatives", ylim=(0, 44))
    box(ax, 2, 14, 26, 22, "PRESERVATION MASTER\n\noriginal / archival scan\nSHA-256 at ingest + fixity checks\nnever overwritten\nnever served to kiosk",
        fc=C["gold_t"], ec=C["gold"], fs=9)
    box(ax, 38, 26, 26, 14, "ACCESS DERIVATIVE\nresized JPEG / PDF · MP4 H.264\nplayback audio · .vtt captions\nrights-approved only", fc=C["green_t"], ec=C["green"], fs=8.8)
    box(ax, 38, 6, 26, 14, "PROCESSING DERIVATIVE\nOCR/ASR candidate · layout\nembeddings · thumbnails\nversioned when cited", fc=C["tint"], fs=8.8)
    box(ax, 74, 26, 24, 14, "Kiosk / web viewer\n(signed short-lived URL)\nOffline bundle subset", fc="white", fs=8.8)
    box(ax, 74, 6, 24, 14, "Search index · RAG\n(passages with page/time\ncoordinates)", fc="white", fs=8.8)
    arrow(ax, (28, 28), (38, 33), "derive")
    arrow(ax, (28, 20), (38, 13), "derive")
    arrow(ax, (64, 33), (74, 33))
    arrow(ax, (64, 13), (74, 13))
    ax.text(2, 3, "Backups: at least one independent restoration path. A second disk in the same kiosk is NOT a backup. Evaluate with NDSA Levels.",
            fontsize=8.8, color=C["rose"])
    save(fig, "15_preservation_tiers.png")


def fig_hybrid_retrieval():
    fig, ax = canvas(16, 6.8, "Figure 16 - Hybrid retrieval: rights filter FIRST, then lexical + dense, fused and reranked", ylim=(0, 46))
    s = [("Query", "visitor text\n(+ language)"), ("Normalise", "NFKC · script ·\npunctuation"),
         ("Alias expand", "Babasaheb → Ambedkar\n(curated table)"), ("Rights filter", "eligible passages\nonly (SEARCH/AI)")]
    for i, (t, d) in enumerate(s):
        x = 1 + i * 13
        box(ax, x, 26, 11, 9, t, fc=C["rose_t"] if i == 3 else C["tint"], bold=True, fs=9)
        ax.text(x + 5.5, 21.5, d, ha="center", fontsize=7.6, color=C["ink2"], va="center")
        if i:
            arrow(ax, (x - 2, 30.5), (x, 30.5))
    box(ax, 56, 34, 16, 8, "Lexical (BM25 / FTS)\nexact titles, quotes,\ndates, article numbers", fs=8, fc=C["ivory"])
    box(ax, 56, 18, 16, 8, "Dense (pgvector)\nconcepts without\nexact vocabulary", fs=8, fc=C["ivory"])
    arrow(ax, (50, 30.5), (56, 38)); arrow(ax, (50, 30.5), (56, 22))
    box(ax, 76, 26, 10, 9, "RRF fusion\n+ reviewed\nboost", fs=8.5, bold=True, fc=C["gold_t"], ec=C["gold"])
    arrow(ax, (72, 38), (76, 32)); arrow(ax, (72, 22), (76, 29))
    box(ax, 89, 24, 10, 13, "Top-k with\n(item, page,\noffsets) or\n(item, ms)", fs=8.3, fc=C["green_t"], ec=C["green"])
    arrow(ax, (86, 30.5), (89, 30.5))
    ax.text(1, 8, "Acceptance (target): a curated-topic query returns a citable item in the top five on a fixed test set. Report P@5 / MRR and failures.\n"
            "Original-language text and labelled translations are indexed separately - AI output never silently replaces the original.",
            fontsize=8.8, color=C["ink2"])
    save(fig, "16_hybrid_retrieval.png")


def fig_rag_sequence():
    fig, ax = canvas(16, 9, "Figure 17 - Server-side source-grounded answer sequence (heritage_core.answer_contract)", ylim=(0, 64))
    lanes = ["Kiosk UI", "API /v1/ask", "Rights + retrieval", "Model (server-only)", "Citation verifier", "Catalogue"]
    xs = [8 + i * 17 for i in range(len(lanes))]
    for x, l in zip(xs, lanes):
        box(ax, x - 7, 56, 14, 5, l, fc=C["blue"], color="white", bold=True, fs=8.8)
        ax.plot([x, x], [4, 56], color=C["mute"], ls=":", lw=1)
    msgs = [(0, 1, "POST {query, language, device_id}"), (1, 2, "1 apply item/passage permissions + rate limit"),
            (2, 1, "2 evidence set: stable IDs + spans"), (1, 1, "3 drop unreviewed OCR from quoting"),
            (1, 3, "4 excerpts + guard instruction"), (3, 1, "answer + supporting passage IDs"),
            (1, 4, "5 every ID ∈ retrieved set? still visible?"), (4, 5, "6 fetch title/edition/page/time"),
            (5, 4, "metadata"), (4, 1, "7 ok  → cite  |  fail → abstain"), (1, 0, "answered | not_verified | unavailable")]
    y = 52
    for a, b, t in msgs:
        if a == b:
            ax.annotate("", xy=(xs[a] + 0.3, y - 2), xytext=(xs[a] + 0.3, y),
                        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=-1.2", color=C["saffron_d"]))
            ax.text(xs[a] + 3, y - 1, t, fontsize=7.6, color=C["saffron_d"], va="center")
        else:
            col = C["rose"] if "abstain" in t else C["chakra"]
            arrow(ax, (xs[a], y), (xs[b], y), color=col, lw=1.3)
            ax.text((xs[a] + xs[b]) / 2, y + 1, t, ha="center", fontsize=7.6, color=col,
                    bbox=dict(fc="white", ec="none", pad=0.5))
        y -= 4.3
    ax.text(1, 1, "8  UI labels AI SUMMARY / AI TRANSLATION and keeps the original scan or transcript one tap away. Citations come from the catalogue, never from model text.",
            fontsize=8.5, color=C["ink2"])
    save(fig, "17_rag_sequence.png")


def fig_knowledge_map():
    nodes = {n["id"]: n for n in RAW["km_nodes"]}
    fig, ax = plt.subplots(figsize=(14, 8.4))
    ax.set_xlim(40, 1160); ax.set_ylim(740, 150); ax.axis("off")
    ax.set_title("Figure 18 - Knowledge map from the reviewed relation table (12 nodes, 13 edges, exported from the prototype)",
                 loc="left", color=C["blue"])
    col = {"person": C["blue"], "work": C["saffron_d"], "debate": C["chakra"], "record": C["teal"],
           "manuscript": C["rose"], "media": C["violet"], "subject": C["green"]}
    for e in RAW["km_edges"]:
        a, b = nodes.get(e["from"]), nodes.get(e["to"])
        if not a or not b:
            continue
        ax.plot([a["x"], b["x"]], [a["y"], b["y"]], color=e.get("color", "#999"), lw=1.6, alpha=0.8, zorder=1)
        ax.text((a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2, e["rel"], fontsize=6.8, ha="center", va="center",
                color=e.get("color", "#555"), bbox=dict(fc="white", ec="none", pad=0.6), zorder=2)
    for n in nodes.values():
        r = n.get("r", 28) * 1.45
        ax.add_patch(Circle((n["x"], n["y"]), r, fc=col.get(n["type"], "#888"), ec="white", lw=2, zorder=3))
        ax.text(n["x"], n["y"], "\n".join(n["lines"]), ha="center", va="center", fontsize=5.9 if n["type"] != "person" else 8.5,
                color="white", fontweight="bold", zorder=4)
        if n.get("sub"):
            ax.text(n["x"], n["y"] + r + 12, n["sub"], ha="center", fontsize=6.8, color=C["ink2"], zorder=4)
    for i, (k, v) in enumerate(col.items()):
        ax.add_patch(Circle((70 + i * 150, 725), 9, fc=v)); ax.text(84 + i * 150, 725, k, va="center", fontsize=8)
    save(fig, "18_knowledge_map.png", "demo")


def fig_timeline():
    ev = RAW["events"]
    fig, ax = plt.subplots(figsize=(17, 6.2))
    eras = RAW["eras"]
    ecol = [C["tint"], C["saffron_t"], C["gold_t"], C["green_t"], C["violet_t"]]
    for i, e in enumerate(eras):
        ax.axvspan(e["from"], e["to"] + 1, color=ecol[i], alpha=0.8, zorder=0)
        ax.text((e["from"] + e["to"] + 1) / 2, 3.35, f'{e["from"]}-{e["to"]}', ha="center", fontsize=8.5, color=C["ink2"])
    ax.axhline(0, color=C["blue"], lw=2)
    for i, e in enumerate(ev):
        yr = e["year"] + (0.35 if e["id"].endswith("b") else 0)
        h = [1.1, 2.2, 1.65, 2.75][i % 4] * (1 if i % 2 == 0 else -1)
        c = KIND_COL.get(e["kind"], C["ink2"])
        ax.plot([yr, yr], [0, h], color=c, lw=1.2)
        ax.scatter([yr], [0], s=60, color=c, zorder=3, edgecolor="white")
        nev = len(e.get("evidence", []))
        ax.text(yr, h + (0.12 if h > 0 else -0.12), f'{e["date"]}\n{e["title"]}\n[{nev} evidence link{"s" if nev != 1 else ""}]',
                ha="center", va="bottom" if h > 0 else "top", fontsize=7, color=c)
    ax.set_ylim(-3.9, 3.7); ax.set_xlim(1888, 1960); ax.set_yticks([])
    ax.set_title("Figure 19 - The 14 curator-reviewed timeline cards in the prototype, each linked to at least one source item",
                 loc="left", color=C["blue"])
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    save(fig, "19_timeline_events.png", "demo")


def fig_corpus():
    items = RAW["items"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    kc = Counter(i["kind"] for i in items)
    ks = list(KIND_COL)[:4]
    axes[0].bar([KIND_LBL[k].replace(" & ", " &\n") for k in ks], [kc[k] for k in ks], color=[KIND_COL[k] for k in ks])
    axes[0].set_title("Items by collection category")
    axes[0].tick_params(axis="x", labelsize=7.5)
    axes[0].text(3, max(kc.values()) * 0.9, "5th category\n(interpretive) =\n14 timeline cards", fontsize=7.5, ha="center", color=C["green"])
    rc = Counter(i["rights"] for i in items)
    axes[1].barh(list(rc), list(rc.values()), color=[C["green"] if "approved" in k else C["gold"] if "link" in k else C["rose"] for k in rc])
    axes[1].set_title("Items by rights state")
    stt = Counter(i.get("status", "published") for i in items)
    axes[2].bar(list(stt), list(stt.values()), color=[C["green"], C["grey"], C["gold"], C["rose"]][:len(stt)])
    axes[2].set_title("Items by review status")
    axes[2].tick_params(axis="x", labelrotation=20, labelsize=8)
    for a in axes:
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    cached = sum(1 for i in items if i.get("cached"))
    fig.suptitle(f"Figure 20 - Demo corpus exported from the prototype: {len(items)} items, {cached} flagged for the offline cache",
                 x=0.01, ha="left", color=C["blue"], fontweight="bold")
    fig.tight_layout()
    save(fig, "20_demo_corpus.png", "demo")


def fig_ui_map():
    fig, ax = canvas(16, 8.6, "Figure 21 - Kiosk screen map (as implemented in prototype/ambedkar_kiosk.html)", ylim=(0, 60))
    box(ax, 2, 25, 13, 9, "ATTRACT\nsilent intro\n'Touch to begin'", fc=C["blue"], color="white", bold=True, fs=8.5)
    box(ax, 22, 25, 13, 9, "HOME\n5 category tiles ·\nstory of the day", fc=C["saffron"], color="white", bold=True, fs=8.5)
    arrow(ax, (15, 29.5), (22, 29.5), "PIR / touch", fs=7.5)
    dock = [("Explore", "filters: category ·\nyear · language · sort"), ("Timeline", "14 cards · 5 eras\n→ evidence"),
            ("Two-Minute Stories", "3 guided journeys"), ("Knowledge Map", "reviewed relations"),
            ("Ask the Archive", "cited answer or\nNOT VERIFIED"), ("Reading list", "temporary · QR\nhand-off (demo)")]
    for i, (t, d) in enumerate(dock):
        y = 52 - i * 8.6
        box(ax, 44, y, 16, 6.6, t, fc=C["ivory"], bold=True, fs=8.8)
        ax.text(61, y + 3.3, d, fontsize=7.6, color=C["ink2"], va="center")
        arrow(ax, (35, 29.5), (44, y + 3.3), color=C["mute"], lw=1)
    box(ax, 78, 44, 20, 9, "Document viewer\nscan | reviewed text | OCR\nprinted page vs PDF index", fc=C["tint"], fs=8)
    box(ax, 78, 31, 20, 9, "Media player\ncaptions · transcript seek\nAUTHENTIC / NARRATION badge", fc=C["tint"], fs=8)
    box(ax, 78, 18, 20, 9, "Provenance & rights\nsource register · rights\nstate · attribution", fc=C["tint"], fs=8)
    box(ax, 78, 4, 20, 9, "Overlays: Help · session\ncountdown · satisfaction\n(optional, anonymous)", fc="white", fs=8)
    for y in (48.5, 35.5, 22.5):
        arrow(ax, (72, 40), (78, y), color=C["chakra"], lw=1)
    box(ax, 2, 4, 33, 12, "Hidden operator surfaces (demo): Device console\n(simulate PIR/HOME/Wi-Fi loss, force idle),\nCurator console (FR-10), Test protocol, Visitor outcomes",
        fc=C["rose_t"], ec=C["rose"], fs=8)
    ax.text(2, 57, "Top strip: language (EN · HI · MR · TE) · text size · contrast · audio · online badge · clock", fontsize=8.5, color=C["ink2"])
    save(fig, "21_ui_screen_map.png")


def fig_gantt():
    tasks = [
        ("Sample list + rights register", 1, 1, "content"), ("Order HW · Pi OS · GPIO voltages", 1, 1, "hw"),
        ("DB · storage · admin draft form", 2, 1, "cloud"), ("Home/browse screens", 2, 1, "ui"), ("Pi event agent", 2, 1, "hw"),
        ("Ingest derivatives · page map · captions", 3, 1, "content"), ("Document viewer", 3, 1, "ui"),
        ("Hybrid search + fixed question set", 4, 1, "ai"), ("Cited Q&A · permission filter", 5, 1, "ai"),
        ("Offline cache · translation labels", 5, 1, "hw"), ("Security checks", 5, 1, "cloud"),
        ("Visitor / accessibility tests", 6, 1, "ui"), ("Metrics · rehearsal · handover", 6, 1, "content"),
    ]
    col = {"content": C["gold"], "hw": C["green"], "cloud": C["chakra"], "ui": C["saffron"], "ai": C["violet"]}
    fig, ax = plt.subplots(figsize=(14, 6))
    for i, (t, s, d, k) in enumerate(tasks):
        y = len(tasks) - i
        ax.barh(y, d - 0.08, left=s - 1 + 0.04, color=col[k], edgecolor="white")
        ax.text(s - 1 - 0.04, y, t, va="center", ha="right", fontsize=8, color=C["ink"])
    for g, wk in [("A", 1), ("B", 1), ("C", 3), ("D", 5), ("E", 6)]:
        ax.axvline(wk, color=C["rose"], ls="--", lw=1)
    for g, wk, off in [("Gate A/B", 1, 0), ("Gate C", 3, 0), ("Gate D", 5, 0), ("Gate E", 6, 0)]:
        ax.text(wk - 0.02, len(tasks) + 1.0, g, ha="right", color=C["rose"], fontsize=8.5, fontweight="bold")
    ax.set_xlim(-2.6, 6.05); ax.set_ylim(0.3, len(tasks) + 1.6)
    ax.axvspan(-2.6, 0, color="white", zorder=0)
    ax.set_xticks([0.5 + i for i in range(6)]); ax.set_xticklabels([f"Week {i + 1}" for i in range(6)])
    ax.set_yticks([])
    for k, v in col.items():
        ax.barh(-5, 0, color=v, label={"content": "content / curation", "hw": "embedded", "cloud": "cloud / catalogue",
                                       "ui": "kiosk UI / a11y", "ai": "search / AI"}[k])
    ax.legend(loc="lower left", fontsize=8, ncol=5, frameon=False, bbox_to_anchor=(0, -0.14))
    ax.set_title("Figure 22 - Six-week academic prototype plan with decision gates (assumes Pi, cloud account and sample material)",
                 loc="left", color=C["blue"])
    save(fig, "22_six_week_gantt.png", "target")


def fig_gates():
    fig, ax = canvas(16, 5.2, "Figure 23 - Decision gates: nothing moves forward on a convincing screen alone", ylim=(0, 34))
    g = [("A - Content", "approved rights and\nsource references before\nanything is public"),
         ("B - Hardware", "PIR OUT voltage and\ndisplay power verified\nbefore GPIO testing"),
         ("C - Retrieval", "page alignment + readable\naccess copy validated\nbefore chatbot enabled"),
         ("D - AI", "abstention / citation\nbenchmark passes before\nopen-ended Q&A demo"),
         ("E - Presentation", "network-off demo and\nvisitor reset tested\nIN THE VENUE")]
    for i, (t, d) in enumerate(g):
        x = 1 + i * 19.8
        ax.add_patch(Polygon([[x, 10], [x + 16, 10], [x + 18.5, 19], [x + 16, 28], [x, 28], [x + 2.5, 19]],
                             fc=[C["gold_t"], C["green_t"], C["tint"], C["violet_t"], C["saffron_t"]][i], ec=C["blue"], lw=1.3))
        ax.text(x + 9.2, 24.5, t, ha="center", fontweight="bold", color=C["blue"], fontsize=10)
        ax.text(x + 9.2, 17, d, ha="center", va="center", fontsize=8, color=C["ink2"])
    ax.text(1, 4, "Failing a gate means: fix and re-test, or descope the feature from the public demo (e.g. show links instead of generated answers).",
            fontsize=9, color=C["rose"])
    save(fig, "23_decision_gates.png")


def fig_storage():
    pages = np.array([1_000, 5_000, 10_000, 50_000])
    mib = [10, 25, 60]
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    w = 0.25
    for i, m in enumerate(mib):
        axes[0].bar(np.arange(len(pages)) + (i - 1) * w, [sizing.master_gib(p, m) for p in pages], w,
                    label=f"{m} MiB/page", color=[C["teal"], C["chakra"], C["saffron_d"]][i])
    axes[0].set_xticks(range(len(pages))); axes[0].set_xticklabels([f"{p:,} pages" for p in pages])
    axes[0].set_yscale("log"); axes[0].set_ylabel("GiB of image masters (log)")
    axes[0].set_title("Masters only, by assumed mean page size"); axes[0].legend(frameon=False)
    one = [sizing.master_gib(p) for p in pages]
    three = [sizing.logical_copies_gib(p) for p in pages]
    axes[1].bar(np.arange(len(pages)) - 0.2, one, 0.4, label="1 copy", color=C["chakra"])
    axes[1].bar(np.arange(len(pages)) + 0.2, three, 0.4, label="3 logical copies", color=C["gold"])
    for i, (a, b) in enumerate(zip(one, three)):
        axes[1].text(i - 0.2, a, f"{a:,.1f}", ha="center", va="bottom", fontsize=7.5)
        axes[1].text(i + 0.2, b, f"{b:,.1f}", ha="center", va="bottom", fontsize=7.5)
    axes[1].set_xticks(range(len(pages))); axes[1].set_xticklabels([f"{p:,}" for p in pages])
    axes[1].set_yscale("log"); axes[1].set_title("25 MiB/page: 1 vs 3 logical copies (GiB)"); axes[1].legend(frameon=False)
    for a in axes:
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.suptitle("Figure 24 - Storage scenarios computed by heritage_core.sizing (1,000 pages × 25 MiB ≈ 24.4 GiB; ×3 ≈ 73.2 GiB). "
                 "Excludes AV, derivatives, DB.", x=0.01, ha="left", color=C["blue"], fontweight="bold", fontsize=11)
    fig.tight_layout()
    save(fig, "24_storage_scenarios.png", "target")


RISKS = [("Unclear reuse rights", 3, 5), ("False quote / speaker / page", 3, 5), ("OCR corrupts names", 4, 3),
         ("Network / cloud outage", 3, 3), ("GPIO overvoltage / poor PSU", 2, 4), ("Inaccessible touch layout", 3, 4),
         ("Cloud / AI cost overrun", 2, 3), ("Timeline overstates claims", 2, 4), ("Pi theft / tampering", 2, 3)]


def fig_risk():
    fig, ax = plt.subplots(figsize=(13, 7))
    for i in range(1, 6):
        for j in range(1, 6):
            sc = i * j
            ax.add_patch(Rectangle((i - 0.5, j - 0.5), 1, 1, fc=C["green_t"] if sc <= 4 else C["gold_t"] if sc <= 9 else C["saffron_t"] if sc <= 14 else C["rose_t"], ec="white"))
    off = Counter()
    for n, (name, lik, imp) in enumerate(RISKS, 1):
        k = (lik, imp)
        dx = [-0.22, 0.22, -0.22, 0.22][off[k] % 4]; dy = [0.18, 0.18, -0.18, -0.18][off[k] % 4]
        off[k] += 1
        ax.add_patch(Circle((lik + dx, imp + dy), 0.15, fc=C["blue"], zorder=3))
        ax.text(lik + dx, imp + dy, str(n), ha="center", va="center", color="white", fontsize=9, fontweight="bold", zorder=4)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.set_aspect("equal")
    ax.set_xlabel("Likelihood (1-5)"); ax.set_ylabel("Impact (1-5)")
    legend = "\n".join(f"{n:>2}. {name}  (L{l} × I{im} = {l * im})" for n, (name, l, im) in enumerate(RISKS, 1))
    fig.text(0.62, 0.5, legend, fontsize=9.5, va="center", family="monospace", color=C["ink"])
    fig.subplots_adjust(right=0.6)
    ax.set_title("Figure 25 - Risk workshop starting scores BEFORE mitigation\n(team assumptions, not an empirical assessment - re-score with stakeholders)",
                 loc="left", color=C["blue"], fontsize=11)
    save(fig, "25_risk_matrix.png", "target")


def fig_targets():
    t = [("Search: citable item in top 5", "≥ 80 %*"), ("Citation links resolve to permitted page/time", "100 %"),
         ("Out-of-scope questions abstain", "100 % of 10"), ("Permission-pending leaks", "0"),
         ("Cold boot → ATTRACT", "measure; target TBD"), ("PIR approach → Home", "measure; target TBD"),
         ("HOME press → cleared session", "every trial"), ("Wi-Fi off → usable offline exhibit", "every trial")]
    fig, ax = plt.subplots(figsize=(14, 4.8)); ax.axis("off")
    ax.set_xlim(0, 4); ax.set_ylim(0, 2.2)
    for i, (a, b) in enumerate(t):
        x = (i % 4); y = 1.1 if i < 4 else 0
        ax.add_patch(FancyBboxPatch((x + 0.05, y + 0.08), 0.9, 0.9, boxstyle="round,pad=0.01,rounding_size=0.05",
                                    fc=C["ivory"], ec=C["saffron_d"], lw=1.3))
        ax.text(x + 0.5, y + 0.62, b, ha="center", fontsize=15, fontweight="bold", color=C["blue"])
        ax.text(x + 0.5, y + 0.28, a, ha="center", fontsize=8.4, color=C["ink2"], wrap=True)
    ax.set_title("Figure 26 - Proposed pilot acceptance gates (set final thresholds with supervisor and curator)\n"
                 "* the 80 % value is a placeholder proposed by this README, not stated in the design document", loc="left",
                 color=C["blue"], fontsize=11)
    save(fig, "26_pilot_targets.png", "target")


def fig_test_coverage():
    tests = RAW["tests"]
    fam = Counter(t["id"].split("-")[0] for t in tests)
    mode = Counter(t["mode"] for t in tests)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    axes[0].bar(list(fam), list(fam.values()), color=C["chakra"])
    axes[0].set_title(f"{len(tests)} protocol test cases by family")
    lbl = {"hw": "needs real hardware", "demo": "runnable in HTML demo", "corpus": "needs test corpus", "be": "needs backend"}
    axes[1].barh([lbl[k] for k in mode], list(mode.values()), color=[C["green"], C["gold"], C["rose"], C["violet"]][:len(mode)])
    axes[1].set_title("Where each case can actually be executed")
    for a in axes:
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.suptitle("Figure 27 - Test protocol coverage (from the prototype's TESTS table). Counts of cases, NOT pass rates.",
                 x=0.01, ha="left", color=C["blue"], fontweight="bold")
    fig.tight_layout()
    save(fig, "27_test_coverage.png", "demo")


def fig_repo_map():
    fig, ax = canvas(16, 8, "Figure 28 - Repository map (multi-repo; shared contracts live in one place)", ylim=(0, 58))
    box(ax, 36, 44, 28, 9, "heritage-archive-main  (this repo)\nREADME · architecture · contracts ·\nreference rules + tests · prototype", fc=C["blue"], color="white", bold=True, fs=8.8)
    repos = [(1, 24, "heritage-kiosk-agent", "Python · GPIO bridge ·\nevent relay · manifest sync\n· systemd units"),
             (21, 24, "heritage-kiosk-ui", "React + TS static build ·\ni18n · a11y · offline\nbadges · Playwright"),
             (41, 24, "heritage-archive-api", "FastAPI · PostgreSQL ·\npgvector · rights gate ·\n/v1 public/device/admin"),
             (61, 24, "heritage-ingest-worker", "OCR · ASR · fixity ·\nembeddings · job table ·\nreview queue feed"),
             (81, 24, "heritage-infra", "IaC templates · env\nexamples · backup and\nrestore scripts")]
    for x, y, t, d in repos:
        box(ax, x, y, 18, 12, "", fc=C["ivory"])
        ax.text(x + 9, y + 9.5, t, ha="center", fontsize=8.6, fontweight="bold", color=C["blue"])
        ax.text(x + 9, y + 4.3, d, ha="center", va="center", fontsize=7.4, color=C["ink2"])
        arrow(ax, (50, 44), (x + 9, y + 12), color=C["mute"], lw=1)
    box(ax, 21, 6, 58, 9, "contracts/ : openapi.yaml · offline-manifest.schema.json · ingest-manifest.schema.json · ask-response.schema.json\n"
        "reference/heritage_core : executable rules + shared test vectors (every service runs them in CI)", fc=C["gold_t"], ec=C["gold"], fs=8.3)
    for x in (10, 30, 50, 70, 90):
        arrow(ax, (x, 24), (min(max(x, 25), 75), 15), color=C["gold"], ls="--", lw=1)
    save(fig, "28_repo_map.png")


def fig_cicd():
    fig, ax = canvas(16, 5, "Figure 29 - CI/CD pipeline (per repo) - secrets only from the CI secret store", ylim=(0, 32))
    st = ["push / PR", "lint + type\n(ruff · mypy · eslint · tsc)", "unit tests +\nshared vectors", "contract tests\n(OpenAPI · JSON Schema)",
          "security scan\n(deps · secrets)", "build artefacts\n(UI bundle · API image)", "staging deploy\n+ smoke", "manual approval\n(2 people)", "production /\nPi fleet rollout"]
    for i, s in enumerate(st):
        x = 1 + i * 11
        box(ax, x, 12, 9.6, 10, s, fc=C["rose_t"] if i == 7 else C["tint"], fs=7.6)
        if i:
            arrow(ax, (x - 1.4, 17), (x, 17))
    ax.text(1, 4, "Pi rollout = signed UI bundle + agent package pinned by version; the Pi pulls updates, the cloud never pushes shell commands.",
            fontsize=8.8, color=C["ink2"])
    save(fig, "29_cicd_pipeline.png")


def fig_deployment():
    fig, ax = canvas(16, 7.4, "Figure 30 - Deployment topology (prototype single kiosk; pilot = small fleet)", ylim=(0, 54))
    zone(ax, 1, 4, 30, 46, "VENUE", C["tint"], C["chakra"])
    zone(ax, 36, 4, 63, 46, "CLOUD / APPROVED HOSTING (provider TBD)", C["saffron_t"], C["saffron_d"])
    box(ax, 4, 32, 24, 10, "Kiosk 01 (Pi 5)\nChromium kiosk · agent ·\nSQLite cache", fs=8.5)
    box(ax, 4, 18, 24, 8, "Kiosk 02..N (pilot)\nsame image, unique token", fs=8.5, fc="white")
    box(ax, 4, 7, 24, 7, "Venue network\nEthernet preferred · Wi-Fi fallback", fs=8, fc="white")
    box(ax, 40, 34, 17, 9, "Reverse proxy\nTLS · rate limit", fs=8.5)
    box(ax, 61, 34, 17, 9, "API containers\n(FastAPI)", fs=8.5)
    box(ax, 82, 34, 15, 9, "Worker\ncontainers", fs=8.5)
    box(ax, 40, 18, 17, 9, "PostgreSQL\n+ pgvector", fs=8.5, fc=C["gold_t"], ec=C["gold"])
    box(ax, 61, 18, 17, 9, "Object storage\n(private buckets)", fs=8.5, fc=C["gold_t"], ec=C["gold"])
    box(ax, 82, 18, 15, 9, "Model / OCR /\nASR provider", fs=8.5, fc=C["violet_t"], ec=C["violet"])
    box(ax, 40, 7, 57, 7, "Independent backup target (different account/site) · uptime monitor · log store", fs=8.3, fc="white")
    arrow(ax, (28, 37), (40, 38.5), "HTTPS")
    arrow(ax, (57, 38.5), (61, 38.5)); arrow(ax, (78, 38.5), (82, 38.5))
    arrow(ax, (69, 34), (48, 27)); arrow(ax, (69, 34), (69, 27)); arrow(ax, (89, 34), (89, 27), color=C["violet"])
    arrow(ax, (48, 18), (48, 14), color=C["gold"]); arrow(ax, (69, 18), (69, 14), color=C["gold"])
    save(fig, "30_deployment_topology.png")


def fig_roadmap():
    fig, ax = canvas(16, 5.6, "Figure 31 - Institutional scale-up roadmap (Phases 2-3 are NOT part of the class demo)", ylim=(0, 38))
    ph = [("PHASE 1 - Academic proof", "one Pi kiosk · small cleared corpus ·\nreviewed multilingual samples ·\nfixed evaluation set", C["green_t"], C["green"]),
          ("PHASE 2 - Institution pilot", "permission agreements · collection policy ·\nmulti-kiosk fleet · approved hosting ·\nprofessional digitisation · security &\naccessibility audit · restoration drills", C["gold_t"], C["gold"]),
          ("PHASE 3 - Wider archive", "IIIF where useful · distributed curation ·\nname authority + knowledge graph ·\nmore Indian languages · research\naccounts where justified", C["tint"], C["chakra"])]
    for i, (t, d, fc, ec) in enumerate(ph):
        x = 1 + i * 33
        ax.add_patch(Polygon([[x, 6], [x + 29, 6], [x + 32, 19], [x + 29, 32], [x, 32], [x + 3, 19]], fc=fc, ec=ec, lw=1.6))
        ax.text(x + 16, 28, t, ha="center", fontweight="bold", color=ec, fontsize=10.5)
        ax.text(x + 16, 16.5, d, ha="center", va="center", fontsize=8.3, color=C["ink2"])
    ax.text(1, 1.5, "The scarce resource is curatorial capacity and rights management - not a larger model. Claim 'full archive access' only when coverage and permissions warrant it.",
            fontsize=8.8, color=C["rose"])
    save(fig, "31_scaleup_roadmap.png")


def fig_ocr_cer():
    rows = []
    for it in RAW["items"]:
        if it["kind"] not in ("writing", "constitutional"):
            continue
        for pg in it.get("pages", []):
            if pg.get("ocr") and pg.get("passages"):
                ref = pg["passages"][0]["text"]
                rows.append((f'{it["id"]} p.{pg["printed"]}', cer(pg["ocr"], ref), wer(pg["ocr"], ref), it["kind"]))
    fig, ax = plt.subplots(figsize=(14, 5))
    x = np.arange(len(rows))
    ax.bar(x - 0.2, [r[1] * 100 for r in rows], 0.4, label="CER %", color=C["chakra"])
    ax.bar(x + 0.2, [r[2] * 100 for r in rows], 0.4, label="WER %", color=C["saffron"])
    ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("error rate vs reviewed passage (%)")
    ax.legend(frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Figure 32 - CER/WER of the sample 'unreviewed OCR' strings embedded in the prototype vs their reviewed text\n"
                 "Demonstrates the metric pipeline only: the OCR strings are hand-made demo samples, not engine output. "
                 "High bars = sample text not aligned to the first passage.", loc="left", color=C["blue"], fontsize=10.5)
    save(fig, "32_ocr_cer_demo.png", "demo")
    return rows


def retrieval_benchmark():
    """Queries = first key of each prototype ASK_SET entry. A result counts as relevant if it is one of the
    passages the prototype cites, or (when the prototype cites a whole media item) any segment of that item."""
    idx = HybridIndex(DATA["typed_items"])
    by_id = {p.id: p for p in idx.passages}
    qs = []
    for a in RAW["ask_set"]:
        rel = {c["passage"] if c.get("passage") else "ITEM:" + c["item"] for c in a["cites"]}
        qs.append((a["keys"][0], rel))
    res = {"lexical": [], "dense": [], "hybrid": []}
    for q, rel in qs:
        runs = {"lexical": [idx.passages[i].id for i, _ in idx.bm25(tokens(q))],
                "dense": [idx.passages[i].id for i, _ in idx.dense(q)],
                "hybrid": [h.passage.id for h in idx.search(q, k=10)]}
        for k, lst in runs.items():
            marked = [pid if pid in rel else ("ITEM:" + by_id[pid].item_id) for pid in lst]
            res[k].append((hit_at_k(marked, rel), reciprocal_rank(marked, rel)))
    return qs, res


def fig_retrieval_bench():
    qs, res = retrieval_benchmark()
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    names = list(res)
    h = [np.mean([r[0] for r in res[n]]) for n in names]
    m = [np.mean([r[1] for r in res[n]]) for n in names]
    axes[0].bar(names, h, color=[C["chakra"], C["teal"], C["saffron_d"]])
    axes[0].set_ylim(0, 1.05); axes[0].set_title(f"Hit@5 over {len(qs)} curated demo questions")
    axes[1].bar(names, m, color=[C["chakra"], C["teal"], C["saffron_d"]])
    axes[1].set_ylim(0, 1.05); axes[1].set_title("Mean reciprocal rank")
    for a, vals in zip(axes, (h, m)):
        for i, v in enumerate(vals):
            a.text(i, v + 0.02, f"{v:.2f}", ha="center")
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.suptitle("Figure 33 - Reference retrieval on the demo corpus (queries = ASK_SET keys; relevance = prototype's cited passages).\n"
                 "Toy benchmark: 'dense' is a character-trigram stand-in, not an embedding model.", x=0.01, ha="left",
                 color=C["blue"], fontweight="bold", fontsize=10.5)
    fig.tight_layout()
    save(fig, "33_retrieval_benchmark_demo.png", "demo")
    return qs, res


def fig_curation():
    fig, ax = canvas(16, 5.4, "Figure 34 - Curation workflow (FR-10) as implemented in the prototype's curator console", ylim=(0, 36))
    st = [("draft", C["grey"]), ("in_review", C["gold_t"]), ("approved_1", C["tint"]), ("published", C["green_t"]), ("withdrawn", C["rose_t"])]
    xs = [2, 22, 42, 62, 82]
    for (s, fc), x in zip(st, xs):
        box(ax, x, 16, 15, 8, s, fc=fc, bold=True, fs=10)
    arrow(ax, (17, 20), (22, 20), "Curator:\nsend for review", fs=7.5, toff=(0, 3.5))
    arrow(ax, (37, 20), (42, 20), "Reviewer 1:\ncontent approve", fs=7.5, toff=(0, 3.5))
    arrow(ax, (57, 20), (62, 20), "Reviewer 2:\nrights checkbox\n+ publish", fs=7.5, toff=(0, 4.2))
    arrow(ax, (77, 20), (82, 20), "withdraw", fs=7.5, color=C["rose"], toff=(0, 2.5))
    arrow(ax, (89.5, 16), (9.5, 16), "restore → draft (no public visibility)", fs=7.5, color=C["mute"], rad=0.25, toff=(0, -9))
    ax.text(62, 32, "published → enters public index; offline cache sync deferred until reconnect", fontsize=8, color=C["green"])
    ax.text(62, 29.5, "withdrawn → removed from index, search, reading lists; manifest invalidated", fontsize=8, color=C["rose"])
    save(fig, "34_curation_workflow.png")


def fig_manifest():
    fig, ax = canvas(16, 5.8, "Figure 35 - Offline manifest lifecycle (heritage_core.manifest)", ylim=(0, 40))
    st = [("build", "only OFFLINE_CACHE-\npermitted items"), ("sign", "HMAC-SHA256 (proto)\nEd25519 (future)"),
          ("GET /v1/offline-manifest", "Pi agent pulls\nwhen online"), ("verify", "signature · expiry +\ngrace · version > current"),
          ("atomic apply", "temp file · fsync ·\nos.replace"), ("revoke", "items no longer listed\nare purged")]
    for i, (t, d) in enumerate(st):
        x = 1 + i * 16.4
        box(ax, x, 20, 14.5, 9, t, fc=C["tint"], bold=True, fs=8.8)
        ax.text(x + 7.25, 14.5, d, ha="center", va="center", fontsize=7.8, color=C["ink2"])
        if i:
            arrow(ax, (x - 1.9, 24.5), (x, 24.5))
    box(ax, 50, 1.5, 30, 7, "reject: bad signature · stale/rollback ·\nexpired beyond grace → FAIL CLOSED", fc=C["rose_t"], ec=C["rose"], fs=8)
    arrow(ax, (57, 20), (62, 8.5), color=C["rose"])
    save(fig, "35_manifest_lifecycle.png")


def fig_threats():
    threats = ["Stolen Pi token", "Unauthorised source replication", "Prompt injection in documents", "False citations",
               "Malicious PDF / media upload", "Long retention of spoken queries", "Visitor exits Chromium", "Offline cache of withdrawn item"]
    controls = ["Transport TLS", "Scoped device cred", "Admin MFA + review", "Rights filter pre-retrieval",
                "Server-side secrets", "Evidence-not-instructions", "Media validation / isolation", "Session purge", "Manifest expiry"]
    M = np.array([
        [1, 2, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 2, 0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 2, 0, 0, 0], [0, 0, 1, 1, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 2, 0, 0], [1, 0, 0, 0, 0, 0, 0, 2, 0], [0, 1, 0, 0, 1, 0, 0, 1, 0], [0, 0, 0, 1, 0, 0, 0, 0, 2]])
    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.imshow(M, cmap=matplotlib.colors.ListedColormap(["#F4F5F8", C["gold_t"], C["green"]]), aspect="auto")
    ax.set_xticks(range(len(controls))); ax.set_xticklabels(controls, rotation=30, ha="right", fontsize=8.3)
    ax.set_yticks(range(len(threats))); ax.set_yticklabels(threats, fontsize=8.5)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if M[i, j]:
                ax.text(j, i, "primary" if M[i, j] == 2 else "helps", ha="center", va="center", fontsize=7.3,
                        color="white" if M[i, j] == 2 else C["ink"])
    ax.set_title("Figure 36 - Threat → control mapping (design intent; not a penetration-test result)", loc="left", color=C["blue"])
    save(fig, "36_threat_controls.png")


def fig_av_workflow():
    fig, ax = canvas(16, 5.2, "Figure 37 - Audio / video workflow: authentic recordings and synthetic narration never mix", ylim=(0, 34))
    st = [("Receive source", "highest quality as\nrights allow"), ("Preserve", "master kept; never\n'streaming = archive'"),
          ("Derive", "MP4/H.264 playback ·\naudio derivative"), ("Caption", ".vtt + timestamped\ntranscript (ASR =\nunreviewed)"),
          ("Review", "names · quotations ·\nspeaker verified"), ("Publish", "badge: AUTHENTIC\nRECORDING or MODERN\nNARRATION")]
    for i, (t, d) in enumerate(st):
        x = 1 + i * 16.4
        box(ax, x, 17, 14.5, 8, t, fc=C["violet_t"], ec=C["violet"], bold=True, fs=9)
        ax.text(x + 7.25, 11, d, ha="center", va="center", fontsize=7.8, color=C["ink2"])
        if i:
            arrow(ax, (x - 1.9, 21), (x, 21), color=C["violet"])
    ax.text(1, 2.5, "Never fabricate an 'original' Ambedkar voice. Transcript click seeks the player; a media-grounded citation seeks the same segment.",
            fontsize=8.8, color=C["rose"])
    save(fig, "37_av_workflow.png")


def fig_session_reset():
    fig, ax = canvas(15, 6.4, "Figure 38 - Session reset: HOME button and idle timeout run the same routine", ylim=(0, 44))
    box(ax, 2, 30, 18, 8, "HOME press\nBCM27 falling, debounced", fc=C["tint"], fs=8.5)
    box(ax, 2, 16, 18, 8, "Idle ≥ 120 s → warning\n20 s countdown expires", fc=C["saffron_t"], ec=C["saffron_d"], fs=8.5)
    box(ax, 28, 20, 20, 14, "resetSession()", fc=C["blue"], color="white", bold=True, fs=11)
    arrow(ax, (20, 34), (28, 29)); arrow(ax, (20, 20), (28, 25))
    clears = ["stop media playback", "clear reading list + QR hand-off", "clear question box / answer panel",
              "clear filters, story, viewer state", "record anonymous session counters only", "return to ATTRACT"]
    for i, c in enumerate(clears):
        box(ax, 56, 36 - i * 5.6, 26, 4.4, c, fc=C["green_t"] if i < 5 else C["tint"], ec=C["green"], fs=8.2)
        arrow(ax, (48, 27), (56, 38.2 - i * 5.6), lw=0.9, color=C["mute"])
    box(ax, 86, 18, 12, 10, "NOT cleared:\noffline cache ·\nmanifest", fc=C["gold_t"], ec=C["gold"], fs=8.2)
    save(fig, "38_session_reset.png")


def fig_benchmark_outcomes():
    """Figure 39 - demo benchmark outcomes, computed by scripts/run_benchmark.py (not hand-entered)."""
    import importlib.util
    import re as _re
    spec = importlib.util.spec_from_file_location("rb", ROOT / "scripts" / "run_benchmark.py")
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    res = rb.main(str(ROOT / "data" / "benchmark_demo.json"))
    s, rows = res["summary"], res["rows"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw={"width_ratios": [1, 1.25]})
    cats = [("Cited a labelled passage", s["answered_with_labelled_citation"], C["green"]),
            ("Other passage, same item", s["other_passage_same_item"], C["gold"]),
            ("Cited an unlabelled item", s["wrong_item"], C["rose"]),
            ("False abstention", s["false_abstentions"], C["saffron"])]
    left = 0
    for name, v, col in cats:
        a1.barh(1, v, left=left, color=col, edgecolor="white", label=f"{name} ({v})")
        left += v
    left = 0
    for name, v, col in [("Correct abstention", s["correct_abstentions"], C["green"]),
                         ("Unsupported answer", s["unsupported_answers"], C["rose"])]:
        a1.barh(0, v, left=left, color=col, edgecolor="white", hatch="//" if "Unsupported" in name else None,
                label=f"{name} ({v})")
        left += v
    a1.set_yticks([0, 1], [f"Probes (n={s['negative_n']})\nunanswerable + misattribution", f"Answerable (n={s['answerable_n']})"])
    a1.set_xlabel("Questions")
    a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=8.5, frameon=False)
    a1.set_title("Outcomes per bucket", loc="left", color=C["blue"])
    a1.spines[["top", "right"]].set_visible(False)
    probes = [r for r in rows if r["bucket"] != "answerable"]
    cov = [float(m.group(1)) if (m := _re.search(r"\(([0-9.]+)\)", r["reason"])) else 0.0 for r in probes]
    cols = [C["saffron"] if c >= 0.4 else C["blue"] for c in cov]
    a2.bar([r["id"] for r in probes], cov, color=cols)
    a2.axhline(0.5, color=C["rose"], ls="--", lw=1.5)
    a2.text(len(probes) - 0.5, 0.515, "abstain below min_coverage = 0.5", ha="right", color=C["rose"], fontsize=9)
    a2.set_ylim(0, 0.7)
    a2.set_ylabel("Best evidence coverage (0 = no lexical support)")
    a2.tick_params(axis="x", rotation=60, labelsize=8)
    a2.set_title("Probe coverage vs threshold (orange = within 0.1 of it)", loc="left", color=C["blue"])
    a2.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Figure 39 - Demo benchmark: 8 answerable questions + 13 negative probes through the reference answer contract",
                 x=0.01, ha="left", color=C["blue"], fontsize=12)
    fig.tight_layout(rect=(0, 0.02, 1, 0.94))
    save(fig, "39_benchmark_outcomes.png", "demo")


def main():
    print("Generating diagrams ...")
    for f in [fig_banner, fig_system_context, fig_split_architecture, fig_gpio_wiring, fig_header_map, fig_state_machine,
              fig_boot_sequence, fig_pi_processes, fig_offline_contract, fig_cloud_services, fig_trust_boundaries,
              fig_ingest_pipeline, fig_rights_states, fig_rights_matrix, fig_data_model, fig_preservation,
              fig_hybrid_retrieval, fig_rag_sequence, fig_knowledge_map, fig_timeline, fig_corpus, fig_ui_map, fig_gantt,
              fig_gates, fig_storage, fig_risk, fig_targets, fig_test_coverage, fig_repo_map, fig_cicd, fig_deployment,
              fig_roadmap, fig_curation, fig_manifest, fig_threats, fig_av_workflow, fig_session_reset, fig_benchmark_outcomes]:
        f()
    rows = fig_ocr_cer()
    qs, res = fig_retrieval_bench()
    # write computed numbers so the README can quote them verbatim
    summary = {
        "ocr": [{"page": r[0], "cer": round(r[1], 4), "wer": round(r[2], 4)} for r in rows],
        "retrieval": {k: {"hit@5": round(float(np.mean([x[0] for x in v])), 3),
                          "mrr": round(float(np.mean([x[1] for x in v])), 3),
                          "per_query": [{"q": q, "hit": x[0], "rr": round(x[1], 3)} for (q, _), x in zip(qs, v)]}
                      for k, v in res.items()},
    }
    (OUT / "computed_metrics.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print("  wrote diagrams/computed_metrics.json")


if __name__ == "__main__":
    main()
