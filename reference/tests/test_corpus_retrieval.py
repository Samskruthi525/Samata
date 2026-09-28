import pytest
from heritage_core import corpus
from heritage_core.retrieval import HybridIndex, normalise, tokens
from heritage_core.rights import Action


@pytest.fixture(scope="module")
def data():
    return corpus.load()


def test_demo_corpus_counts(data):
    items = data["typed_items"]
    assert len(items) == 14
    assert {i.kind for i in items.values()} == {"writing", "constitutional", "manuscript_photo", "media"}
    assert len(data["events"]) == 14 and len(data["tests"]) == 16


def test_printed_page_differs_from_pdf_index(data):
    p = next(p for p in data["typed_items"]["CR-001"].passages if p.id == "CR001-P-b")
    assert p.printed_page == "978" and p.page_index == 6


def test_pending_and_link_only_not_indexed(data):
    idx = HybridIndex(data["typed_items"])
    ids = {p.item_id for p in idx.passages}
    assert "AV-003" not in ids   # permission_pending
    assert "MP-003" not in ids   # link_only


def test_alias_expansion():
    assert "ambedkar" in normalise("Babasaheb")
    assert "the" not in tokens("the Poona Pact")


def test_known_query_top5(data):
    idx = HybridIndex(data["typed_items"])
    hits = idx.search("constitutional morality")
    assert "CR001-P-b" in [h.passage.id for h in hits]


def test_media_passages_carry_timestamps(data):
    segs = [p for p in data["typed_items"]["AV-001"].passages]
    assert segs and all(p.start_ms is not None and p.end_ms > p.start_ms for p in segs)
