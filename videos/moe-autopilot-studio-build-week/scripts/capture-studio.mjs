import { mkdir, rename } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const assets = path.join(root, "capture", "assets");
const rawVideo = path.join(root, "capture", "raw-video");
const baseUrl = process.env.STUDIO_URL ?? "http://127.0.0.1:18770/";
const chrome = process.env.CHROME_PATH ??
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

await mkdir(assets, { recursive: true });
await mkdir(rawVideo, { recursive: true });

const browser = await chromium.launch({ executablePath: chrome, headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  recordVideo: { dir: rawVideo, size: { width: 1440, height: 900 } },
});
const page = await context.newPage();
const video = page.video();

const members = [
  { provider: "xiaomi", label: "Xiaomi MiMo", model: "mimo-v2.5", status: "accepted", latency_ms: 5800, recommendation_id: "hot96", rationale: "Use the deterministic recommendation and retain protocol safeguards." },
  { provider: "deepseek", label: "DeepSeek", model: "deepseek-v4-flash", status: "accepted", latency_ms: 6200, recommendation_id: "hot96", rationale: "Keep the measured candidate and preserve the protocol fingerprint." },
  { provider: "chatgpt", label: "ChatGPT lead", model: "gpt-5.6-sol", status: "accepted", latency_ms: 15200, recommendation_id: "hot96", rationale: "The council confirms the measured recommendation; the deterministic engine remains authoritative." },
];
await page.route("**/api/advisors/status*", (route) => route.fulfill({
  contentType: "application/json",
  body: JSON.stringify({
    mode: "moa",
    strategy: "parallel scouts, ChatGPT synthesis, deterministic validation",
    providers: [
      { id: "chatgpt", label: "ChatGPT", configured: true, available: true, model: "gpt-5.6-sol", auth: "oauth" },
      { id: "xiaomi", label: "Xiaomi MiMo", configured: true, available: true, model: "mimo-v2.5", auth: "environment", latency_ms: 5800 },
      { id: "deepseek", label: "DeepSeek", configured: true, available: true, model: "deepseek-v4-flash", auth: "environment", latency_ms: 6200 },
    ],
  }),
}));
await page.route("**/api/advisor", (route) => route.fulfill({
  contentType: "application/json",
  body: JSON.stringify({
    recommendation_id: "hot96",
    rationale: "Three independent reviews agree with the measured recommendation. The deterministic engine remains authoritative.",
    risk_flags: ["Keep the protocol fingerprint matched."],
    assumptions: [],
    backend: "moa",
    model: "gpt-5.6-sol council",
    members,
    quorum: 3,
  }),
}));

async function settle() {
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(700);
}

async function shot(name) {
  await page.screenshot({
    path: path.join(assets, name),
    fullPage: false,
  });
}

await page.goto(baseUrl);
await settle();
await page.getByRole("heading", { name: "Enable this configuration" }).waitFor();
await shot("studio-enable.png");

await page.getByRole("spinbutton", { name: "Prompt tokens" }).fill("16000");
await page.getByRole("button", { name: "Analyze workload" }).click();
await page.getByRole("heading", { name: "Leave the split disabled" }).waitFor();
await page.waitForTimeout(900);
await shot("studio-disable.png");

await page.getByRole("button", { name: "Evidence", exact: true }).click();
await page.getByRole("heading", { name: "Coder-Next: prefill versus decode" }).waitFor();
await page.waitForTimeout(700);
await shot("studio-evidence.png");

await page.getByRole("button", { name: "Runs", exact: true }).click();
await page.getByRole("heading", { name: "Baseline → split A/B" }).waitFor();
await page.waitForTimeout(700);
await shot("studio-runs.png");

await page.getByRole("button", { name: "Studio", exact: true }).click();
await page.getByRole("spinbutton", { name: "Prompt tokens" }).fill("500");
await page.getByRole("button", { name: "Analyze workload" }).click();
await page.getByRole("button", { name: "Consult council" }).click();
await page.getByText("ChatGPT lead", { exact: true }).waitFor({ timeout: 60_000 });
await page.waitForTimeout(900);
await shot("studio-advisor.png");

await context.close();
const recordedPath = await video.path();
await browser.close();
await rename(recordedPath, path.join(rawVideo, "studio-workflow.webm"));

console.log(`Captured Studio at ${baseUrl}`);
