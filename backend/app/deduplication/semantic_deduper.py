"""Semantic similarity deduplication via embeddings."""

from __future__ import annotations

from typing import Sequence


class SemanticDeduper:
    """Compare embedding vectors; threshold configurable per category."""

    def __init__(self, threshold: float = 0.92) -> None:
        self.threshold = threshold

    def is_duplicate(
        self, vec_a: Sequence[float], vec_b: Sequence[float]
    ) -> tuple[bool, float]:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return False, 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return False, 0.0
        sim = dot / (norm_a * norm_b)
        return sim >= self.threshold, sim
