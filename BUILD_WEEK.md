# Build Week boundary

## Before July 13, 2026

The source project had already demonstrated a static, load-time hot/cold expert
split for llama.cpp, an offline profiler, a hot-list format, a canonical coverage
calculation, and measured performance results on one Windows workstation.

Source of record: `JigSawPT/moe-autopilot@e1170152ed074a062c235ee685af08fd3dde6dec`.

## Built for OpenAI Build Week

MoE Autopilot Studio is a separate product and repository. Its new work includes:

- a typed deterministic analysis engine and protocol compatibility guard;
- a local FastAPI service and React Studio;
- evidence grades and workload-level ENABLE / DISABLE / MEASURE verdicts;
- secure argv-based experiment execution and reproducible exports;
- ChatGPT OAuth and GPT-5.6 Sol through Codex App Server;
- fixture-only offline and hosted judge modes;
- automated tests, Windows packaging, and public demo infrastructure.

The Build Week work does not claim a new cache algorithm or new benchmark result.
It turns pre-existing research evidence into a testable developer tool.

