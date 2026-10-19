# Builds index.html for ad 02 (SaltLine Smokehouse call) from transcript.json + clip.segs.json.
# The call-flow map (RezFlo's own design): every step of the call is a card; the active step glows purple,
# finished steps get a green tick, a purple line fills the arrow to the next step, and the map pans as the call moves.
# Run: python3 cut.py … ; python3 music.py <clip> <end> <swell> ; python3 build.py ; npx hyperframes check / render
import json, html

SEGS = json.load(open("clip.segs.json"))
CLIP = SEGS[-1]["out"][1]
END, XF = 3.6, 0.7
TOTAL = round(CLIP + END, 2)

W = [w for s in json.load(open("transcript.json")) for w in s["words"]]
words = [{"w": w["w"].strip(), "s": round(w["s"], 2), "e": round(w["e"], 2)} for w in W][:284]  # 284+ is whisper noise in the fade-out
T = lambda i: words[i]["s"]

CALLER = [(11, 18), (30, 37), (48, 55), (67, 81), (88, 97), (120, 128), (142, 143), (153, 158), (173, 176), (212, 214), (230, 236), (270, 274)]
for i, w in enumerate(words):
    w["ai"] = not any(a <= i <= b for a, b in CALLER)
cw = []
i = 0
while i < len(words):   # caption words, with "Salt" + "Line…" merged
    w = dict(words[i])
    if w["w"] == "Salt" and i + 1 < len(words) and words[i + 1]["w"].startswith("Line"):
        w["w"] = "SaltLine" + words[i + 1]["w"][4:]; w["e"] = words[i + 1]["e"]; i += 1
    if cw and (w["w"][0] in "-." or w["w"][0].isdigit() and cw[-1]["w"].endswith(".")) and w["s"] - cw[-1]["e"] < 0.8 and cw[-1]["ai"] == w["ai"]:
        cw[-1]["w"] += w["w"]; cw[-1]["e"] = w["e"]   # "gluten" + "-free", "$49" + ".72", "one" + "-piece"
    else:
        cw.append(w)
    i += 1

chunks, cur = [], []
for w in cw:
    if cur and (w["ai"] != cur[-1]["ai"] or w["s"] - cur[-1]["e"] > 0.35 or len(cur) >= 4
                or cur[-1]["w"][-1] in ".?!" or (cur[-1]["w"][-1] == "," and len(cur) >= 2)):
        chunks.append(cur); cur = []
    cur.append(w)
chunks.append(cur)
cap_html, cap_js = [], []
for k, c in enumerate(chunks):
    a = round(c[0]["s"] - 0.06, 2)
    nxt = chunks[k + 1][0]["s"] - 0.06 if k + 1 < len(chunks) else CLIP
    b = round(min(nxt, c[-1]["e"] + 0.5), 2)
    cls = "cap ai" if c[0]["ai"] else "cap me"
    cap_html.append(f'<div id="c{k}" class="{cls}">' + " ".join(f'<span class="w">{html.escape(w["w"])}</span>' for w in c) + "</div>")
    cap_js.append([k, a, b, [w["s"] for w in c]])

# --- the call-flow map ---------------------------------------------------------------
ICON = {
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "bag": '<path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "plus": '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>',
    "swap": '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "note": '<path d="M5 4h14v12l-4 4H5z"/><path d="M15 20v-4h4M8 9h8M8 13h5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "cup": '<path d="M6 7h12l-1.6 14H7.6z"/><path d="M5 7h14M13 7l2-5h3"/>',
    "check": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="M3 6l1.2 1.2L6.5 5M3 12l1.2 1.2 2.3-2.2M3 18l1.2 1.2 2.3-2.2"/>',
    "msg": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    "bot": '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 8V4M9 13h.01M15 13h.01M9.5 16h5"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
}
# (title, detail, icon, start word, "any time" step)
STEPS = [
    ("Greeting", "SaltLine", "phone", 0, False),
    ("Pickup order", "Pickup", "bag", 19, False),
    ("Take the order", "Fish tacos", "list", 30, False),
    ("Offer a meal", "Meal + yam fries", "plus", 42, False),
    ("Swap an item", "Cod → halibut", "swap", 75, False),
    ("Allergy question", "Answered", "shield", 88, False),
    ("Special notes", "Tartar on side", "note", 117, False),
    ("Name + time", "Jonas · ASAP", "clock", 134, False),
    ("Offer add-ons", "No thanks", "cup", 165, False),
    ("Read it back", "Confirmed", "check", 177, False),
    ("Total + text", "Summary texted", "msg", 215, False),
    ("Says it's AI", "When asked", "bot", 230, True),
    ("Offer a human", "Stayed with AI", "person", 253, True),
    ("Wrap up", "See you soon", "flag", 275, False),
]
CW, CH, GX, GY, X0, Y0 = 270, 122, 50, 64, 85, 24
def cell(k):                     # snake: rows of 3, alternating direction
    r, c = divmod(k, 3)
    if r % 2: c = 2 - c
    return r, c, X0 + c * (CW + GX), Y0 + r * (CH + GY)
