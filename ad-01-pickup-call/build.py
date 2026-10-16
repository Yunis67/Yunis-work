# Builds index.html from transcript.json (word timings of clip.mp4).
# Run: python3 build.py   (then npx hyperframes check / render)
import json, html

CLIP = 45.22          # clip.mp4 length
END = 3.4             # end card length
TOTAL = round(CLIP + END, 2)
CUTS = [4.82, 5.32, 7.84, 10.68, 13.76, 19.36, 20.66, 26.28, 32.68, 35.02, 36.1, 39.98, 43.04]  # jump cuts in clip.mp4

# who is talking (clip.mp4 time ranges); everything else is the caller (Sarah)
AI = [(0, 2.9), (4.85, 7.2), (7.98, 10.8), (14.0, 19.55), (21.0, 25.0), (26.4, 31.6), (33.0, 41.9)]
FIX = {"Intalia.": "Antalya.", "donor": "doner", "donor,": "doner,", "fry?": "fries?"}

words = []
for s in json.load(open("transcript.json")):
    for w in s["words"]:
        t = w["w"].strip()
        words.append({"w": FIX.get(t, t), "s": round(w["s"], 2), "e": round(w["e"], 2)})
for w in words:
    w["ai"] = any(a <= w["s"] < b for a, b in AI)

# group into 1 to 4 word chunks: break on speaker change, sentence end, gap, or length
chunks, cur = [], []
for i, w in enumerate(words):
    if cur and (w["ai"] != cur[-1]["ai"] or w["s"] - cur[-1]["e"] > 0.35 or len(cur) >= 4
                or cur[-1]["w"][-1] in ".?!" or (cur[-1]["w"][-1] == "," and len(cur) >= 2)):
        chunks.append(cur); cur = []
    cur.append(w)
chunks.append(cur)

cap_html, cap_js = [], []
for k, c in enumerate(chunks):
    start = round(c[0]["s"] - 0.06, 2)
    nxt = chunks[k + 1][0]["s"] - 0.06 if k + 1 < len(chunks) else CLIP
    end = round(min(nxt, c[-1]["e"] + 0.45), 2)
    cls = "cap ai" if c[0]["ai"] else "cap me"
    spans = "".join(f'<span class="w">{html.escape(w["w"])}</span> ' for w in c).strip()
    cap_html.append(f'<div id="c{k}" class="{cls}">{spans}</div>')
    cap_js.append([k, start, end, [w["s"] for w in c]])

