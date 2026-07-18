import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const framesDir = path.join(root, "compositions", "frames");
const voiceDir = path.join(root, "assets", "voice");
await mkdir(framesDir, { recursive: true });
await mkdir(voiceDir, { recursive: true });

const palette = {
  ink: "#102018",
  deep: "#19422e",
  green: "#176b4b",
  greenLite: "#276948",
  mint: "#dff3e9",
  paper: "#eef3ef",
  white: "#ffffff",
  blue: "#2868d7",
  amber: "#c07a0a",
  red: "#b83a32",
  muted: "#6b786f",
  line: "#cbd5ce",
};

const frames = [
  {
    id: "01-wrong-question",
    duration: 5.931,
    transition: "cut",
    voice: "Faster decode can make the whole workload slower. The setting is not the decision. The workload is.",
    body: `
      <div class="ground dark"></div>
      <div class="topbar light"><span>MOE AUTOPILOT / 01</span><span>WORKLOAD > NUMBER</span></div>
      <div class="hook-wrap">
        <div id="hook-a" class="hook-line serif">FASTER <span>DECODE</span></div>
        <div id="hook-rule" class="speed-rule"><i></i></div>
        <div id="hook-b" class="hook-small mono">CAN MAKE</div>
        <div id="hook-c" class="hook-payoff serif">THE WORKLOAD<br><em>SLOWER</em></div>
        <div id="hook-final" class="hook-final mono">THE WORKLOAD IS THE DECISION</div>
      </div>`,
    css: `
      .hook-wrap{position:absolute;left:120px;right:120px;top:170px;bottom:120px}
      .hook-line{font-size:156px;line-height:.9;color:${palette.white};white-space:nowrap}.hook-line span{color:${palette.mint}}
      .speed-rule{position:absolute;left:4px;top:190px;width:1170px;height:8px;background:#ffffff24}.speed-rule i{display:block;width:100%;height:100%;background:${palette.mint};transform-origin:left}
      .hook-small{position:absolute;left:8px;top:270px;font-size:30px;color:${palette.mint};letter-spacing:.16em}
      .hook-payoff{position:absolute;left:0;top:330px;font-size:124px;line-height:.88;color:${palette.white}}.hook-payoff em{font-style:normal;color:${palette.mint}}
      .hook-final{position:absolute;right:0;bottom:130px;padding:20px 26px;border:2px solid ${palette.mint};color:${palette.mint};font-size:25px;letter-spacing:.12em}
    `,
    timeline: `
      tl.fromTo("#hook-a",{opacity:0,y:70},{opacity:1,y:0,duration:1.1,ease:"power3.out"},0.25)
        .fromTo("#hook-rule i",{scaleX:0},{scaleX:1,duration:1.1,ease:"power3.out"},1.0)
        .fromTo("#hook-b",{opacity:0,x:-30},{opacity:1,x:0,duration:.65,ease:"power3.out"},2.7)
        .fromTo("#hook-c",{opacity:0,y:90,filter:"blur(8px)"},{opacity:1,y:0,filter:"blur(0px)",duration:1.15,ease:"power3.out"},3.6)
        .fromTo("#hook-final",{opacity:0,scaleX:.6,transformOrigin:"right center"},{opacity:1,scaleX:1,duration:.75,ease:"power3.out"},4.75);`,
  },
  {
    id: "02-measured-enable",
    duration: 14.123,
    transition: "zoom-through",
    voice: "MoE Autopilot Studio turns measured local-inference evidence into a reproducible verdict. At five hundred prompt tokens and three hundred output tokens, this split improves total latency by 4.4 percent.",
    body: `
      <div class="ground paper"></div><div class="topbar"><span>MEASURED VERDICT / 02</span><span>CODER-NEXT</span></div>
      <div id="enable-window" class="window-shot"><img src="assets/studio-enable.png" alt="Real Studio ENABLE analysis"></div>
      <div id="input-pills" class="pill-row"><span>500 PROMPT</span><span>300 OUTPUT</span></div>
      <div id="enable-kpi" class="kpi green-kpi"><b>-4.4%</b><small>TOTAL LATENCY</small></div>
      <div id="enable-lock" class="lockline mono"><span>ENABLE</span><span>MEASURED</span><code>8d00bad838c14baa</code></div>`,
    css: `
      .window-shot{position:absolute;left:170px;top:118px;width:1440px;height:900px;border:2px solid ${palette.ink};background:${palette.white};overflow:hidden}.window-shot img{width:100%;height:100%;object-fit:cover}
      .pill-row{position:absolute;left:122px;top:190px;display:flex;gap:12px}.pill-row span{padding:12px 16px;background:${palette.deep};color:${palette.white};font:600 20px 'JetBrains Mono',monospace;letter-spacing:.08em}
      .kpi{position:absolute;right:95px;top:260px;width:420px;padding:32px;border:2px solid ${palette.green};background:${palette.white}}.kpi b{display:block;font:400 112px/1 Georgia,serif}.kpi small{font:600 20px 'JetBrains Mono',monospace;letter-spacing:.12em}
      .green-kpi b{color:${palette.green}}
      .lockline{position:absolute;right:95px;bottom:165px;display:flex;gap:22px;align-items:center;padding:16px 20px;background:${palette.deep};color:${palette.white};font-size:18px}.lockline span{color:${palette.mint}}.lockline code{font-size:16px}
    `,
    timeline: `
      tl.fromTo("#enable-window",{opacity:0,y:80,scale:.96},{opacity:1,y:0,scale:1,duration:1.2,ease:"power3.out"},.2)
        .fromTo("#input-pills span",{opacity:0,y:24},{opacity:1,y:0,duration:.6,stagger:.35,ease:"power3.out"},3.6)
        .fromTo("#enable-kpi",{opacity:0,x:160},{opacity:1,x:0,duration:1,ease:"power3.out"},8.6)
        .fromTo("#enable-lock",{opacity:0,scaleX:.5,transformOrigin:"right center"},{opacity:1,scaleX:1,duration:.8,ease:"power3.out"},11.8);`,
  },
  {
    id: "03-decision-flip",
    duration: 15.275,
    transition: "push-slide LEFT",
    voice: "Change only the prompt to sixteen thousand tokens. Coverage stays at 68.6 percent. Decode still improves. But prefill now dominates, so the same split regresses total latency by 3.9 percent. Disable it.",
    body: `
      <div class="ground paper"></div><div class="topbar"><span>CONTROLLED COMPARISON / 03</span><span>SAME MODEL / SAME SPLIT</span></div>
      <div id="compare-left" class="compare-card left"><img src="assets/studio-enable.png" alt="ENABLE at short prompt"><strong>500</strong><small>PROMPT TOKENS</small></div>
      <div id="compare-right" class="compare-card right"><img src="assets/studio-disable.png" alt="DISABLE at long prompt"><strong>16000</strong><small>PROMPT TOKENS</small></div>
      <div id="constant" class="constant serif"><b>68.6%</b><span>COVERAGE<br>UNCHANGED</span></div>
      <div id="regress" class="regress"><b>+3.9%</b><span>PREFILL DOMINATES</span></div>
      <div id="disable-stamp" class="disable-stamp mono">DISABLE</div>`,
    css: `
      .compare-card{position:absolute;top:150px;width:790px;height:560px;border:2px solid ${palette.ink};background:${palette.white};overflow:hidden}.compare-card.left{left:100px}.compare-card.right{right:100px}.compare-card img{width:100%;height:494px;object-fit:cover;object-position:top}.compare-card strong{position:absolute;left:24px;bottom:10px;font:400 52px Georgia,serif}.compare-card small{position:absolute;left:164px;bottom:22px;font:600 16px 'JetBrains Mono',monospace;letter-spacing:.1em}
      .constant{position:absolute;left:690px;top:755px;width:520px;padding:22px 30px;background:${palette.deep};color:${palette.white};display:flex;align-items:center;gap:26px}.constant b{font-size:76px;color:${palette.mint}}.constant span{font:600 18px 'JetBrains Mono',monospace;letter-spacing:.1em}
      .regress{position:absolute;right:100px;top:755px;width:430px;padding:22px;border:2px solid ${palette.red};background:${palette.white}}.regress b{display:block;font:400 82px Georgia,serif;color:${palette.red}}.regress span{font:600 16px 'JetBrains Mono',monospace;letter-spacing:.1em}
      .disable-stamp{position:absolute;left:100px;top:790px;padding:22px 38px;border:4px solid ${palette.red};color:${palette.red};font-size:36px;letter-spacing:.16em;transform:rotate(-3deg)}
    `,
    timeline: `
      tl.fromTo("#compare-left",{opacity:0,x:-180,rotateY:18},{opacity:1,x:0,rotateY:0,duration:1.1,ease:"power3.out"},.3)
        .fromTo("#compare-right",{opacity:0,x:180,rotateY:-18},{opacity:1,x:0,rotateY:0,duration:1.1,ease:"power3.out"},1.0)
        .fromTo("#constant",{opacity:0,y:40},{opacity:1,y:0,duration:.9,ease:"power3.out"},7.1)
        .fromTo("#regress",{opacity:0,x:100},{opacity:1,x:0,duration:.9,ease:"power3.out"},12.2)
        .fromTo("#disable-stamp",{opacity:0,scale:1.7,filter:"blur(5px)"},{opacity:1,scale:1,filter:"blur(0px)",duration:.55,ease:"power3.out"},14.35);`,
  },
  {
    id: "04-protocol-guard",
    duration: 15.701,
    transition: "zoom-through",
    voice: "The guardrail is protocol compatibility. The Studio joins prefill and decode only when model, build, flags, and instrument match. An older break-even near 2.3 is not blended in. The measured protocol recomputes 19.2.",
    body: `
      <div class="ground paper"></div><div class="topbar"><span>EVIDENCE REGISTRY / 04</span><span>PROTOCOL FINGERPRINT</span></div>
      <div id="evidence-window" class="evidence-window"><img src="assets/studio-evidence.png" alt="Protocol-compatible evidence registry"></div>
      <div id="protocol-chips" class="protocol-chips mono"><span>MODEL</span><span>BUILD</span><span>FLAGS</span><span>INSTRUMENT</span></div>
      <div id="old-value" class="old-value serif"><b>2.3</b><span>OLDER / INCOMPATIBLE</span></div>
      <div id="boundary" class="boundary"></div>
      <div id="measured-value" class="measured-value serif"><b>19.2 : 1</b><span>MEASURED TOGETHER</span></div>`,
    css: `
      .evidence-window{position:absolute;left:120px;top:155px;width:1280px;height:800px;border:2px solid ${palette.ink};background:${palette.white};overflow:hidden}.evidence-window img{width:100%;height:100%;object-fit:cover;object-position:top}
      .protocol-chips{position:absolute;right:105px;top:175px;width:350px;display:grid;gap:12px}.protocol-chips span{padding:18px 22px;border:2px solid ${palette.green};background:${palette.white};color:${palette.deep};font-size:18px;letter-spacing:.1em}
      .old-value{position:absolute;right:120px;top:505px;width:310px;padding:20px;border:2px solid ${palette.red};background:${palette.white};color:${palette.red}}.old-value b,.measured-value b{display:block;font-size:86px}.old-value span,.measured-value span{font:600 15px 'JetBrains Mono',monospace;letter-spacing:.09em}
      .boundary{position:absolute;right:90px;top:490px;width:370px;height:2px;background:${palette.red};transform:rotate(-8deg)}
      .measured-value{position:absolute;right:90px;bottom:175px;width:400px;padding:26px;background:${palette.deep};color:${palette.white}}.measured-value b{color:${palette.mint};font-size:74px}
    `,
    timeline: `
      tl.fromTo("#evidence-window",{opacity:0,y:60},{opacity:1,y:0,duration:1,ease:"power3.out"},.2)
        .fromTo("#protocol-chips span",{opacity:0,x:80},{opacity:1,x:0,duration:.55,stagger:.45,ease:"power3.out"},3.2)
        .fromTo("#old-value",{opacity:0,x:100},{opacity:1,x:0,duration:.7,ease:"power3.out"},8.1)
        .fromTo("#boundary",{scaleX:0,transformOrigin:"left"},{scaleX:1,duration:.45,ease:"power3.out"},9.6)
        .to("#old-value",{x:430,opacity:0,duration:.65,ease:"power3.in"},10.2)
        .fromTo("#measured-value",{opacity:0,y:70},{opacity:1,y:0,duration:.9,ease:"power3.out"},12.0);`,
  },
  {
    id: "05-bounded-advisor",
    duration: 15.979,
    transition: "crossfade",
    voice: "GPT-5.6 does the language work, not the arithmetic. Through Codex App Server and ChatGPT OAuth, it explains the structured report and proposes only experiments the engine already produced. The verdict cannot be overwritten.",
    body: `
      <div class="ground paper"></div><div class="topbar"><span>BOUNDED ADVISOR / 05</span><span>GPT-5.6 + APP SERVER</span></div>
      <div id="advisor-window" class="advisor-window"><img src="assets/studio-advisor.png" alt="Live GPT-5.6 explanation"></div>
      <div id="roles" class="role-stack mono"><span><b>ENGINE</b> CALCULATE</span><span><b>GPT-5.6</b> EXPLAIN</span><span><b>USER</b> CONFIRM</span></div>
      <div id="cursor" class="cursor">↖</div><div id="ripple" class="ripple"></div>
      <div id="advisor-lock" class="advisor-lock mono">VERDICT LOCKED / INVALID EXPERIMENT IDS REJECTED</div>`,
    css: `
      .advisor-window{position:absolute;left:120px;top:145px;width:1440px;height:900px;border:2px solid ${palette.ink};background:${palette.white};overflow:hidden}.advisor-window img{width:100%;height:100%;object-fit:cover}
      .role-stack{position:absolute;right:78px;top:220px;width:355px;display:grid;gap:10px}.role-stack span{padding:18px;background:${palette.deep};color:${palette.white};font-size:17px;letter-spacing:.08em}.role-stack b{color:${palette.mint};margin-right:12px}
      .cursor{position:absolute;right:190px;bottom:160px;font-size:54px;color:${palette.blue};text-shadow:0 2px 0 #fff}.ripple{position:absolute;right:205px;bottom:178px;width:80px;height:80px;border:4px solid ${palette.blue};border-radius:50%}
      .advisor-lock{position:absolute;left:420px;bottom:165px;padding:16px 24px;background:${palette.deep};color:${palette.mint};font-size:17px;letter-spacing:.09em}
    `,
    timeline: `
      tl.fromTo("#advisor-window",{opacity:0,y:55},{opacity:1,y:0,duration:1,ease:"power3.out"},.2)
        .fromTo("#cursor",{opacity:0,x:180,y:120},{opacity:1,x:0,y:0,duration:1.2,ease:"power3.out"},2.4)
        .fromTo("#ripple",{opacity:0,scale:.2},{opacity:1,scale:1,duration:.35,ease:"power2.out"},3.45).to("#ripple",{opacity:0,scale:1.8,duration:.5,ease:"power2.out",overwrite:"auto"},3.82)
        .fromTo("#roles span",{opacity:0,x:80},{opacity:1,x:0,duration:.55,stagger:.7,ease:"power3.out"},4.4)
        .fromTo("#advisor-lock",{opacity:0,scaleX:.4,transformOrigin:"center"},{opacity:1,scaleX:1,duration:.8,ease:"power3.out"},12.2);`,
  },
  {
    id: "06-windows-runner",
    duration: 14.571,
    transition: "push-slide LEFT",
    voice: "A decision can become a Windows experiment without becoming a shell string. Executables, arguments, and environment stay structured. Timeouts, outputs, VRAM, cancellation, and process ownership are captured for the next comparison.",
    body: `
      <div class="ground paper"></div><div class="topbar"><span>LOCAL EXPERIMENT QUEUE / 06</span><span>WINDOWS</span></div>
      <div id="runs-window" class="runs-window"><img src="assets/studio-runs.png" alt="Safe Windows experiment runner"></div>
      <div id="argv-cards" class="argv-cards mono"><span>executable</span><span>argv[]</span><span>env{}</span></div>
      <div id="no-shell" class="no-shell mono">SHELL STRING</div>
      <div id="runner-foot" class="runner-foot mono"><span>TIMEOUT</span><span>OUTPUTS</span><span>VRAM</span><span>CANCEL</span><span>OWNERSHIP</span></div>`,
    css: `
      .runs-window{position:absolute;left:105px;top:145px;width:1440px;height:810px;border:2px solid ${palette.ink};background:${palette.white};overflow:hidden}.runs-window img{width:100%;height:100%;object-fit:cover;object-position:top}
      .argv-cards{position:absolute;right:80px;top:220px;display:grid;gap:12px;width:320px}.argv-cards span{padding:20px 24px;background:${palette.deep};color:${palette.mint};font-size:21px;letter-spacing:.08em}
      .no-shell{position:absolute;right:78px;top:500px;padding:20px 26px;border:3px solid ${palette.red};color:${palette.red};font-size:18px;letter-spacing:.08em}.no-shell:after{content:"";position:absolute;left:-10px;right:-10px;top:50%;height:3px;background:${palette.red};transform:rotate(-7deg)}
      .runner-foot{position:absolute;left:105px;right:105px;bottom:165px;min-height:58px;display:flex;justify-content:space-between;align-items:flex-start;border-top:2px solid ${palette.green};padding-top:17px;color:${palette.deep};font-size:18px;letter-spacing:.1em}
    `,
    timeline: `
      tl.fromTo("#runs-window",{opacity:0,y:60},{opacity:1,y:0,duration:1,ease:"power3.out"},.2)
        .fromTo("#argv-cards span",{opacity:0,x:90},{opacity:1,x:0,duration:.55,stagger:.55,ease:"power3.out"},3.6)
        .fromTo("#no-shell",{opacity:0,scale:1.3},{opacity:1,scale:1,duration:.55,ease:"power3.out"},7.0)
        .to("#no-shell",{x:420,opacity:0,duration:.65,ease:"power3.in"},8.2)
        .fromTo("#runner-foot span",{opacity:0,y:22},{opacity:1,y:0,duration:.45,stagger:.4,ease:"power3.out"},10.0);`,
  },
  {
    id: "07-build-week-boundary",
    duration: 17.792,
    transition: "zoom-through",
    voice: "The measurements and llama.cpp work predate Build Week. The public Studio built this week adds the deterministic engine, fixture lab, imports, safe runner, exports, and bounded GPT-5.6 workflow. It works offline, with no GPU or model required.",
    body: `
      <div class="ground paper"></div><div class="topbar"><span>PROVENANCE / 07</span><span>OPENAI BUILD WEEK</span></div>
      <section id="before-band" class="before-band"><h2>PRE-BUILD WEEK</h2><p>HISTORICAL MEASUREMENTS</p><p>LLAMA.CPP FORK</p></section>
      <section id="built-band" class="built-band"><h2>BUILT THIS WEEK</h2><div class="build-grid mono"><span>ENGINE</span><span>FIXTURES</span><span>IMPORTS</span><span>RUNNER</span><span>EXPORTS</span><span>GPT-5.6</span></div></section>
      <div id="boundary-shot" class="boundary-shot"><img src="assets/studio-enable.png" alt="Shipped Studio"></div>
      <div id="offline-foot" class="offline-foot mono"><span>OFFLINE</span><span>NO GPU</span><span>NO MODEL</span></div>`,
    css: `
      .before-band{position:absolute;left:100px;top:155px;width:480px;height:690px;padding:38px;border:2px solid ${palette.ink};background:${palette.white}}.before-band h2,.built-band h2{font:600 20px 'JetBrains Mono',monospace;letter-spacing:.13em}.before-band p{margin-top:44px;padding-top:18px;border-top:2px solid ${palette.line};font:400 42px/1.1 Georgia,serif}
      .built-band{position:absolute;left:610px;right:100px;top:155px;height:690px;padding:38px;background:${palette.deep};color:${palette.white}}.built-band h2{color:${palette.mint}}
      .build-grid{position:absolute;left:38px;right:38px;top:110px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.build-grid span{height:150px;display:flex;align-items:flex-end;padding:20px;border:2px solid ${palette.mint};color:${palette.mint};font-size:22px;letter-spacing:.09em}
      .boundary-shot{position:absolute;right:130px;bottom:155px;width:690px;height:350px;border:2px solid ${palette.ink};overflow:hidden;background:${palette.white}}.boundary-shot img{width:100%;height:100%;object-fit:cover;object-position:top}
      .offline-foot{position:absolute;left:100px;right:100px;bottom:165px;display:flex;justify-content:space-between;border-top:2px solid ${palette.green};padding-top:16px;color:${palette.deep};font-size:20px;letter-spacing:.14em}
    `,
    timeline: `
      tl.fromTo("#before-band",{opacity:0,x:-80},{opacity:1,x:0,duration:.9,ease:"power3.out"},.3)
        .fromTo("#built-band",{opacity:0,x:100},{opacity:1,x:0,duration:.9,ease:"power3.out"},2.0)
        .fromTo("#built-band .build-grid span",{opacity:0,y:40},{opacity:1,y:0,duration:.5,stagger:.55,ease:"power3.out"},4.0)
        .fromTo("#boundary-shot",{opacity:0,y:80},{opacity:1,y:0,duration:.9,ease:"power3.out"},10.0)
        .fromTo("#offline-foot span",{opacity:0,y:18},{opacity:1,y:0,duration:.45,stagger:.5,ease:"power3.out"},13.3);`,
  },
  {
    id: "08-reproduce",
    duration: 9.579,
    transition: "blur-crossfade",
    voice: "Do not trust the fastest number. Reproduce the decision. MoE Autopilot Studio is public now on GitHub, with a Windows release and fixture walkthrough.",
    body: `
      <div class="ground dark"></div><div class="topbar light"><span>MOE AUTOPILOT STUDIO / 08</span><span>PUBLIC NOW</span></div>
      <div id="fastest" class="fastest mono">FASTEST NUMBER</div>
      <div id="strike" class="strike"></div>
      <div id="final-title" class="final-title serif">REPRODUCE<br>THE <em>DECISION</em></div>
      <div id="final-mark" class="final-mark mono">MA</div>
      <div id="final-url" class="final-url mono">github.com/jcomlabs/moe-autopilot-studio</div>
      <div id="final-sub" class="final-sub mono">WINDOWS RELEASE + FIXTURE WALKTHROUGH</div><div id="final-rule" class="final-rule"></div>`,
    css: `
      .fastest{position:absolute;left:125px;top:220px;color:#ffffff99;font-size:32px;letter-spacing:.13em}.strike{position:absolute;left:110px;top:239px;width:380px;height:5px;background:${palette.red};transform-origin:left}
      .final-title{position:absolute;left:120px;top:320px;color:${palette.white};font-size:126px;line-height:.86}.final-title em{font-style:normal;color:${palette.mint}}
      .final-mark{position:absolute;right:155px;top:325px;width:210px;height:210px;border:4px solid ${palette.mint};border-radius:50%;display:flex;align-items:center;justify-content:center;color:${palette.mint};font-size:54px;letter-spacing:.06em}
      .final-url{position:absolute;left:125px;bottom:245px;color:${palette.mint};font-size:27px;letter-spacing:.04em}.final-sub{position:absolute;left:125px;bottom:190px;color:${palette.white};font-size:18px;letter-spacing:.13em}.final-rule{position:absolute;left:125px;bottom:158px;width:1080px;height:3px;background:${palette.mint};transform-origin:left}
    `,
    timeline: `
      tl.fromTo("#fastest",{opacity:0,y:25},{opacity:1,y:0,duration:.7,ease:"power3.out"},.3)
        .fromTo("#strike",{scaleX:0},{scaleX:1,duration:.55,ease:"power3.out"},1.7)
        .fromTo("#final-title",{opacity:0,y:80,filter:"blur(7px)"},{opacity:1,y:0,filter:"blur(0px)",duration:1.1,ease:"power3.out"},2.8)
        .fromTo("#final-mark",{opacity:0,scale:.2,rotate:-80},{opacity:1,scale:1,rotate:0,duration:1,ease:"power3.out"},4.2)
        .fromTo("#final-url",{opacity:0,y:24},{opacity:1,y:0,duration:.7,ease:"power3.out"},6.2)
        .fromTo("#final-sub",{opacity:0,y:20},{opacity:1,y:0,duration:.65,ease:"power3.out"},7.0)
        .fromTo("#final-rule",{scaleX:0},{scaleX:1,duration:.7,ease:"power3.out"},7.3);`,
  },
];

