---
format: 1920x1080
message: "The fastest decode setting is not always the fastest workload"
arc: "Demo Loop: question -> decision -> decision flip -> trust -> execution -> boundary -> CTA"
audience: "OpenAI Build Week judges, local-inference researchers, and Windows AI builders"
mode: autonomous
music: none
---

## Frame 1 - The wrong question

- scene: A decode-speed claim is physically replaced by the workload-level question.
- voiceover: "Faster decode can make the whole workload slower. The setting is not the decision. The workload is."
- duration: 5.931s
- poster: 7s
- transition_in: cut
- status: animated
- src: compositions/frames/01-wrong-question.html
- type: hook
- persuasion: Contrarian reframing
- beat: tension + curiosity
- blueprint: kinetic-type-beats
- asset_candidates:

narrativeRole: Break the default benchmark assumption and state the value thesis immediately.
keyMessage: Optimize the real workload, not one isolated number.

Scene 1 (0.0-2.6s): On deep green, only "FASTER DECODE" enters in oversized cream serif through a compact kinetic beat slam (`kinetic-beat-slam`); a thin mono speed rail grows beneath it.
Scene 2 (2.6-5.4s): "can make" arrives small; "THE WORKLOAD SLOWER" replaces the rail through a velocity-matched vertical swap (`discrete-text-sequence`), with SLOWER in mint.
Scene 3 (5.4-9.0s): The first claim compresses to the top third; "THE WORKLOAD IS THE DECISION" resolves large at center, then holds still for the read.

## Frame 2 - A measured enable

- scene: The real Studio window lands on ENABLE and its four measured decision metrics.
- voiceover: "MoE Autopilot Studio turns measured local-inference evidence into a reproducible verdict. At five hundred prompt tokens and three hundred output tokens, this split improves total latency by 4.4 percent."
- duration: 14.123s
- poster: 12s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/02-measured-enable.html
- type: product_intro
- persuasion: Show-don't-tell proof
- beat: clarity + control
- blueprint: video-text-pivot
- asset_candidates: assets/studio-enable.png - Real Studio ENABLE state with measured charts and candidate matrix; assets/studio-workflow.webm - Real packaged-app interaction recording

narrativeRole: Introduce the product through a real result, not a feature list.
keyMessage: The Studio converts evidence into an auditable workload verdict.

Scene 1 (0.0-3.2s): A browser-window crop of `studio-enable.png` enters from the lower right with a smooth long-tail settle; the camera locks onto the green verdict banner (`coordinate-target-zoom`).
Scene 2 (3.2-8.8s): As the VO names inputs, two editorial tags reveal sequentially: `500 PROMPT` and `300 OUTPUT`; the window remains readable and stable.
Scene 3 (8.8-12.3s): The measured `-4.4%` stat slides out of the real UI into a large left-side KPI block (`video-text-pivot` signature move), while the app remains visible on the right.
Scene 4 (12.3-15.0s): `ENABLE` and `MEASURED` lock together above a thin protocol fingerprint line; hold with no camera drift.

## Frame 3 - Same split, opposite answer

- scene: ENABLE and DISABLE states face each other, then the long-prompt state wins the frame.
- voiceover: "Change only the prompt to sixteen thousand tokens. Coverage stays at 68.6 percent. Decode still improves. But prefill now dominates, so the same split regresses total latency by 3.9 percent. Disable it."
- duration: 15.275s
- poster: 15s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/03-decision-flip.html
- type: feature_showcase
- persuasion: Controlled comparison
- beat: surprise + understanding
- blueprint: comparison-split
- asset_candidates: assets/studio-enable.png - ENABLE state at 500 in and 300 out; assets/studio-disable.png - DISABLE state at 16000 in and 300 out

narrativeRole: Deliver the memorable product demonstration: one workload change reverses the decision.
keyMessage: Workload shape can reverse the correct MoE-cache choice.

