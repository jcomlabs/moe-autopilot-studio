import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const metaPath = path.join(root, "audio_meta.json");
const meta = JSON.parse(await readFile(metaPath, "utf8"));

for (const voice of meta.voices) {
  const number = String(voice.frame).padStart(2, "0");
  const text = (await readFile(path.join(root, "assets", "voice", `${number}.txt`), "utf8")).trim();
  const tokens = text.match(/\S+/g) ?? [];
  const weights = tokens.map((token) => {
    const letters = token.replace(/[^A-Za-z0-9.-]/g, "").length;
    const pause = /[.!?]$/.test(token) ? 1.25 : /[,;:]$/.test(token) ? 0.55 : 0;
    return 0.78 + Math.min(letters, 14) * 0.035 + pause;
  });
  const usable = Math.max(voice.duration_s - 0.18, voice.duration_s * 0.96);
  const scale = usable / weights.reduce((sum, value) => sum + value, 0);
  let cursor = 0.08;
  voice.words = tokens.map((token, index) => {
    const start = cursor;
    const span = weights[index] * scale;
    const end = Math.min(voice.duration_s, start + span * 0.82);
    cursor += span;
    return { text: token, start: Number(start.toFixed(3)), end: Number(end.toFixed(3)) };
  });
  voice.word_timing_source = "estimated_from_locked_script";
}

await writeFile(metaPath, `${JSON.stringify(meta, null, 2)}\n`, "utf8");
console.log(`Estimated caption timing for ${meta.voices.length} narration lines.`);
