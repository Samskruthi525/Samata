"""Signed, versioned offline manifest for the Pi cache (design doc §5.3).

* Only items permitted for Action.OFFLINE_CACHE are included.
* HMAC-SHA256 signature (prototype). Production should prefer an asymmetric
  signature (e.g. Ed25519) so the Pi holds only a public verification key.
* Fail closed: expired beyond grace -> cache must not be shown.
* Updates are atomic (write temp file, fsync, os.replace).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .corpus import Item
from .rights import Action


class ManifestError(Exception):
    pass


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def build(items: dict[str, Item], version: int, key: bytes, *, issued: datetime | None = None,
          ttl: timedelta = timedelta(days=7)) -> dict:
    issued = issued or datetime.now(timezone.utc)
    entries = sorted(({"item_id": it.id, "title": it.title, "kind": it.kind}
                      for it in items.values() if it.allowed(Action.OFFLINE_CACHE)), key=lambda e: e["item_id"])
    body = {"version": version, "issued_at": issued.isoformat(), "expires_at": (issued + ttl).isoformat(),
            "items": entries}
    return {"body": body, "sig": hmac.new(key, _canon(body), hashlib.sha256).hexdigest()}


def verify(manifest: dict, key: bytes, *, now: datetime | None = None,
           grace: timedelta = timedelta(hours=24)) -> dict:
    body = manifest.get("body")
    if body is None or "sig" not in manifest:
        raise ManifestError("malformed manifest")
    good = hmac.new(key, _canon(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(good, manifest["sig"]):
        raise ManifestError("bad signature")
    now = now or datetime.now(timezone.utc)
    if now > datetime.fromisoformat(body["expires_at"]) + grace:
        raise ManifestError("manifest expired beyond grace period - fail closed")
    return body


@dataclass
class CacheState:
    version: int
    item_ids: frozenset[str]


def apply_update(current: CacheState | None, manifest: dict, key: bytes, store: Path, **kw) -> tuple[CacheState, set[str]]:
    """Verify, reject rollbacks, atomically persist. Returns (new_state, revoked_ids)."""
    body = verify(manifest, key, **kw)
    if current and body["version"] <= current.version:
        raise ManifestError(f"stale manifest v{body['version']} <= v{current.version}")
    new_ids = frozenset(e["item_id"] for e in body["items"])
    revoked = set(current.item_ids - new_ids) if current else set()
    store.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=store.parent, prefix=".manifest-")
    with os.fdopen(fd, "wb") as f:
        f.write(_canon(manifest))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, store)
    return CacheState(body["version"], new_ids), revoked
