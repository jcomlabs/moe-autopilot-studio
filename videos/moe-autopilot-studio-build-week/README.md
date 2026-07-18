# Build Week demo source

This directory contains the reproducible source for the 113-second English
MoE Autopilot Studio demonstration. It uses real captures from the packaged
Windows application, deterministic HTML compositions, generated narration,
and checked-in caption timings. It contains no music, prompt history,
credentials, private model files, or clinical data.

## Rebuild

Requirements: Node.js 22+, FFmpeg, and HyperFrames 0.7.64.

```powershell
npm ci
npm run build:video
npm run check
npm run render
```

`npm run capture:studio` refreshes application screenshots from a Studio
instance at `http://127.0.0.1:18771`. Generated renders, snapshots, raw capture,
tool instructions, and `node_modules` are intentionally ignored by Git.

## Provenance

- Product captures: MoE Autopilot Studio 0.2.0 fixture paths. The council image
  is a credential-free capture replay of the separately validated live 3/3 run.
- Narration: Kokoro `af_heart`, generated locally from `SCRIPT.md`.
- Captions: derived from the locked script because a word-level Whisper runtime
  was unavailable; the derivation is recorded in `audio_meta.json`.
- Visual composition: authored during Build Week with HyperFrames 0.7.64.
- Music: none.

The final master was rendered and validated locally. It is intended for a
separate release asset after owner review:

- Name: `moe-autopilot-studio-build-week-v2.mp4`
- SHA-256: `566db2cc4ab9607f7e58dbac7208306c6cbe12a8c8a4522fd84896543aad07e3`
