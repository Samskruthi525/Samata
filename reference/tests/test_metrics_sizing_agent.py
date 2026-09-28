import math
import pytest
from heritage_core import metrics, sizing
from pi_gpio_bridge import Bridge, loopback_only


def test_cer_wer():
    assert metrics.cer("abc", "abc") == 0
    assert metrics.cer("abd", "abc") == pytest.approx(1 / 3)
    assert metrics.wer("a b d", "a b c") == pytest.approx(1 / 3)


def test_ranking_metrics():
    assert metrics.precision_at_k(["a", "x", "b", "y", "z"], {"a", "b"}) == 0.4
    assert metrics.reciprocal_rank(["x", "a"], {"a"}) == 0.5
    assert math.isnan(metrics.citation_validity([], set()))


def test_storage_matches_design_doc():
    assert round(sizing.master_gib(1000), 1) == 24.4
    assert round(sizing.logical_copies_gib(1000), 1) == 73.2


def test_bridge_refuses_cloud_url():
    with pytest.raises(ValueError):
        loopback_only("https://archive.example.org/device/event")
    assert loopback_only("http://127.0.0.1:8765/device/event")


def test_bridge_cooldown_and_failure_counting():
    t = [0.0]; sent = []
    b = Bridge("http://127.0.0.1:8765/device/event", clock=lambda: t[0], cooldown_s=10, sender=sent.append)
    assert b.on_motion() and not b.on_motion()
    t[0] = 11; assert b.on_motion()
    assert b.on_home() and [e["event"] for e in sent] == ["visitor_approached", "visitor_approached", "home_pressed"]

    def boom(_): raise OSError("refused")
    b2 = Bridge("http://localhost:8765/device/event", sender=boom)
    assert not b2.on_home() and b2.failures == 1


def test_event_service_static_no_traversal(tmp_path):
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location(
        "les", pathlib.Path(__file__).resolve().parents[2] / "kiosk-agent" / "local_event_service.py")
    les = importlib.util.module_from_spec(spec); spec.loader.exec_module(les)
    ui = tmp_path / "ui"; ui.mkdir(); (ui / "index.html").write_text("ok")
    (tmp_path / "secret.env").write_text("x")
    root = ui.resolve()
    assert les.resolve_static(root, "/") == root / "index.html"
    assert les.resolve_static(root, "/index.html?x=1") == root / "index.html"
    assert les.resolve_static(root, "/../secret.env") is None
    assert les.resolve_static(root, "/missing.js") is None


def test_offline_cache_schema_runs_and_matches_readme():
    import pathlib, re, sqlite3
    root = pathlib.Path(__file__).resolve().parents[2]
    ddl = (root / "kiosk-agent" / "cache_schema.sql").read_text(encoding="utf-8")
    part = (root / "readme_src" / "03_embedded.md").read_text(encoding="utf-8")
    block = re.search(r"### 20\.4.*?```sql\n(.*?)```", part, re.S).group(1)
    assert block.strip() == ddl.strip()                      # README and file stay in sync
    db = sqlite3.connect(":memory:")
    db.executescript(ddl)
    db.execute("INSERT INTO cached_text VALUES ('WS001-P-b','WS-001','12','division of labourers')")
    assert db.execute("SELECT passage_id FROM cached_text WHERE cached_text MATCH 'labourers'").fetchall() == [("WS001-P-b",)]