Scene 1 (0.0-4.2s): The ENABLE screenshot tilts open on the left; the DISABLE screenshot mirrors it on the right (`split-tilt-cards`). A central fixed label reads `SAME MODEL / SAME SPLIT`.
Scene 2 (4.2-8.0s): `500` morphs to `16000` in a mono prompt-token counter; all other input labels remain visually locked.
Scene 3 (8.0-12.8s): Coverage `68.6%` pins in the center while small `decode still improves` text appears beneath, proving what did not change.
Scene 4 (12.8-15.5s): The right DISABLE surface enlarges to full width; `+3.9%` extracts into a red-outlined KPI and the prefill bar overtakes baseline.
Scene 5 (15.5-18.0s): A restrained red `DISABLE` stamp lands once and holds; no bounce, no additional motion.

## Frame 4 - The protocol guard

- scene: The Evidence registry becomes an instrument panel that accepts one comparison and rejects another.
- voiceover: "The guardrail is protocol compatibility. The Studio joins prefill and decode only when model, build, flags, and instrument match. An older break-even near 2.3 is not blended in. The measured protocol recomputes 19.2."
- duration: 15.701s
- poster: 14s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/04-protocol-guard.html
- type: benefit_highlight
- persuasion: Risk reversal
- beat: skepticism -> trust
- blueprint: device-surface-showcase
- asset_candidates: assets/studio-evidence.png - Real Evidence registry with measured arms and protocol-limit warnings

narrativeRole: Explain why the verdict deserves trust and demonstrate refusal to mix incompatible evidence.
keyMessage: Protocol fingerprints prevent false certainty.

Scene 1 (0.0-4.0s): `studio-evidence.png` fills a flat editorial window; the measured-arm rows reveal top to bottom as the VO names compatibility.
Scene 2 (4.0-8.3s): Four mono chips - MODEL, BUILD, FLAGS, INSTRUMENT - assemble above the table (`grid-card-assemble`), joined by one green hairline.
Scene 3 (8.3-12.2s): The older `2.3` value enters from the left, hits a protocol boundary, and is displaced out (`reactive-displacement`); a small `INCOMPATIBLE` marker remains.
Scene 4 (12.2-17.0s): `19.2 : 1` counts up center-frame beside `MEASURED TOGETHER`; the evidence screenshot stays visible as the receipt and the shot holds.

## Frame 5 - A bounded council

- scene: Two parallel scouts feed validated opinions to a GPT-5.6 lead beside the unchanged deterministic verdict.
- voiceover: "Two independent scouts, Xiaomi MiMo and DeepSeek, review the same bounded report in parallel. GPT-5.6 synthesizes only validated opinions. The engine still owns every number, command, and experiment ID. In the live test, all three agreed. No model can overwrite the verdict."
- duration: 20.139s
- poster: 13s
- transition_in: crossfade
- status: animated
- src: compositions/frames/05-bounded-advisor.html
- type: feature_showcase
- persuasion: Trust through constrained AI
- beat: confidence
- blueprint: cursor-ui-demo
- asset_candidates: assets/studio-advisor.png - Capture replay of the validated three-member council UI; the live 3/3 run was tested separately

narrativeRole: Show model diversity without weakening the deterministic authority boundary.
keyMessage: Independent models can disagree or fail, but only validated opinions reach the lead and none can alter the result.

Scene 1 (0.0-3.8s): The advisor surface enters with the green ENABLE verdict already fixed.
Scene 2 (3.8-10.8s): Xiaomi MiMo and DeepSeek appear as parallel scouts, followed by GPT-5.6 as the synthesis lead.
Scene 3 (10.8-15.8s): `3 / 3 VALIDATED QUORUM` resolves beside the council while the measured report remains unchanged.
Scene 4 (15.8-20.1s): A lock line closes beneath the frame: `ENGINE OWNS NUMBERS · COMMANDS · EXPERIMENT IDS`.

## Frame 6 - From verdict to Windows run