# waveform: bars move only while the AI is talking
wave_js = [[a, b] for a, b in AI]

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
      :root {{ --ink: #0b0a12; --glow: #1d1638; --brand: #5b41da; --peri: #8f7bff; --green: #34c759; --cream: #f3efe6; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Inter", sans-serif; background: var(--ink); }}
      .clip {{ position: absolute; inset: 0; }}
      .mono {{ font-family: "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: 0.14em; }}

      #vw {{ position: absolute; inset: 0; transform-origin: 540px 820px; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #shade {{ position: absolute; inset: 0; pointer-events: none;
        background: linear-gradient(180deg, rgba(11,10,18,0.62) 0%, rgba(11,10,18,0.38) 26%, rgba(11,10,18,0) 40%, rgba(11,10,18,0) 70%, rgba(11,10,18,0.3) 100%); }}

      /* hook */
      #hook {{ position: absolute; left: 0; top: 300px; width: 1080px; text-align: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 104px; line-height: 1.02; letter-spacing: -0.03em; color: #fff; }}
      #hook .ln {{ display: block; overflow: hidden; padding: 0 0 8px; }}
      #hook .ln span {{ display: inline-block; text-shadow: 0 6px 30px rgba(11,10,18,0.75); }}
      #hook .ai {{ color: var(--peri); text-shadow: 0 0 26px rgba(143,123,255,0.85), 0 6px 30px rgba(11,10,18,0.75); }}

      /* AI badge (top) */
      #badge {{ position: absolute; left: 0; top: 118px; width: 1080px; display: flex; flex-direction: column; align-items: center; gap: 14px; opacity: 0; }}
      #pill {{ display: flex; align-items: center; gap: 18px; height: 78px; padding: 0 30px; border-radius: 999px; background: rgba(11,10,18,0.8);
        border: 2.5px solid var(--peri); box-shadow: 0 0 22px rgba(143,123,255,0.55), inset 0 0 14px rgba(143,123,255,0.25); }}
      #pill .dot {{ width: 16px; height: 16px; border-radius: 50%; background: var(--peri); box-shadow: 0 0 12px var(--peri); }}
      #pill .lbl {{ font-size: 24px; color: #fff; }}
      #bars {{ display: flex; align-items: center; gap: 6px; height: 40px; }}
      #bars i {{ display: block; width: 6px; height: 40px; border-radius: 3px; background: var(--peri); transform: scaleY(0.18); }}
      #sub {{ font-size: 25px; color: rgba(255,255,255,0.86); text-shadow: 0 2px 12px rgba(11,10,18,0.9); }}

      /* live order ticket (ceiling area, above her head) */
      #tk {{ position: absolute; left: 230px; top: 278px; width: 620px; padding: 22px 30px 18px; border-radius: 30px; background: rgba(11,10,18,0.84);
        border: 2.5px solid var(--peri); box-shadow: 0 0 26px rgba(143,123,255,0.5), 0 24px 60px rgba(11,10,18,0.5); opacity: 0; }}
      #tk .hd {{ display: flex; align-items: center; justify-content: space-between; padding-bottom: 14px; border-bottom: 2px solid rgba(143,123,255,0.3); }}
      #tk .t1 {{ font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 38px; color: #fff; letter-spacing: -0.01em; }}
      #tk .t2 {{ font-size: 19px; color: var(--peri); margin-top: 6px; }}
      #st {{ position: relative; width: 196px; height: 46px; }}
      #st .s {{ position: absolute; right: 0; top: 0; height: 46px; display: flex; align-items: center; gap: 10px; padding: 0 16px; border-radius: 999px; font-size: 19px; white-space: nowrap; }}
      #st .live {{ color: var(--peri); border: 2px solid rgba(143,123,255,0.6); }}
      #st .live i {{ width: 11px; height: 11px; border-radius: 50%; background: var(--peri); }}
      #st .done {{ color: #fff; background: var(--green); opacity: 0; }}
      #st .done svg {{ width: 22px; height: 22px; }}
      .tr {{ display: flex; align-items: center; gap: 18px; height: 56px; font-size: 32px; color: #fff; opacity: 0; }}
      .tr:first-of-type {{ margin-top: 8px; }}
      .tr .q {{ width: 64px; font-size: 22px; color: var(--peri); }}
      .tr .v {{ font-weight: 700; white-space: nowrap; }}
      .tr.pk .v {{ font-weight: 400; color: rgba(255,255,255,0.85); }}

      /* captions (under her face) */
      .cap {{ position: absolute; left: 110px; top: 1090px; width: 860px; text-align: center; font-weight: 700; font-size: 70px; line-height: 1.08; letter-spacing: -0.01em; opacity: 0; }}
      .cap .w {{ display: inline-block; opacity: 0.4; color: #fff; text-shadow: 0 4px 18px rgba(11,10,18,0.85); }}
      .cap.ai .w.on {{ opacity: 1; color: #b9adff; text-shadow: 0 0 22px rgba(143,123,255,0.95), 0 0 6px rgba(143,123,255,0.7), 0 4px 18px rgba(11,10,18,0.85); }}
      .cap.me .w.on {{ opacity: 1; color: #fff; text-shadow: 0 0 20px rgba(255,255,255,0.55), 0 4px 18px rgba(11,10,18,0.9); }}

      /* option chips (over her chest) */
      .chips {{ position: absolute; left: 110px; top: 1290px; width: 860px; display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
      .chip {{ position: relative; height: 84px; padding: 0 36px; border-radius: 999px; display: flex; align-items: center; font-weight: 700; font-size: 38px; color: #fff; white-space: nowrap;
        background: rgba(11,10,18,0.8); border: 2.5px solid var(--peri); box-shadow: 0 0 20px rgba(143,123,255,0.5); opacity: 0; }}
      .chip .x {{ position: absolute; left: 26px; right: 26px; top: 50%; height: 4px; margin-top: -2px; border-radius: 2px; background: #fff; transform-origin: 0 50%; }}
      .chip .pick {{ position: absolute; inset: -3px; border-radius: 999px; background: var(--brand); border: 2.5px solid #b9adff; opacity: 0; }}
      .chip span {{ position: relative; }}
      #nm .cur {{ display: inline-block; width: 4px; height: 44px; margin-left: 4px; vertical-align: -6px; background: var(--peri); }}
      #nmv i {{ font-style: normal; opacity: 0; }}
      #nm .lab {{ color: var(--peri); font-weight: 400; margin-right: 14px; }}

      /* end card */
      #endc {{ position: absolute; inset: 0; background: radial-gradient(ellipse 760px 900px at 50% 46%, var(--glow) 0%, var(--ink) 72%); }}
      #elogo {{ position: absolute; left: 395px; top: 470px; width: 290px; height: 358px; }}
      #eh {{ position: absolute; left: 0; top: 930px; width: 1080px; text-align: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 84px; line-height: 1.05; letter-spacing: -0.03em; color: #fff; }}
      #eh .ln {{ display: block; overflow: hidden; padding-bottom: 12px; }}
      #eh .ln span {{ display: inline-block; }}
      #eh .p {{ color: var(--peri); }}
      #ecta {{ position: absolute; left: 190px; top: 1200px; width: 700px; height: 112px; border-radius: 999px; background: var(--brand); display: flex; align-items: center; justify-content: center; gap: 16px;
        font-weight: 700; font-size: 42px; color: #fff; box-shadow: 0 0 40px rgba(91,65,218,0.6); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <!-- the call (0 to {CLIP}s): cut-down clip.mp4 -->
      <div id="vw">
        <video id="src" class="clip" src="clip.mp4" data-start="0" data-duration="{CLIP}" data-has-audio="true" playsinline></video>
        <div id="shade"></div>
      </div>

      <div id="ov" class="clip" data-start="0" data-duration="{CLIP}" style="z-index:20">
        <!-- hook 0 to 3s -->
        <div id="hook"><span class="ln"><span>Can you tell</span></span><span class="ln"><span>this is <b class="ai">AI?</b></span></span></div>

        <div id="badge">
          <div id="pill"><i class="dot"></i><span class="lbl mono">RezFlo AI receptionist</span><div id="bars">{"".join("<i></i>" for _ in range(9))}</div></div>
          <div id="sub">Real call to RezFlo's AI · pauses trimmed</div>
        </div>

        <div id="tk">
          <div class="hd">
            <div><div class="t1">Pickup order</div><div class="t2 mono">Antalya · Name: Sarah</div></div>
            <div id="st"><div class="s live mono"><i></i>Live</div><div class="s done mono"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>Placed</div></div>
          </div>
          <div id="r1" class="tr"><span class="q mono">1 ×</span><span class="v">Chicken doner</span></div>
          <div id="r2" class="tr"><span class="q mono">1 ×</span><span class="v">Regular fries</span></div>
          <div id="r3" class="tr"><span class="q mono">1 ×</span><span class="v">Soda</span></div>
          <div id="r4" class="tr pk"><span class="q mono">◷</span><span class="v">Pickup · as soon as possible</span></div>
        </div>

        <div class="chips" id="cn"><div id="nm" class="chip"><span><b class="lab">Name</b><b id="nmv">{"".join(f"<i>{c}</i>" for c in "Sarah")}</b><i class="cur"></i></span></div></div>
        <div class="chips" id="cd"><div id="d1" class="chip"><i class="pick"></i><span>Soda</span></div><div id="d2" class="chip"><span>Turkish tea</span></div></div>
        <div class="chips" id="cc"><div id="m1" class="chip"><span>No onions</span><i class="x"></i></div><div id="m2" class="chip"><span>Extra sauce</span><i class="x"></i></div></div>
        <div class="chips" id="cp"><div id="p1" class="chip"><i class="pick"></i><span>As soon as possible</span></div><div id="p2" class="chip"><span>Specific time</span></div></div>

        {chr(10).join("        " + h for h in cap_html).strip()}
      </div>

      <!-- end card ({CLIP} to {TOTAL}s) -->
      <div id="endc" class="clip" data-start="{CLIP}" data-duration="{END}" style="z-index:30">
        <img id="elogo" src="rezflo-logo-on-dark.svg" alt="RezFlo" />
        <div id="eh"><span class="ln"><span>Every call answered.</span></span><span class="ln"><span class="p">Every order taken.</span></span></div>
        <div id="ecta"><span>Fill out the form below</span><b>↓</b></div>
      </div>

      <audio id="sfx-hook" src="sfx/switch.wav" data-start="0.12" data-duration="0.14" data-volume="0.25"></audio>
      <audio id="sfx-badge" src="sfx/pop.wav" data-start="3.0" data-duration="0.17" data-volume="0.2"></audio>
      <audio id="sfx-nm" src="sfx/pop.wav" data-start="5.9" data-duration="0.17" data-volume="0.2"></audio>
      <audio id="sfx-tk" src="sfx/pop.wav" data-start="8.05" data-duration="0.17" data-volume="0.22"></audio>
      <audio id="sfx-r1" src="sfx/tick.wav" data-start="11.95" data-duration="0.09" data-volume="0.3"></audio>
      <audio id="sfx-r2" src="sfx/tick.wav" data-start="13.25" data-duration="0.09" data-volume="0.3"></audio>
      <audio id="sfx-d1" src="sfx/pop.wav" data-start="18.0" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-d2" src="sfx/pop.wav" data-start="18.7" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-r3" src="sfx/tick.wav" data-start="20.6" data-duration="0.09" data-volume="0.3"></audio>
      <audio id="sfx-m1" src="sfx/pop.wav" data-start="22.9" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-m2" src="sfx/pop.wav" data-start="24.1" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-mx" src="sfx/snap.wav" data-start="25.55" data-duration="0.16" data-volume="0.25"></audio>
      <audio id="sfx-p1" src="sfx/pop.wav" data-start="29.1" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-p2" src="sfx/pop.wav" data-start="30.8" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-r4" src="sfx/tick.wav" data-start="32.3" data-duration="0.09" data-volume="0.3"></audio>
      <audio id="sfx-ok" src="sfx/success.wav" data-start="42.3" data-duration="0.6" data-volume="0.3"></audio>
      <audio id="sfx-end" src="sfx/chime.wav" data-start="{CLIP + 0.1:.2f}" data-duration="0.8" data-volume="0.3"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const CAPS = {json.dumps(cap_js)};
      const WAVE = {json.dumps(wave_js)};
      const CUTS = {json.dumps(CUTS)};
      const AION = {{ opacity: 1, color: "#b9adff", textShadow: "0 0 22px rgba(143,123,255,0.95), 0 0 6px rgba(143,123,255,0.7), 0 4px 18px rgba(11,10,18,0.85)" }};
      const MEON = {{ opacity: 1, color: "#ffffff", textShadow: "0 0 20px rgba(255,255,255,0.55), 0 4px 18px rgba(11,10,18,0.9)" }};
      const chipIn = (sel, t) => tl.fromTo(sel, {{ opacity: 0, y: 26, scale: 0.86 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(1.6)" }}, t);
      const chipsOut = (sel, t) => tl.to(sel, {{ opacity: 0, y: -16, scale: 0.94, duration: 0.25, ease: "power3.in", stagger: 0.04 }}, t);
      const pick = (sel, t) => {{ tl.to(sel + " .pick", {{ opacity: 1, duration: 0.15 }}, t); tl.fromTo(sel, {{ scale: 1 }}, {{ scale: 1.1, duration: 0.14, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, t); }};
      const rowIn = (sel, t) => tl.fromTo(sel, {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }}, t);
      const flash = (sel, t) => tl.fromTo(sel, {{ color: "#ffffff" }}, {{ color: "#b9adff", duration: 0.12, yoyo: true, repeat: 1, immediateRender: false }}, t);

      // jump cuts: alternate framing so each cut reads as a new angle
      CUTS.forEach((t, k) => tl.set("#vw", {{ scale: k % 2 === 0 ? 1.07 : 1 }}, t));
      // punch-ins on the key lines
      tl.fromTo("#vw", {{ scale: 1.07 }}, {{ scale: 1.12, duration: 0.35, ease: "power3.out", immediateRender: false }}, 36.6);
      tl.fromTo("#vw", {{ scale: 1.0 }}, {{ scale: 1.08, duration: 0.3, ease: "power3.out", immediateRender: false }}, 43.1);

      // hook (under 3s) → shrinks into the AI badge
      tl.fromTo("#hook .ln span", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.12 }}, 0.05);
      tl.to("#hook", {{ opacity: 0, y: -60, scale: 0.8, duration: 0.3, ease: "power3.in" }}, 2.75);
      tl.fromTo("#badge", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 3.0);
      tl.to("#pill .dot", {{ opacity: 0.35, duration: 0.5, yoyo: true, repeat: 41, ease: "sine.inOut" }}, 3.0);

      // waveform moves while the AI talks (fixed pattern, so every render is identical)
      const H = [0.55, 0.9, 0.4, 1, 0.65, 0.85, 0.35, 0.75, 0.5];
      WAVE.forEach(([a, b]) => {{
        for (let t = Math.max(a, 3.0), n = 0; t < b; t += 0.14, n++) {{
          document.querySelectorAll("#bars i").forEach((el, j) => tl.to(el, {{ scaleY: 0.2 + 0.8 * H[(j + n * 4) % 9] * (0.6 + 0.4 * ((n + j) % 3) / 2), duration: 0.13, ease: "sine.inOut" }}, t));
        }}
        tl.to("#bars i", {{ scaleY: 0.18, duration: 0.15 }}, b);
      }});

      // captions: chunk on/off, each word lights up as it is said
      CAPS.forEach(([k, a, b, ws]) => {{
        const el = document.getElementById("c" + k);
        tl.fromTo(el, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, a);
        const on = el.classList.contains("ai") ? AION : MEON;
        el.querySelectorAll(".w").forEach((w, j) => tl.set(w, on, ws[j]));
        tl.set(el, {{ opacity: 0 }}, b);
      }});

      // name: "What name…" 5.42 → chip with a cursor, "Sarah" 7.56 types in
      chipIn("#nm", 5.9);
      tl.to("#nm .cur", {{ opacity: 0, duration: 0.25, yoyo: true, repeat: 5, ease: "steps(1)" }}, 6.0);
      document.querySelectorAll("#nmv i").forEach((el, j) => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, immediateRender: false }}, 7.56 + j * 0.06));
      chipsOut("#nm", 8.6);

      // ticket: opens on "Perfect, Sarah" 8.02, items as she says them
      tl.fromTo("#tk", {{ opacity: 0, y: -30, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.4)" }}, 8.05);
      rowIn("#r1", 11.9);   // "chicken doner"
      rowIn("#r2", 13.2);   // "regular fries"

      // drink: "soda" 18.02, "Turkish tea" 18.72, "I'll get a soda" 20.56
      chipIn("#d1", 18.0); chipIn("#d2", 18.7);
      pick("#d1", 20.5);
      tl.to("#d2", {{ opacity: 0.25, duration: 0.2 }}, 20.5);
      rowIn("#r3", 20.6);
      chipsOut("#cd .chip", 21.25);

      // changes: "no onions" 22.90, "extra sauce" 24.12, "Nope" 25.54 → crossed out
      chipIn("#m1", 22.9); chipIn("#m2", 24.1);
      tl.fromTo("#cc .x", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power3.out", stagger: 0.08 }}, 25.55);
      tl.to("#cc .chip", {{ opacity: 0.45, duration: 0.2 }}, 25.75);
      chipsOut("#cc .chip", 26.6);

      // pickup time: "as soon as possible" 29.10, "specific time" 30.82, answer 31.78
      chipIn("#p1", 29.1); chipIn("#p2", 30.8);
      pick("#p1", 31.8);
      tl.to("#p2", {{ opacity: 0.25, duration: 0.2 }}, 31.8);
      rowIn("#r4", 32.3);
      chipsOut("#cp .chip", 33.1);

      // read-back: rows light up on each item, ticket pulses on "correct?"
      flash("#r1 .v", 37.4); flash("#r2 .v", 38.6); flash("#r3 .v", 39.8);
      tl.fromTo("#tk", {{ scale: 1 }}, {{ scale: 1.035, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, 41.4);

      // "Yeah, that's perfect" 42.26 → order placed
      tl.to("#st .live", {{ opacity: 0, duration: 0.15 }}, 42.3);
      tl.fromTo("#st .done", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)" }}, 42.3);
      tl.to("#tk", {{ borderColor: "#34c759", boxShadow: "0 0 30px rgba(52,199,89,0.55), 0 24px 60px rgba(11,10,18,0.5)", duration: 0.3 }}, 42.3);

      // end card
      tl.fromTo("#endc", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {CLIP});
      tl.fromTo("#elogo", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)" }}, {CLIP + 0.1:.2f});
      tl.fromTo("#eh .ln span", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.14 }}, {CLIP + 0.35:.2f});
      tl.fromTo("#ecta", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {CLIP + 0.85:.2f});
      tl.to("#ecta b", {{ y: 8, duration: 0.35, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {CLIP + 1.2:.2f});

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(page)
print(len(chunks), "caption chunks,", TOTAL, "s")
