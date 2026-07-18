from __future__ import annotations

import json
from statistics import mean
from typing import Any

from .coverage import parse_hotlist
from .models import ImportRequest, ImportResult


MAX_IMPORT_BYTES = 25 * 1024 * 1024


def _json(content: str) -> Any:
    if len(content.encode("utf-8")) > MAX_IMPORT_BYTES:
        raise ValueError("import exceeds 25 MiB")
    return json.loads(content)


def parse_import(request: ImportRequest) -> ImportResult:
    if request.kind == "hotlist":
        layers = parse_hotlist(request.content)
        counts = [len(ids) for ids in layers.values()]
        return ImportResult(
            kind=request.kind,
            summary={
                "filename": request.filename,
                "layers": len(layers),
                "experts_per_layer_min": min(counts),
                "experts_per_layer_max": max(counts),
                "hotlist": layers,
            },
        )

    payload = _json(request.content)
    if request.kind == "profile":
        layers = payload.get("layers") if isinstance(payload, dict) else None
        if not isinstance(layers, dict) or not layers:
            raise ValueError("profile must contain a non-empty layers object")
        sanitized: dict[str, list[int]] = {}
        for layer, value in layers.items():
            counts = value.get("counts") if isinstance(value, dict) else None
            if not isinstance(counts, list) or not all(isinstance(item, int) and item >= 0 for item in counts):
                raise ValueError(f"layer {layer} has invalid counts")
            sanitized[str(int(layer))] = counts
        return ImportResult(
            kind=request.kind,
            summary={"filename": request.filename, "layers": len(sanitized), "counts": sanitized},
        )

    if request.kind == "server_timing":
        rows = payload if isinstance(payload, list) else [payload]
        values = []
        for row in rows:
            timings = row.get("timings", {}) if isinstance(row, dict) else {}
            value = timings.get("predicted_per_second")
            if isinstance(value, (int, float)) and value > 0:
                values.append(float(value))
        if not values:
            raise ValueError("no timings.predicted_per_second values found")
        return ImportResult(
            kind=request.kind,
            summary={"filename": request.filename, "decode_tps": mean(values), "repetitions": values},
        )

    if not isinstance(payload, list):
        raise ValueError("llama-bench import must be a JSON array")
    prefill = [float(row["avg_ts"]) for row in payload if row.get("n_prompt") and row.get("avg_ts")]
    decode = [float(row["avg_ts"]) for row in payload if row.get("n_gen") and row.get("avg_ts")]
    if not prefill and not decode:
        raise ValueError("no llama-bench avg_ts rows found")
    return ImportResult(
        kind=request.kind,
        summary={
            "filename": request.filename,
            "prefill_tps": mean(prefill) if prefill else None,
            "decode_tps": mean(decode) if decode else None,
            "prefill_rows": len(prefill),
            "decode_rows": len(decode),
        },
    )


def read_gguf_model(path: str) -> dict[str, Any]:
    """Read model metadata only when the optional gguf dependency is installed."""
    try:
        from gguf import GGUFReader
    except ImportError as exc:
        raise RuntimeError("GGUF inspection requires: pip install moe-autopilot-studio[gguf]") from exc
    reader = GGUFReader(path)
    return {
        "tensor_count": len(reader.tensors),
        "field_count": len(reader.fields),
        "path": path,
    }

