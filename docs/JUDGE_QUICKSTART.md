# Judge Quickstart

## Offline path

1. Extract the Windows ZIP into a clean folder.
2. Launch `MoEAutopilotStudio.exe` and wait for the browser.
3. The initial fixture produces a verdict immediately.
4. Change prompt/output tokens and press `Analyze workload`.
5. Inspect `Evidence` for source hashes and protocol IDs.
6. Export the analysis as JSON or self-contained HTML.

Expected time: under two minutes. Expected external requirements: none.

## Live GPT-5.6 path

1. Install Codex CLI and sign in with a ChatGPT account using `codex login`.
2. Restart Studio; the top-right control reports the App Server connection.
3. Press `Explain with GPT-5.6`.
4. Verify that the response selects the same experiment ID as the deterministic
   candidate matrix.

Studio does not receive or persist the OAuth token. It delegates account and
model access to the locally installed Codex CLI.

## Expected fixture checks

- Session-transfer canonical coverage: `68.56%`.
- Same-protocol decode gain: `+22.22%`.
- Prefill change at HOT_N=96: `-9.90%`.
- Derived break-even: approximately `19.18 : 1` prompt/output.
- A 16,000 / 300 prompt-heavy workload: `DISABLE` for total latency.
- Legacy build arms: `MEASURE` with `protocol-mismatch`.

## Local runner path

This optional path requires a compatible llama.cpp fork, a GGUF model, and a
session hot-list. The `Runs` view queues baseline followed by split, captures
argv/env and outputs, and can cancel only the process it started.