function frameDocument(frame) {
  return `<!doctype html>
<html lang="en"><head><meta charset="UTF-8"></head><body><template>
<style>
  *{box-sizing:border-box}#root{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden;container-type:size;color:${palette.ink};font-family:Georgia,serif}.clip,.ground{position:absolute;inset:0}.ground.paper{background:${palette.paper}}.ground.dark{background:${palette.deep}}.serif{font-family:Georgia,serif}.mono{font-family:'JetBrains Mono',Consolas,monospace}.topbar{position:absolute;left:80px;right:80px;top:48px;display:flex;justify-content:space-between;padding-bottom:18px;border-bottom:2px solid ${palette.green};font:600 18px 'JetBrains Mono',Consolas,monospace;letter-spacing:.13em;color:${palette.deep};z-index:50}.topbar.light{color:${palette.mint};border-color:${palette.mint}}
  ${frame.css}
</style>
<div id="root" data-composition-id="${frame.id}" data-width="1920" data-height="1080" data-duration="${frame.duration}">${frame.body}</div>
<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});${frame.timeline}tl.to({}, {duration:${frame.duration}}, 0);window.__timelines["${frame.id}"]=tl;<\/script>
</template></body></html>`.replace(/[ \t]+$/gm, "");
}

for (const [index, frame] of frames.entries()) {
  await writeFile(path.join(framesDir, `${frame.id}.html`), frameDocument(frame), "utf8");
  await writeFile(path.join(voiceDir, `${String(index + 1).padStart(2, "0")}.txt`), frame.voice, "utf8");
}

