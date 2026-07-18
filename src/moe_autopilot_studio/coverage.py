from __future__ import annotations

from .models import ActivationProfile


def canonical_coverage(profile: ActivationProfile, hot_n: int | None = None) -> float:
    """Mean of per-layer covered-hit fractions, matching the historical CLI."""
    n = hot_n or profile.hot_n
    layer_coverages: list[float] = []
    for layer_id in sorted(profile.layers, key=int):
        counts = profile.layers[layer_id]
        hot = set(profile.hotlist.get(layer_id, [])[:n])
        total = sum(counts)
        covered = sum(count for expert, count in enumerate(counts) if expert in hot)
        layer_coverages.append(covered / total if total else 0.0)
    if not layer_coverages:
        raise ValueError("profile has no layers")
    return sum(layer_coverages) / len(layer_coverages)


def parse_hotlist(text: str) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"invalid hot-list line {line_number}")
        layer = str(int(parts[0]))
        ids = [int(value) for value in parts[1:]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate expert id on line {line_number}")
        result[layer] = ids
    if not result:
        raise ValueError("hot-list is empty")
    return result
