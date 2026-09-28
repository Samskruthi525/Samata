from datetime import datetime, timedelta, timezone
import pytest
from heritage_core import corpus, manifest
from heritage_core.manifest import ManifestError, CacheState
from heritage_core.rights import ReviewStatus

KEY = b"test-only-key-not-a-secret"
T0 = datetime(2026, 9, 26, tzinfo=timezone.utc)


def items():
    return corpus.load()["typed_items"]


def test_only_cacheable_items():
    m = manifest.build(items(), 1, KEY, issued=T0)
    ids = {e["item_id"] for e in m["body"]["items"]}
    assert ids == {"WS-001", "CR-001", "CR-003", "MP-002", "AV-002"}


def test_tamper_detected():
    m = manifest.build(items(), 1, KEY, issued=T0)
    m["body"]["items"].append({"item_id": "AV-003", "title": "x", "kind": "media"})
    with pytest.raises(ManifestError, match="signature"):
        manifest.verify(m, KEY, now=T0)


def test_fail_closed_after_grace():
    m = manifest.build(items(), 1, KEY, issued=T0, ttl=timedelta(days=7))
    manifest.verify(m, KEY, now=T0 + timedelta(days=7, hours=23))
    with pytest.raises(ManifestError, match="fail closed"):
        manifest.verify(m, KEY, now=T0 + timedelta(days=8, hours=1))


def test_update_is_atomic_and_revokes(tmp_path):
    its = items()
    store = tmp_path / "cache" / "manifest.json"
    s1, rev = manifest.apply_update(None, manifest.build(its, 1, KEY, issued=T0), KEY, store, now=T0)
    assert not rev and store.exists()
    its["MP-002"].status = ReviewStatus.WITHDRAWN
    s2, rev = manifest.apply_update(s1, manifest.build(its, 2, KEY, issued=T0), KEY, store, now=T0)
    assert rev == {"MP-002"} and "MP-002" not in s2.item_ids
    assert not list(store.parent.glob(".manifest-*"))


def test_rollback_rejected(tmp_path):
    m = manifest.build(items(), 3, KEY, issued=T0)
    with pytest.raises(ManifestError, match="stale"):
        manifest.apply_update(CacheState(5, frozenset()), m, KEY, tmp_path / "m.json", now=T0)
