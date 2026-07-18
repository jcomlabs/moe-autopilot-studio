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
await page.getByRole("button", { name: "Explain with GPT-5.6" }).click();
await page.getByText("For this 500-token prompt", { exact: false }).waitFor({ timeout: 60_000 });
await page.waitForTimeout(900);
await shot("studio-advisor.png");

await context.close();
const recordedPath = await video.path();
await browser.close();
await rename(recordedPath, path.join(rawVideo, "studio-workflow.webm"));

console.log(`Captured Studio at ${baseUrl}`);