ROWS = (len(STEPS) + 2) // 3
MAPH = Y0 + ROWS * (CH + GY)
VPH = 2 * (CH + GY) + 6          # visible window: exactly two rows of the map

cards, links = [], []
for k, (title, detail, icon, _, anytime) in enumerate(STEPS):
    r, c, x, y = cell(k)
    tag = '<span class="any mono">Any time</span>' if anytime else ""
    cards.append(f'<div id="n{k}" class="node{" anytime" if anytime else ""}" style="left:{x}px;top:{y}px">{tag}'
                 f'<div class="tile"><svg viewBox="0 0 24 24">{ICON[icon]}</svg></div>'
                 f'<div class="txt"><div class="t">{html.escape(title)}</div><div class="d mono">{html.escape(detail)}</div></div>'
                 f'<i class="tick"><svg viewBox="0 0 24 24"><path d="M6 12.5l4 4L18 8"/></svg></i></div>')
    if k + 1 < len(STEPS):
        r2, c2, x2, y2 = cell(k + 1)
        if r2 == r:   # same row: horizontal arrow
            if c2 > c: x1_, x2_ = x + CW + 8, x2 - 10
            else:      x1_, x2_ = x - 8, x2 + CW + 10
            ya = y + CH / 2
            d = f"M{x1_},{ya} L{x2_},{ya}"; L = abs(x2_ - x1_)
        else:         # down to the next row
            xa = x + CW / 2
            d = f"M{xa},{y + CH + 8} L{xa},{y2 - 10}"; L = y2 - 10 - (y + CH + 8)
        dash = ' stroke-dasharray="6 7"' if STEPS[k + 1][4] or anytime else ""
        links.append(f'<path class="lb" d="{d}"{dash}/><path id="l{k}" class="lf" d="{d}" style="stroke-dasharray:{L:.0f};stroke-dashoffset:{L:.0f}" marker-end="url(#ah)"/>')

steps_js = [[round(T(s[3]), 2), cell(k)[0]] for k, s in enumerate(STEPS)]

page = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="./gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Space Grotesk"; src: url("fonts/SpaceGrotesk-700.woff2") format("woff2"); font-weight: 700; }}
      @font-face {{ font-family: "Inter"; src: url("fonts/Inter-400.woff2") format("woff2"); font-weight: 400; }}
      @font-face {{ font-family: "Inter"; src: url("fonts/Inter-700.woff2") format("woff2"); font-weight: 700; }}
      @font-face {{ font-family: "JetBrains Mono"; src: url("fonts/JetBrainsMono-400.woff2") format("woff2"); font-weight: 400; }}
      @font-face {{ font-family: "Instrument Serif"; src: url("fonts/InstrumentSerif-400-italic.woff2") format("woff2"); font-weight: 400; font-style: italic; }}
      :root {{ --ink: #0b0a12; --brand: #5b41da; --peri: #8f7bff; --green: #34c759; --cream: #f3efe6; --dk: #16141f; --dkb: #2a2738; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Inter", sans-serif; background: var(--ink); }}
      .clip {{ position: absolute; inset: 0; }}
      .mono {{ font-family: "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: 0.12em; }}

      #vw {{ position: absolute; inset: 0; transform-origin: 540px 880px; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #shade {{ position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(11,10,18,0.78) 0%, rgba(11,10,18,0.6) 20%, rgba(11,10,18,0) 31%, rgba(11,10,18,0) 60%, rgba(11,10,18,0.35) 70%, rgba(11,10,18,0.35) 78%, rgba(11,10,18,0) 92%); }}

      /* hook */
      #hook {{ position: absolute; left: 0; top: 150px; width: 1080px; text-align: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 100px; line-height: 1.02; letter-spacing: -0.03em; color: #fff; }}
      #hook .ln {{ display: block; overflow: hidden; padding: 0 0 8px; }}
      #hook .ln span {{ display: inline-block; text-shadow: 0 6px 30px rgba(11,10,18,0.75); }}
      #hook .ai {{ color: var(--peri); text-shadow: 0 0 26px rgba(143,123,255,0.85), 0 6px 30px rgba(11,10,18,0.75); }}

      /* call-flow map (top of frame, above his head) */
      #vp {{ position: absolute; left: 0; top: 70px; width: 1080px; height: {VPH}px; overflow: hidden;
        opacity: 0; }}
      #map {{ position: absolute; left: 0; top: 0; width: 1080px; height: {MAPH}px; }}
      #links {{ position: absolute; inset: 0; width: 1080px; height: {MAPH}px; overflow: visible; }}
      .lb {{ fill: none; stroke: rgba(185,183,198,0.4); stroke-width: 3; }}
      .lf {{ fill: none; stroke: var(--peri); stroke-width: 4; filter: drop-shadow(0 0 6px rgba(143,123,255,0.9)); }}
      .node {{ position: absolute; width: {CW}px; height: {CH}px; border-radius: 30px; background: rgba(22,20,31,0.9); border: 2.5px solid var(--dkb);
        display: flex; align-items: center; gap: 14px; padding: 0 16px; opacity: 0.5; box-shadow: 0 16px 36px rgba(11,10,18,0.45); }}
      .node.anytime {{ border-style: dashed; border-color: rgba(143,123,255,0.45); }}
      .node .any {{ position: absolute; right: 18px; top: -15px; font-size: 14px; color: #c9bfff; background: var(--ink); border: 1.5px solid rgba(143,123,255,0.7); padding: 4px 9px; border-radius: 8px; }}
      .tile {{ width: 58px; height: 58px; border-radius: 18px; background: #221e33; display: flex; align-items: center; justify-content: center; flex: none; }}
      .tile svg {{ width: 32px; height: 32px; fill: none; stroke: #b9adff; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }}
      .txt {{ flex: 1; min-width: 0; }}
      .node .t {{ font-weight: 700; font-size: 25px; line-height: 1.06; color: #fff; }}
      .node .d {{ font-size: 13px; letter-spacing: 0.08em; color: #b9b5cc; margin-top: 6px; white-space: nowrap; opacity: 0; }}
      .node .tick {{ position: absolute; right: -10px; top: -10px; width: 34px; height: 34px; border-radius: 50%; background: var(--green); border: 3px solid var(--ink); display: flex; align-items: center; justify-content: center; opacity: 0; }}
      .node .tick svg {{ width: 20px; height: 20px; fill: none; stroke: #fff; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }}

      /* captions (on his chest, above the phone) */
      .cap {{ position: absolute; left: 110px; bottom: 470px; width: 860px; text-align: center; font-weight: 700; font-size: 60px; line-height: 1.1; letter-spacing: -0.01em; opacity: 0; }}
      .cap .w {{ display: inline-block; color: #fff; opacity: 0.7; text-shadow: 0 2px 0 rgba(11,10,18,0.45), 0 4px 20px rgba(11,10,18,0.95); }}

      /* end banner */
      #endc {{ position: absolute; inset: 0; background: radial-gradient(900px 1200px at 50% 44%, #6c53ee 0%, var(--brand) 64%); color: var(--cream);
        display: flex; flex-direction: column; align-items: center; justify-content: center; padding-bottom: 180px; }}
      #eR {{ width: 210px; height: 210px; border-radius: 54px; background: var(--cream); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 140px 30px rgba(243,239,230,0.22); }}
      #eR .rm {{ width: 150px; height: 150px; overflow: visible; }}
      #eq {{ margin-top: 54px; font-size: 26px; color: var(--cream); background: rgba(11,10,18,0.22); padding: 14px 24px; border-radius: 14px; }}
      #esee-m {{ margin-top: 26px; overflow: hidden; padding: 0 60px 10px; text-align: center; }}
      #esee {{ display: block; font-family: "Instrument Serif", serif; font-style: italic; font-size: 132px; line-height: 1.02; }}
      #eurl {{ font-size: 28px; margin-top: 18px; }}
      #ebelow {{ position: absolute; left: 0; top: 1380px; width: 1080px; display: flex; justify-content: center; align-items: center; gap: 16px; font-weight: 700; font-size: 44px; }}
      #ebelow b {{ display: inline-block; font-size: 50px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="vw">
        <video id="src" class="clip" src="clip.mp4" data-start="0" data-duration="{CLIP}" data-has-audio="true" playsinline></video>
        <div id="shade"></div>
      </div>
      <audio id="music" src="music.wav" data-start="0" data-duration="{TOTAL}" data-volume="1"></audio>

      <div id="ov" class="clip" data-start="0" data-duration="{CLIP}" style="z-index:20">
        <div id="hook"><span class="ln"><span>Can you tell</span></span><span class="ln"><span>this is <b class="ai">AI?</b></span></span></div>
        <div id="vp"><div id="map" data-layout-allow-overflow>
          <svg id="links" viewBox="0 0 1080 {MAPH}"><defs><marker id="ah" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#8f7bff"/></marker></defs>{"".join(links)}</svg>
          {"".join(cards)}
        </div></div>
        {(chr(10) + "        ").join(cap_html)}
      </div>

      <div id="endc" class="clip" data-start="{round(CLIP - XF, 2)}" data-duration="{round(END + XF, 2)}" style="z-index:30">
        <div id="eR">{open("rtile.svg").read()}</div>
        <div id="eq" class="mono">AI receptionist for restaurants</div>
        <div id="esee-m"><span id="esee">Never miss<br />a call again.</span></div>
        <div id="eurl" class="mono">rezflo.ca</div>
        <div id="ebelow"><span>Fill out the form below</span><b>↓</b></div>
      </div>

      {"".join(f'<audio id="sfx-n{k}" src="sfx/tick.wav" data-start="{t}" data-duration="0.09" data-volume="0.22"></audio>' for k, (t, _) in enumerate(steps_js) if k)}
      <audio id="sfx-hook" src="sfx/switch.wav" data-start="0.12" data-duration="0.14" data-volume="0.22"></audio>
      <audio id="sfx-map" src="sfx/pop.wav" data-start="2.9" data-duration="0.17" data-volume="0.2"></audio>
      <audio id="sfx-text" src="sfx/success.wav" data-start="{T(225)}" data-duration="0.6" data-volume="0.22"></audio>
      <audio id="sfx-fill" src="sfx/fill.wav" data-start="{CLIP - 0.9:.2f}" data-duration="0.5" data-volume="0.2"></audio>
      <audio id="sfx-end" src="sfx/chime.wav" data-start="{CLIP - 0.25:.2f}" data-duration="0.95" data-volume="0.3"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const CAPS = {json.dumps(cap_js)};
      const STEPS = {json.dumps(steps_js)};
      const CLIP = {CLIP}, XF = {XF}, VPH = {VPH}, MAPH = {MAPH}, CH = {CH}, GY = {GY}, Y0 = {Y0};
      const AION = {{ opacity: 1, color: "#c4b9ff", textShadow: "0 0 22px rgba(143,123,255,0.95), 0 0 6px rgba(143,123,255,0.75), 0 4px 20px rgba(11,10,18,0.95)" }};
      const MEON = {{ opacity: 1, color: "#ffffff", textShadow: "0 0 18px rgba(255,255,255,0.5), 0 4px 20px rgba(11,10,18,0.95)" }};

      // camera: slow push-ins that hold
      tl.fromTo("#vw", {{ scale: 1 }}, {{ scale: 1.04, duration: {round(T(177) - 0.3, 2)}, ease: "none" }}, 0);
      tl.to("#vw", {{ scale: 1.08, duration: 2.2, ease: "sine.inOut" }}, {T(177)} - 0.3);
      tl.to("#vw", {{ scale: 1.13, duration: 2.2, ease: "sine.inOut" }}, {T(230)} - 0.3);

      // hook, then the map takes the top of the frame
      tl.fromTo("#hook .ln span", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.12 }}, 0.05);
      tl.to("#hook", {{ opacity: 0, y: -50, duration: 0.3, ease: "power3.in" }}, 2.6);
      tl.fromTo("#vp", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 2.85);
      tl.fromTo(".node", {{ scale: 0.85 }}, {{ scale: 1, duration: 0.45, ease: "back.out(1.6)", stagger: 0.03 }}, 2.85);

      // steps: active glows, done gets a tick, the arrow fills, the map pans to keep the active row in view
      const ACTIVE = {{ opacity: 1, scale: 1.06, borderColor: "#8f7bff", boxShadow: "0 0 0 2px rgba(143,123,255,0.35), 0 0 34px rgba(143,123,255,0.75), 0 16px 36px rgba(11,10,18,0.45)" }};
      const DONE = {{ opacity: 1, scale: 1, borderColor: "#3a3550", boxShadow: "0 16px 36px rgba(11,10,18,0.45)" }};
      let lastRow = -1;
      STEPS.forEach(([t0, row], k) => {{
        const t = Math.max(t0, k === 0 ? 3.0 : t0);
        const n = "#n" + k;
        if (k > 0) {{
          tl.to("#l" + (k - 1), {{ strokeDashoffset: 0, duration: 0.35, ease: "power2.inOut" }}, t - 0.35);
          tl.to("#n" + (k - 1), {{ ...DONE, duration: 0.3 }}, t - 0.05);
          tl.to("#n" + (k - 1) + " .tile", {{ backgroundColor: "#221e33", duration: 0.3 }}, t - 0.05);
          tl.fromTo("#n" + (k - 1) + " .tick", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)" }}, t - 0.05);
        }}
        tl.to(n, {{ ...ACTIVE, duration: 0.4, ease: "back.out(1.8)" }}, t);
        tl.to(n + " .tile", {{ backgroundColor: "#5b41da", duration: 0.3 }}, t);
        tl.to(n + " .tile svg", {{ stroke: "#ffffff", duration: 0.3 }}, t);
        tl.fromTo(n + " .d", {{ opacity: 0, y: 6 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, t + 0.5);
        if (row !== lastRow) {{
          const top = Math.min(row, {ROWS} - 2);           // active row on top, next row under it
          const ty = -(Y0 + top * (CH + GY)) + 8;
          tl.to("#map", {{ y: ty, duration: 0.8, ease: "power2.inOut" }}, Math.max(t - 0.6, 3.0));
          lastRow = row;
        }}
      }});
      // last step completes as the call wraps up
      tl.fromTo("#n{len(STEPS) - 1} .tick", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.4)" }}, {T(282)});

      // captions: chunk on/off, each word lights up as it is said
      CAPS.forEach(([k, a, b, ws]) => {{
        const el = document.getElementById("c" + k);
        tl.fromTo(el, {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, a);
        const on = el.classList.contains("ai") ? AION : MEON;
        el.querySelectorAll(".w").forEach((w, j) => tl.set(w, on, ws[j]));
        tl.set(el, {{ opacity: 0 }}, b);
      }});

      // end banner: dissolves in over the last moment, then the logo builds
      const E = CLIP - 0.25;
      tl.fromTo("#endc", {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: "sine.inOut" }}, CLIP - XF);
      tl.to("#vp, .cap", {{ opacity: 0, duration: XF * 0.6, ease: "power2.in" }}, CLIP - XF);
      tl.fromTo("#eR", {{ scale: 0.6, opacity: 0, y: 40 }}, {{ scale: 1, opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.3)" }}, E);
      tl.fromTo("#eR .lane-g", {{ x: 14, y: -14, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.34, ease: "expo.out" }}, E + 0.06);
      tl.fromTo("#eR .lane-p", {{ x: -14, y: 14, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.34, ease: "expo.out" }}, E + 0.11);
      tl.fromTo("#eR .slash-g, #eR .slash-p", {{ x: -22, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.26, ease: "back.out(2)", stagger: 0.05 }}, E + 0.3);
      tl.fromTo("#eq", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, E + 0.35);
      tl.fromTo("#esee", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out" }}, E + 0.55);
      tl.fromTo("#eurl", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, E + 0.9);
      tl.fromTo("#ebelow", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, E + 1.15);
      tl.fromTo("#ebelow b", {{ y: -4 }}, {{ y: 8, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 5, immediateRender: false }}, E + 1.45);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(page)
print(len(chunks), "caption chunks,", TOTAL, "s,", len(STEPS), "steps")
