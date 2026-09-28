"""Hybrid retrieval reference: lexical BM25 + dense stand-in, fused with RRF.

The rights filter is applied BEFORE either index is queried, so an ineligible
passage can never be ranked, logged as a candidate, or passed to a model.

The "dense" scorer here is a character-trigram cosine similarity: a
deterministic, dependency-free stand-in for an embedding model so the fusion
logic can be unit-tested. It is NOT semantic search; production uses
pgvector with a chosen embedding model (dimension TBD).
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from .corpus import Item, Passage
from .rights import Action

ALIASES = {  # approved alias expansion (curator-maintained table in production)
    "babasaheb": "ambedkar", "b. r. ambedkar": "ambedkar", "dr. ambedkar": "ambedkar",
    "bhimrao": "ambedkar", "yerwada": "poona pact",
}
STOP = set("the a an of and or in on at to is was what did about who when where how tell me for by with his her it this that from as be".split())


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    for k, v in ALIASES.items():
        text = text.replace(k, v)
    return text


def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[\w]+", normalise(text)) if t not in STOP]


@dataclass(frozen=True)
class Hit:
    passage: Passage
    score: float
    lexical_rank: int | None
    dense_rank: int | None


class HybridIndex:
    def __init__(self, items: dict[str, Item], action: Action = Action.SEARCH_INDEX, k1=1.4, b=0.75):
        self.items = items
        # --- rights gate first ---
        self.passages = [p for it in items.values() if it.allowed(action) for p in it.passages]
        self.docs = [tokens(p.text + " " + items[p.item_id].title) for p in self.passages]
        self.N = len(self.docs)
        self.avgdl = sum(map(len, self.docs)) / max(self.N, 1)
        self.df = Counter(t for d in self.docs for t in set(d))
        self.k1, self.b = k1, b
        self.tri = [self._trigrams(p.text + " " + items[p.item_id].title) for p in self.passages]

    @staticmethod
    def _trigrams(text: str) -> Counter:
        s = f"  {normalise(text)}  "
        return Counter(s[i:i + 3] for i in range(len(s) - 2))

    def bm25(self, q: list[str]) -> list[tuple[int, float]]:
        out = []
        for i, d in enumerate(self.docs):
            tf = Counter(d)
            s = 0.0
            for t in q:
                if t not in tf:
                    continue
                idf = math.log(1 + (self.N - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * tf[t] * (self.k1 + 1) / (tf[t] + self.k1 * (1 - self.b + self.b * len(d) / self.avgdl))
            if s > 0:
                out.append((i, s))
        return sorted(out, key=lambda x: -x[1])

    def dense(self, query: str) -> list[tuple[int, float]]:
        qv = self._trigrams(query)
        qn = math.sqrt(sum(v * v for v in qv.values()))
        out = []
        for i, dv in enumerate(self.tri):
            dot = sum(qv[k] * dv.get(k, 0) for k in qv)
            dn = math.sqrt(sum(v * v for v in dv.values()))
            if dot:
                out.append((i, dot / (qn * dn)))
        return sorted(out, key=lambda x: -x[1])

    def search(self, query: str, k: int = 5, rrf_k: int = 60, min_dense: float = 0.12) -> list[Hit]:
        lex = self.bm25(tokens(query))
        den = [(i, s) for i, s in self.dense(query) if s >= min_dense]
        lr = {i: r for r, (i, _) in enumerate(lex)}
        dr = {i: r for r, (i, _) in enumerate(den)}
        fused = {}
        for i in set(lr) | set(dr):
            fused[i] = sum(1.0 / (rrf_k + r + 1) for r in (lr.get(i), dr.get(i)) if r is not None)
            # reviewed passages are preferred (design doc §9.1)
            if self.passages[i].reviewed:
                fused[i] *= 1.05
        ranked = sorted(fused.items(), key=lambda x: -x[1])[:k]
        return [Hit(self.passages[i], s, lr.get(i), dr.get(i)) for i, s in ranked]
