"""Load the demo corpus exported from the HTML prototype into typed records."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .rights import RightsPolicy, ReviewStatus, Action, permitted

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "demo_corpus.json"


@dataclass(frozen=True)
class Passage:
    id: str
    item_id: str
    page_index: int | None          # pdf_page_index (0-based) for documents
    printed_page: str | None        # printed label; NOT the same as the PDF index
    text: str
    reviewed: bool = True
    start_ms: int | None = None     # for media transcript segments
    end_ms: int | None = None


@dataclass
class Item:
    id: str
    kind: str
    title: str
    rights: RightsPolicy
    status: ReviewStatus
    cached: bool
    year: int | None
    language: str | None
    source_ref: str | None
    passages: list[Passage] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    def allowed(self, action: Action) -> bool:
        return permitted(self.rights, self.status, action)


def _status(raw: str | None) -> ReviewStatus:
    """Prototype items without a status are published; any unrecognised value
    (e.g. the HTML uses status 'permission_pending' for AV-003) fails closed to DRAFT."""
    if raw is None:
        return ReviewStatus.PUBLISHED
    try:
        return ReviewStatus(raw)
    except ValueError:
        return ReviewStatus.DRAFT


def load(path: str | Path = DEFAULT_PATH) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items: dict[str, Item] = {}
    for r in data["items"]:
        # The prototype marks every cleared demo item as AI/offline eligible only if cached;
        # this is a DEMO assumption and must come from the rights register in production.
        pol = RightsPolicy.from_state(r["rights"], ai_processing_allowed=True,
                                      offline_cache_allowed=bool(r.get("cached")))
        it = Item(id=r["id"], kind=r["kind"], title=r["title"], rights=pol,
                  status=_status(r.get("status")), cached=bool(r.get("cached")),
                  year=r.get("year"), language=r.get("language"), source_ref=r.get("sourceRef"), raw=r)
        for pg in r.get("pages", []):
            for p in pg.get("passages", []):
                it.passages.append(Passage(p["id"], it.id, pg.get("pdf"), pg.get("printed"), p["text"]))
        for i, seg in enumerate(r.get("segments", [])):
            it.passages.append(Passage(f"{it.id}-T{i:02d}", it.id, None, None, seg["text"],
                                       start_ms=seg["ms"], end_ms=seg["ms"] + seg.get("dur", 0)))
        items[it.id] = it
    data["typed_items"] = items
    return data
