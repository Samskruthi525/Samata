"""Evaluation metrics (design doc §12.2). Never merged into one 'AI accuracy' number."""
from __future__ import annotations


def levenshtein(a, b) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def cer(hyp: str, ref: str) -> float:
    return levenshtein(hyp, ref) / max(len(ref), 1)


def wer(hyp: str, ref: str) -> float:
    r = ref.split()
    return levenshtein(hyp.split(), r) / max(len(r), 1)


def precision_at_k(ranked: list[str], relevant: set[str], k: int = 5) -> float:
    return sum(1 for x in ranked[:k] if x in relevant) / k


def hit_at_k(ranked: list[str], relevant: set[str], k: int = 5) -> float:
    return float(any(x in relevant for x in ranked[:k]))


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for i, x in enumerate(ranked, 1):
        if x in relevant:
            return 1.0 / i
    return 0.0


def citation_validity(citations: list[dict], resolvable: set[str]) -> float:
    if not citations:
        return float("nan")
    return sum(1 for c in citations if c["excerpt_id"] in resolvable) / len(citations)
