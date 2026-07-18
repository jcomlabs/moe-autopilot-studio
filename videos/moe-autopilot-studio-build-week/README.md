# Build Week demo source

This directory contains the reproducible source for the 109-second English
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
instance at `http://127.0.0.1:18770`. Generated renders, snapshots, raw capture,
tool instructions, and `node_modules` are intentionally ignored by Git.

## Provenance

- Product captures: MoE Autopilot Studio 0.1.2, fixture and live advisor paths.
- Narration: Kokoro `af_heart`, generated locally from `SCRIPT.md`.
- Captions: derived from the locked script because a word-level Whisper runtime
  was unavailable; the derivation is recorded in `audio_meta.json`.
- Visual composition: authored during Build Week with HyperFrames 0.7.64.
- Music: none.

The normalized master is published separately as a release asset:

- Name: `MoE-Autopilot-Studio-Build-Week-demo.mp4`
- SHA-256: `52d8a1cedb4a2e9111e21056ea526c57fbd5063bc27713b3329086941a6a89b7`
