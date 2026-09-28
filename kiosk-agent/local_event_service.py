#!/usr/bin/env python3
"""Loopback-only relay: POST /device/event -> Server-Sent Events at GET /device/stream.

The browser cannot read GPIO; the kiosk UI subscribes to /device/stream.
Binds to 127.0.0.1 ONLY. Standard library only (prototype).
"""
from __future__ import annotations

import json
import mimetypes
import os
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ALLOWED_EVENTS = {"visitor_approached", "home_pressed", "net_down", "net_up"}
_subscribers: list[queue.Queue] = []
_lock = threading.Lock()
# Optional: serve the static kiosk UI build from the same loopback origin so that
# EventSource("/device/stream") is same-origin. Unset = event relay only.
UI_DIR: Path | None = Path(os.environ["KIOSK_UI_DIR"]).resolve() if os.environ.get("KIOSK_UI_DIR") else None


def resolve_static(ui_dir: Path, url_path: str) -> Path | None:
    """Map a URL path to a file inside ui_dir; None if outside it or missing (no traversal)."""
    rel = url_path.split("?", 1)[0].split("#", 1)[0].lstrip("/") or "index.html"
    target = (ui_dir / rel).resolve()
    if target != ui_dir and ui_dir not in target.parents:
        return None
    if target.is_dir():
        target = target / "index.html"
    return target if target.is_file() else None


def publish(evt: dict) -> int:
    with _lock:
        for q in _subscribers:
            q.put(evt)
        return len(_subscribers)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # keep journald quiet; no visitor data is logged
        pass

    def do_POST(self):
        if self.path != "/device/event" or self.client_address[0] != "127.0.0.1":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", "0"))
        if n > 1024:
            self.send_error(413)
            return
        try:
            evt = json.loads(self.rfile.read(n))
        except json.JSONDecodeError:
            self.send_error(400)
            return
        if evt.get("event") not in ALLOWED_EVENTS:
            self.send_error(422)
            return
        publish({"event": evt["event"], "ts": evt.get("ts")})
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path != "/device/stream":
            self._static()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        q: queue.Queue = queue.Queue()
        with _lock:
            _subscribers.append(q)
        try:
            while True:
                evt = q.get()
                self.wfile.write(f"data: {json.dumps(evt)}\n\n".encode())
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            with _lock:
                _subscribers.remove(q)


    def _static(self):
        f = resolve_static(UI_DIR, self.path) if UI_DIR else None
        if f is None:
            self.send_error(404)
            return
        body = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(f.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def serve(port: int = int(os.environ.get("KIOSK_EVENT_PORT", "8765"))) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":  # pragma: no cover
    serve().serve_forever()