let cursor = 0;
const scenes = frames.map((frame, index) => {
  const start = cursor;
  cursor += frame.duration;
  const number = String(index + 1).padStart(2, "0");
  return `
    <div id="scene-${number}" class="scene" data-composition-id="${frame.id}" data-composition-src="compositions/frames/${frame.id}.html" data-start="${start}" data-duration="${frame.duration}" data-track-index="${index % 2}"></div>
    <audio id="voice-${number}" src="assets/voice/${number}.wav" data-start="${start}" data-duration="${frame.duration}" data-track-index="10" data-volume="1"></audio>`;
}).join("\n");

const transitionCode = frames.slice(1).map((frame, index) => {
  const at = frames.slice(0, index + 1).reduce((sum, item) => sum + item.duration, 0);
  const out = `#scene-${String(index + 1).padStart(2, "0")}`;
  const incoming = `#scene-${String(index + 2).padStart(2, "0")}`;
  if (frame.transition.startsWith("push-slide")) {
    return `tl.to("${out}",{x:-1920,duration:.5,ease:"power3.inOut"},${at}).fromTo("${incoming}",{x:1920},{x:0,duration:.5,ease:"power3.inOut"},${at});`;
  }
  if (frame.transition === "zoom-through") {
    return `tl.to("${out}",{scale:2.2,opacity:0,filter:"blur(8px)",duration:.45,ease:"power3.in"},${at}).fromTo("${incoming}",{scale:.55,opacity:0,filter:"blur(8px)"},{scale:1,opacity:1,filter:"blur(0px)",duration:.45,ease:"power3.out"},${at});`;
  }
  if (frame.transition === "blur-crossfade") {
    return `tl.to("${out}",{opacity:0,filter:"blur(8px)",duration:.5,ease:"power2.inOut"},${at}).fromTo("${incoming}",{opacity:0,filter:"blur(8px)"},{opacity:1,filter:"blur(0px)",duration:.5,ease:"power2.inOut"},${at});`;
  }
  return `tl.to("${out}",{opacity:0,duration:.45,ease:"power2.inOut"},${at}).fromTo("${incoming}",{opacity:0},{opacity:1,duration:.45,ease:"power2.inOut"},${at});`;
}).join("\n");

const index = `<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920,height=1080"><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"><\/script><style>*{margin:0;padding:0;box-sizing:border-box}html,body,#root{width:1920px;height:1080px;overflow:hidden;background:${palette.deep}}.scene{position:absolute;inset:0;width:1920px;height:1080px}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${cursor}" data-width="1920" data-height="1080">${scenes}
  <div id="captions" class="scene" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="${cursor}" data-track-index="100"></div>
</div>
<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});${transitionCode}tl.to({}, {duration:${cursor}}, 0);window.__timelines.main=tl;<\/script></body></html>`;
await writeFile(path.join(root, "index.html"), index, "utf8");

console.log(`Built ${frames.length} frames, ${cursor}s total.`);
