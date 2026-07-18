# Build Week Submission Draft

## Project

**Name:** MoE Autopilot Studio

**Tagline:** A Windows lab that turns measured MoE routing evidence into a
reproducible ENABLE, DISABLE, or MEASURE decision.

**Public demo:** https://jcomlabs.github.io/moe-autopilot-studio/

**Repository:** https://github.com/jcomlabs/moe-autopilot-studio

**Windows release:** https://github.com/jcomlabs/moe-autopilot-studio/releases/latest

## Problem

Local MoE inference has a workload-dependent placement problem. Keeping hot
experts resident can improve generation, regress prompt processing, exceed the
WDDM VRAM margin, or look faster only because two incompatible builds were
compared. Existing benchmark files do not answer the operational question:
should this workload enable the split, with which measured configuration, and
what experiment should run next?

## Solution

MoE Autopilot Studio loads sanitized measurements, computes canonical coverage,
checks immutable protocol fingerprints and hardware budgets, and produces a
deterministic verdict. It exposes coverage, decode, prefill, total latency,
break-even, RAM, and VRAM in one working interface. A safe local runner launches
only known llama.cpp tools as argv arrays, records the exact environment and
outputs, and persists results locally.

The offline fixture path works in under two minutes without Python, a model, a
GPU, or an account. The Windows release adds custom imports and measured A/B
runs.

## OpenAI integration

The optional explanation layer uses Codex App Server over stdio and ChatGPT
OAuth. Each analysis starts an ephemeral GPT-5.6 Sol thread in an empty
read-only directory with approvals disabled. The model receives only user intent
and a bounded deterministic report. It may select only an experiment ID emitted
by the engine, cannot change the verdict, and is rejected if it introduces an
unsupported number. `codex exec --ephemeral` is the compatible fallback; the
entire lab remains useful offline.

## Build Week boundary

Before Build Week, the separate `moe-autopilot` research repository had a
load-time hot/cold llama.cpp fork, profiler, hot-list format, coverage convention,
and workstation measurements. During Build Week, this new repository added the
typed engine, protocol guard, evidence model, Windows Studio, safe runner,
imports, exports, Codex App Server bridge, offline mode, sanitized public
fixtures, tests, CI, packaging, and hosted fixture report.

The submission does not claim a new cache algorithm, V3, dynamic caching,
training, or DeltaMoE. Exact immutable provenance is in `NOTICE` and
`BUILD_WEEK.md`.

## Evidence and honesty

The protocol-compatible Coder-Next fixture measures 68.56% coverage and +22.22%
decode throughput. The end-to-end fixture measures -9.90% prefill and derives a
19.18 prompt/output break-even. Studio explicitly rejects older arms whose build
fingerprints differ, rather than reproducing a historical +19.3% headline across
incompatible builds.

A fresh Build Week runner smoke on Qwen3.6-35B completed both arms on the pinned
fork: 96.65 versus 101.98 tok/s (+5.51%). It is retained in local run history and
is not promoted over the public fixture after only two repetitions.

## Judge walkthrough

1. Open the Pages report or Windows release.
2. Compare interactive chat with the 16,000/300 prompt-heavy scenario.
3. Observe the verdict change from ENABLE to DISABLE.
4. Open session transfer and inspect the blocked legacy protocol rows.
5. In the Windows app, connect ChatGPT and ask GPT-5.6 Sol to explain the selected
   experiment ID.
6. Export the deterministic report or inspect the local Runs history.

## Remaining submission actions

- Record the public video using `docs/VIDEO_SCRIPT.md`; keep it below three
  minutes and show the same live GPT-5.6 explanation as the app.
- Add the final public video URL to the form and this document.
- Verify the release SHA-256 and both public links from a signed-out browser.
- Submit before the Devpost deadline; do not add post-deadline commits to the
  submitted revision.