- scene: The safe runner turns a selected experiment into an argv-only local A/B queue.
- voiceover: "A decision can become a Windows experiment without becoming a shell string. Executables, arguments, and environment stay structured. Timeouts, outputs, VRAM, cancellation, and process ownership are captured for the next comparison."
- duration: 14.571s
- poster: 12s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/06-windows-runner.html
- type: feature_showcase
- persuasion: Friction reduction + operational safety
- beat: control + momentum
- blueprint: device-surface-showcase
- asset_candidates: assets/studio-runs.png - Real Windows runner with structured paths, HOT_N, CPU layers, and a completed Qwen3.6-35B run

narrativeRole: Close the loop from analysis to a reproducible next experiment.
keyMessage: The Studio produces executable evidence without unsafe shell composition.

Scene 1 (0.0-4.2s): `studio-runs.png` enters as a full-height window, with the run specification column held sharp and the recent-run area softly dimmed (`depth-of-field-blur`).
Scene 2 (4.2-8.4s): Three flat code blocks assemble: `executable`, `argv[]`, `env{}`; an attempted `shell string` is crossed out and slides away.
Scene 3 (8.4-12.0s): Focus racks to the real completed Qwen3.6-35B run; VRAM and run ID receive short mono underlines.
Scene 4 (12.0-15.0s): TIMEOUT, OUTPUTS, VRAM, CANCEL, OWNERSHIP reveal one by one along the footline and hold.

## Frame 7 - What was actually built

- scene: Two clearly separated provenance bands show pre-existing evidence and Build Week product work.
- voiceover: "The measurements and llama.cpp work predate Build Week. The public Studio built this week adds the deterministic engine, fixture lab, imports, safe runner, exports, and bounded GPT-5.6 workflow. It works offline, with no GPU or model required."
- duration: 17.792s
- poster: 14s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/07-build-week-boundary.html
- type: social_proof
- persuasion: Credibility through provenance
- beat: trust + completeness
- blueprint: grid-card-assemble
- asset_candidates: assets/studio-enable.png - Public fixture-first Studio surface

narrativeRole: State the competition boundary plainly while showing the breadth of the eligible product.
keyMessage: Historical evidence became a new, public, testable Build Week product.

Scene 1 (0.0-4.0s): A left editorial band labeled `PRE-BUILD WEEK` reveals two restrained items: HISTORICAL MEASUREMENTS and LLAMA.CPP FORK.
Scene 2 (4.0-10.8s): A wider green band labeled `BUILT THIS WEEK` assembles six tiles sequentially: ENGINE, FIXTURES, IMPORTS, RUNNER, EXPORTS, GPT-5.6.
Scene 3 (10.8-14.0s): The actual Studio screenshot rises behind the tiles, connecting the list to the shipped product.
Scene 4 (14.0-17.0s): `OFFLINE / NO GPU / NO MODEL` lands as a quiet three-part footline and holds.

## Frame 8 - Reproduce the decision

- scene: Product identity condenses into the public repository and Windows release call to action.
- voiceover: "Do not trust the fastest number. Reproduce the decision. MoE Autopilot Studio is public now on GitHub, with a Windows release and fixture walkthrough."
- duration: 9.579s
- poster: 8s
- transition_in: blur-crossfade
- status: animated
- src: compositions/frames/08-reproduce.html
- type: cta
- persuasion: Direct action + risk reversal
- beat: motivation
- blueprint: logo-assemble-lockup
- asset_candidates: assets/studio-enable.png - Recognizable shipped-product surface for the closing lockup

narrativeRole: Convert the thesis into one concrete action and leave a memorable product identity.
keyMessage: Open the public Studio and reproduce the decision yourself.

Scene 1 (0.0-3.0s): The Studio screenshot collapses into a small monogram window while the words `FASTEST NUMBER` strike through.
Scene 2 (3.0-6.4s): `REPRODUCE THE DECISION` draws on in large cream serif over deep green; the monogram assembles beside it (`logo-assemble-lockup`).
Scene 3 (6.4-10.0s): The public URL `github.com/jcomlabs/moe-autopilot-studio` and `WINDOWS RELEASE + FIXTURE WALKTHROUGH` resolve beneath; one mint rule draws across and the frame holds.
