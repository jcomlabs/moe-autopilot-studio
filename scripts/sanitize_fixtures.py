"""Build public, prompt-free fixtures from the private local evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean
from typing import Any


SOURCE_COMMIT = "e1170152ed074a062c235ee685af08fd3dde6dec"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def provenance(paths: list[Path]) -> dict[str, Any]:
    return {
        "source_repository": "JigSawPT/moe-autopilot",
        "source_commit": SOURCE_COMMIT,
        "transformation": "Prompt text and local paths removed; only activation counts, expert ids, protocol metadata, and timings retained.",
        "source_artifacts": [
            {"name": path.name, "sha256": sha256(path)} for path in paths
        ],
    }


def server_tps(path: Path) -> float:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return float(payload["timings"]["predicted_per_second"])


def bench_metric(path: Path, metric: str) -> float:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if metric == "prefill":
        values = [float(row["avg_ts"]) for row in rows if int(row.get("n_prompt", 0)) > 0]
    else:
        values = [float(row["avg_ts"]) for row in rows if int(row.get("n_gen", 0)) > 0]
    if not values:
        raise ValueError(f"{path.name} has no {metric} rows")
    return mean(values)


def profile(path: Path, hotlist_path: Path, hot_n: int, expected: float) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))["layers"]
    counts = {str(layer): value["counts"] for layer, value in raw.items()}
    hotlist: dict[str, list[int]] = {}
    for line in hotlist_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            hotlist[str(int(parts[0]))] = [int(value) for value in parts[1 : hot_n + 1]]
    return {
        "layers": counts,
        "hotlist": hotlist,
        "hot_n": hot_n,
        "expected_coverage": expected,
    }


def protocol(instrument: str, model_id: str, build_id: str, flags: dict[str, Any]) -> dict[str, Any]:
    return {"instrument": instrument, "model_id": model_id, "build_id": build_id, "flags": flags}


def run(
    run_id: str,
    label: str,
    role: str,
    proto: dict[str, Any],
    decode: float | None,
    prefill: float | None,
    coverage: float | None,
    hot_n: int | None,
    ncmoe: int,
    vram: float,
    ram: float,
    hashes: list[str],
    repetitions: list[float] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": run_id,
        "label": label,
        "role": role,
        "protocol": proto,
        "evidence": "measured",
        "decode_tps": decode,
        "prefill_tps": prefill,
        "coverage": coverage,
        "hot_n": hot_n,
        "n_cpu_moe": ncmoe,
        "model_vram_gb": vram,
        "ram_required_gb": ram,
        "repetitions": repetitions or [],
        "source_hashes": hashes,
        "notes": notes or [],
    }


def write_fixture(output: Path, payload: dict[str, Any]) -> None:
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    profiles = root / "autopilot" / "profiles"
    evidence = root / "evidence" / "v2"

    hardware = {
        "name": "RTX 5090 / Ryzen 9950X3D / Windows 11",
        "vram_total_gb": 32.0,
        "vram_baseline_gb": 1.0,
        "vram_reserve_gb": 0.5,
        "ram_budget_gb": 48.0,
        "ram_bandwidth_gbps": 42.0,
        "vram_bandwidth_gbps": 1050.0,
    }
    coder = {
        "id": "qwen3-coder-next-mxfp4",
        "name": "Qwen3-Coder-Next MXFP4 MoE",
        "architecture": "qwen3next",
        "layers": 48,
        "expert_count": 512,
        "experts_used": 10,
        "activation_family": "gated-swiglu",
        "notes": ["Measured on one Windows workstation; recalibrate elsewhere."],
    }

    v22 = evidence / "v22_impl"
    base_paths = [v22 / "S0a_nosplit_run1.json", v22 / "S0a_nosplit_run2.json"]
    generic_paths = [evidence / "v2_hot96_1.json", evidence / "v2_hot96_2.json"]
    session_paths = [v22 / "S0_ref_hot96_run1.json", v22 / "S0_ref_hot96_run2.json"]
    ceiling_paths = [evidence / "v2c_live_1.json", evidence / "v2c_live_2.json"]
    live_profile = profiles / "live_profile.json"
    session_hotlist = profiles / "session.hotlist"
    all_decode = base_paths + generic_paths + session_paths + ceiling_paths + [live_profile, session_hotlist]
    decode_proto = protocol(
        "llama-server/timings.predicted_per_second",
        coder["id"],
        "1e6630df2",
        {"n_cpu_moe": 24, "poll": 100, "temperature": 0, "max_tokens": 400, "no_mmap": True, "threads": 16},
    )
    legacy_proto = protocol(
        "llama-server/timings.predicted_per_second",
        coder["id"],
        "12d1037ef",
        {"n_cpu_moe": 24, "temperature": 0, "max_tokens": 400, "no_mmap": True, "threads": 16},
    )
    values = {group: [server_tps(path) for path in paths] for group, paths in {
        "base": base_paths, "generic": generic_paths, "session": session_paths, "ceiling": ceiling_paths
    }.items()}
    write_fixture(out / "coder-next-decode.json", {
        "id": "coder-next-decode",
        "name": "Coder-Next: session transfer",
        "summary": "Task-disjoint session history raises coverage and decode throughput; circular data is shown only as a ceiling.",
        "model": coder,
        "hardware": hardware,
        "default_workload": {"description": "Generation-heavy coding assistant", "prompt_tokens": 500, "output_tokens": 300, "objective": "decode_throughput"},
        "runs": [
            run("baseline", "No split", "baseline", decode_proto, mean(values["base"]), None, 0.0, None, 24, 25.0, 45.0, [sha256(p) for p in base_paths], values["base"]),
            run("generic", "Generic corpus (legacy protocol)", "candidate", legacy_proto, mean(values["generic"]), None, 0.335, 96, 24, 29.2, 45.0, [sha256(p) for p in generic_paths], values["generic"], ["Retained for context; ProtocolFingerprint intentionally blocks comparison with the V2.2 baseline."]),
            run("session", "Session history", "candidate", decode_proto, mean(values["session"]), None, 0.686, 96, 24, 29.2, 45.0, [sha256(p) for p in session_paths], values["session"], ["Non-circular: three prior tasks, evaluated on an unseen task."]),
            run("ceiling", "Same-task ceiling (legacy protocol)", "candidate", legacy_proto, mean(values["ceiling"]), None, 0.804, 96, 24, 29.2, 45.0, [sha256(p) for p in ceiling_paths], values["ceiling"], ["Circular ceiling; not a deployable recommendation."]),
        ],
        "activation_profile": profile(live_profile, session_hotlist, 96, 0.686),
        "limitations": [
            "Decode-only protocol.",
            "The protocol-compatible session arm measures +22.2%; the earlier +19.3% headline mixed build fingerprints and is not reproduced here.",
            "Legacy generic and same-task arms remain visible but cannot be compared with the V2.2 baseline.",
            "The same-task arm is circular and must not be selected as the recommended production configuration.",
        ],
        "provenance": provenance(all_decode),
    })

    prefill_a = [evidence / "prefill_ab_A.json", evidence / "prefill_ab_A2.json"]
    prefill_b = [evidence / "prefill_ab_B.json", evidence / "prefill_ab_B2.json"]
    prefill_c = [evidence / "prefill_ab_C_hotn0.json"]
    e2e_proto = protocol(
        "llama-bench/pp2048+tg128",
        coder["id"],
        "ab2fbb7a6",
        {"n_cpu_moe": 24, "batch": 2048, "ubatch": 2048, "repetitions": 2, "flash_attn": True, "no_mmap": True, "threads": 16},
    )
    def bench_values(paths: list[Path], metric: str) -> list[float]:
        return [bench_metric(path, metric) for path in paths]
    write_fixture(out / "coder-next-e2e.json", {
        "id": "coder-next-e2e",
        "name": "Coder-Next: prefill versus decode",
        "summary": "The resident hot copies help decode but regress prefill; workload shape decides the total-latency verdict.",
        "model": coder,
        "hardware": hardware,
        "default_workload": {"description": "Interactive chat", "prompt_tokens": 500, "output_tokens": 300, "objective": "total_latency"},
        "runs": [
            run("baseline", "No split", "baseline", e2e_proto, mean(bench_values(prefill_a, "decode")), mean(bench_values(prefill_a, "prefill")), 0.0, None, 24, 25.0, 45.0, [sha256(p) for p in prefill_a], bench_values(prefill_a, "decode")),
            run("hot96", "Session HOT_N=96", "candidate", e2e_proto, mean(bench_values(prefill_b, "decode")), mean(bench_values(prefill_b, "prefill")), 0.686, 96, 24, 29.45, 45.0, [sha256(p) for p in prefill_b], bench_values(prefill_b, "decode")),
            run("hot0", "Parsed, no hot copies", "control", e2e_proto, None, bench_metric(prefill_c[0], "prefill"), 0.0, 0, 24, 25.0, 45.0, [sha256(prefill_c[0])]),
        ],
        "activation_profile": profile(live_profile, session_hotlist, 96, 0.686),
        "limitations": [
            "Prefill penalty was measured only at HOT_N=96; the Studio does not extrapolate it to other sizes.",
            "The historical write-up says break-even prompt:output is about 2.3, but its own measured arms and scenario deltas recompute to about 19.2; the Studio uses the measured values.",
        ],
        "provenance": provenance(prefill_a + prefill_b + prefill_c + [live_profile, session_hotlist]),
    })

    qmodel = {
        "id": "qwen3.6-35b-a3b-q4",
        "name": "Qwen3.6-35B-A3B Q4_K_M",
        "architecture": "qwen3moe",
        "layers": 40,
        "expert_count": 256,
        "experts_used": 8,
        "activation_family": "gated-swiglu",
        "notes": ["Second-architecture direction check."],
    }
    qbase = [evidence / "q35_base_1.json", evidence / "q35_base_2.json"]
    qsplit = [evidence / "q35_split_1.json", evidence / "q35_split_2.json"]
    qprofile = profiles / "q35_live.json"
    qhot = profiles / "q35_session.hotlist"
    qproto = protocol("llama-server/timings.predicted_per_second", qmodel["id"], "73d5d804f", {"n_cpu_moe": 16, "temperature": 0, "no_mmap": True, "threads": 16})
    qbase_values = [server_tps(path) for path in qbase]
    qsplit_values = [server_tps(path) for path in qsplit]
    write_fixture(out / "qwen35-decode.json", {
        "id": "qwen35-decode",
        "name": "Qwen3.6-35B: architecture check",
        "summary": "A smaller 256-expert architecture shows the same direction with a smaller relative gain.",
        "model": qmodel,
        "hardware": hardware,
        "default_workload": {"description": "Local generation", "prompt_tokens": 500, "output_tokens": 300, "objective": "decode_throughput"},
        "runs": [
            run("baseline", "No split", "baseline", qproto, mean(qbase_values), None, 0.0, None, 16, 15.0, 20.0, [sha256(p) for p in qbase], qbase_values),
            run("session", "Session HOT_N=48", "candidate", qproto, mean(qsplit_values), None, 0.642, 48, 16, 17.0, 20.0, [sha256(p) for p in qsplit], qsplit_values),
        ],
        "activation_profile": profile(qprofile, qhot, 48, 0.642),
        "limitations": ["Decode-only protocol.", "Forced CPU expert offload; not the all-GPU optimum."],
        "provenance": provenance(qbase + qsplit + [qprofile, qhot]),
    })

    gdoc = evidence / "gptoss_maxabs.md"
    gmodel = {
        "id": "gpt-oss-120b-mxfp4",
        "name": "gpt-oss-120B MXFP4",
        "architecture": "gpt-oss",
        "layers": 36,
        "expert_count": 128,
        "experts_used": 4,
        "activation_family": "swiglu_oai",
        "notes": ["Routing-flatness counterexample: coverage alone is not sufficient."],
    }
    gproto = protocol("llama-server/timings.predicted_per_second", gmodel["id"], "aipc-hardening", {"n_cpu_moe": 25, "hot_n": 22, "held_out": True, "no_mmap": True, "poll": 100})
    write_fixture(out / "gptoss-adaptive.json", {
        "id": "gptoss-adaptive",
        "name": "gpt-oss: coverage is not enough",
        "summary": "Session history adds 17.1 coverage points but only 2.3% over the corpus arm, exposing routing flatness.",
        "model": gmodel,
        "hardware": hardware,
        "default_workload": {"description": "Held-out systems coding prompt", "prompt_tokens": 500, "output_tokens": 300, "objective": "decode_throughput"},
        "runs": [
            run("baseline", "No split", "baseline", gproto, 38.03, None, 0.0, None, 25, 21.4, 45.0, [sha256(gdoc)]),
            run("corpus", "Generic corpus", "candidate", gproto, 40.90, None, 0.280, 22, 25, 29.63, 45.0, [sha256(gdoc)]),
            run("session", "Session history", "candidate", gproto, 41.85, None, 0.451, 22, 25, 29.63, 45.0, [sha256(gdoc)], notes=["The coverage increase mostly reaches low-traffic tail experts."]),
        ],
        "activation_profile": None,
        "limitations": ["Values are sanitized from the measured write-up.", "Coverage is not a universal speed proxy on flat-routing models."],
        "provenance": provenance([gdoc]),
    })

    manifest = {
        "schema_version": 1,
        "source_commit": SOURCE_COMMIT,
        "fixtures": [path.name for path in sorted(out.glob("*.json")) if path.name != "manifest.json"],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
