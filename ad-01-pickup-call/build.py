# Builds index.html from transcript.json (word timings of clip.mp4) and clip.segs.json (cut points).
# Run: python3 cut.py … ; python3 music.py <clip> <end> ; python3 build.py ; npx hyperframes check / render
import json, html

SEGS = json.load(open("clip.segs.json"))
CLIP = SEGS[-1]["out"][1]                 # clip.mp4 length
END = 3.6                                 # end banner length
TOTAL = round(CLIP + END, 2)
CUTS = [s["out"][0] for s in SEGS[1:]]    # jump cuts in clip.mp4

FIX = {"Intalia.": "Antalya.", "donor": "doner", "donor,": "doner,"}
W = [w for s in json.load(open("transcript.json")) for w in s["words"]]
words = [{"w": FIX.get(w["w"].strip(), w["w"].strip()), "s": round(w["s"], 2), "e": round(w["e"], 2)} for w in W]
T = lambda i: words[i]["s"]               # start time of word i (indices from transcript.json)

# the caller (Sarah) says these word ranges; everything else is the AI
CALLER = [(10, 16), (26, 26), (37, 46), (68, 72), (84, 86), (104, 107), (137, 143)]
for i, w in enumerate(words):
    w["ai"] = not any(a <= i <= b for a, b in CALLER)

# AI talking ranges (drives the waveform)
AI, cur = [], None
for w in words:
    if not w["ai"]:
        if cur: AI.append(cur); cur = None
    elif cur and w["s"] - cur[1] < 0.6: cur[1] = w["e"]
    else:
        if cur: AI.append(cur)
        cur = [w["s"], w["e"]]
if cur: AI.append(cur)

# captions: 1 to 4 word chunks; break on speaker change, sentence end, pause, or length
chunks, cur = [], []
for w in words:
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

# key moments, synced to the spoken word
K = dict(
    name=T(19), sarah=T(26), doner=T(41), fries=T(45), itemsOut=T(47) + 0.2,
    soda=T(64), tea=T(66), sodaPick=T(72), drinkOut=T(73) - 0.1,
    onions=T(79), sauce=T(82), nope=T(84), modsOut=T(87) - 0.2,
    asap=T(95), specific=T(102), asapPick=T(104), pickOut=T(108) - 0.1,
    readback=T(119), rb1=T(125), rb2=T(128), rb3=T(131), correct=T(136), yeah=T(137),
    rbPunch=T(122), cool=T(140),
)
K = {k: round(v, 2) for k, v in K.items()}

ICON = {
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "wrap": '<path d="M6 3h12l-3.2 18H9.2z"/><path d="M7 8h10M7.8 13h8.4"/>',
    "fries": '<path d="M5 10h14l-2 11H7z"/><path d="M8 10V4M11 10V3M14 10V4M17 10V6"/>',
    "cup": '<path d="M6 7h12l-1.6 14H7.6z"/><path d="M5 7h14M13 7l2-5h3"/>',
    "tea": '<path d="M8 3h8c0 6-1.2 8-2.6 10v5H17v3H7v-3h3.6v-5C9.2 11 8 9 8 3z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
}
ic = lambda k: f'<svg class="ic" viewBox="0 0 24 24">{ICON[k]}</svg>'
RTILE = open("rtile.svg").read()

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
      :root {{ --ink: #0b0a12; --brand: #5b41da; --peri: #8f7bff; --green: #34c759; --cream: #f3efe6; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Inter", sans-serif; background: var(--ink); }}
      .clip {{ position: absolute; inset: 0; }}
      .mono {{ font-family: "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: 0.14em; }}

      #vw {{ position: absolute; inset: 0; transform-origin: 540px 820px; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #shade {{ position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(11,10,18,0.5) 0%, rgba(11,10,18,0.2) 24%, rgba(11,10,18,0) 36%, rgba(11,10,18,0) 52%, rgba(11,10,18,0.32) 66%, rgba(11,10,18,0.32) 78%, rgba(11,10,18,0) 100%); }}

      /* hook */
      #hook {{ position: absolute; left: 0; top: 300px; width: 1080px; text-align: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 104px; line-height: 1.02; letter-spacing: -0.03em; color: #fff; }}
      #hook .ln {{ display: block; overflow: hidden; padding: 0 0 8px; }}
      #hook .ln span {{ display: inline-block; text-shadow: 0 6px 30px rgba(11,10,18,0.75); }}
      #hook .ai {{ color: var(--peri); text-shadow: 0 0 26px rgba(143,123,255,0.85), 0 6px 30px rgba(11,10,18,0.75); }}

      /* "AI agent" card, under the captions at the start */
      #agent {{ position: absolute; left: 0; top: 1226px; width: 1080px; display: flex; flex-direction: column; align-items: center; gap: 22px; }}
      #acard {{ width: 600px; height: 172px; border-radius: 30px; background: rgba(11,10,18,0.82); border: 3px solid var(--peri);
        box-shadow: 0 0 30px rgba(143,123,255,0.65), inset 0 0 18px rgba(143,123,255,0.25); display: flex; flex-direction: column; justify-content: center; gap: 18px; padding: 0 40px; opacity: 0; }}
      #acard .row {{ display: flex; align-items: center; gap: 22px; }}
      #acard .dot {{ width: 22px; height: 22px; border-radius: 50%; background: var(--peri); box-shadow: 0 0 14px var(--peri); flex: none; }}
      #acard img {{ height: 50px; width: auto; }}
      #acard .lab {{ margin-left: auto; font-weight: 700; font-size: 40px; color: var(--peri); text-shadow: 0 0 16px rgba(143,123,255,0.8); }}
      #bars {{ display: flex; align-items: center; justify-content: center; gap: 7px; height: 52px; }}
      #bars i {{ display: block; width: 6px; height: 52px; border-radius: 3px; background: var(--peri); box-shadow: 0 0 8px rgba(143,123,255,0.8); transform: scaleY(0.16); }}
      #anote {{ font-weight: 700; font-size: 36px; line-height: 1.22; text-align: center; color: #fff; text-shadow: 0 0 14px rgba(255,255,255,0.35), 0 3px 16px rgba(11,10,18,0.95); opacity: 0; }}

      /* order review ticket (top, only during the read-back) */
      #tk {{ position: absolute; left: 230px; top: 140px; width: 620px; padding: 22px 30px 16px; border-radius: 30px; background: rgba(11,10,18,0.86);
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

      /* captions: bottom edge sits just above the pills */
      .cap {{ position: absolute; left: 110px; bottom: 712px; width: 860px; text-align: center; font-weight: 700; font-size: 60px; line-height: 1.1; letter-spacing: -0.01em; opacity: 0; }}
      .cap .w {{ display: inline-block; color: #fff; opacity: 0.7; text-shadow: 0 2px 0 rgba(11,10,18,0.45), 0 4px 20px rgba(11,10,18,0.95); }}

      /* pills, right under the captions */
      .chips {{ position: absolute; left: 90px; top: 1232px; width: 900px; display: flex; flex-wrap: wrap; justify-content: center; gap: 18px; }}
      .chip {{ position: relative; height: 82px; padding: 0 34px; border-radius: 999px; display: flex; align-items: center; gap: 14px; font-weight: 700; font-size: 36px; color: #fff; white-space: nowrap;
        background: rgba(11,10,18,0.8); border: 2.5px solid var(--peri); box-shadow: 0 0 20px rgba(143,123,255,0.5); opacity: 0; }}
      .chip .ic {{ position: relative; width: 38px; height: 38px; fill: none; stroke: #b9adff; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
      .chip .x {{ position: absolute; left: 26px; right: 26px; top: 50%; height: 4px; margin-top: -2px; border-radius: 2px; background: #fff; transform-origin: 0 50%; }}
      .chip .pick {{ position: absolute; inset: -3px; border-radius: 999px; background: var(--brand); border: 2.5px solid #b9adff; opacity: 0; }}
      .chip span {{ position: relative; }}
      #nmv i {{ font-style: normal; opacity: 0; }}
      #nm .cur {{ display: inline-block; width: 4px; height: 42px; margin-left: 4px; vertical-align: -6px; background: var(--peri); }}
      #nm .lab {{ color: var(--peri); font-weight: 400; margin-right: 12px; }}

      /* end banner (same family as the FAQ end cards) */
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
      <!-- the call (0 to {CLIP}s): cut-down clip.mp4 -->
      <div id="vw">
        <video id="src" class="clip" src="clip.mp4" data-start="0" data-duration="{CLIP}" data-has-audio="true" playsinline></video>
        <div id="shade"></div>
      </div>
      <audio id="music" src="music.wav" data-start="0" data-duration="{TOTAL}" data-volume="1"></audio>

      <div id="ov" class="clip" data-start="0" data-duration="{CLIP}" style="z-index:20">
        <div id="hook"><span class="ln"><span>Can you tell</span></span><span class="ln"><span>this is <b class="ai">AI?</b></span></span></div>

        <div id="agent">
          <div id="acard">
            <div class="row"><i class="dot"></i><img src="rezflo-logo-horizontal-on-dark.svg" alt="RezFlo" /><span class="lab">AI agent</span></div>
            <div id="bars">{"".join("<i></i>" for _ in range(22))}</div>
          </div>
          <div id="anote">Real conversation between<br />a caller and RezFlo AI</div>
        </div>

        <div id="tk">
          <div class="hd">
            <div><div class="t1">Order review</div><div class="t2 mono">Pickup · Name: Sarah</div></div>
            <div id="st"><div class="s live mono"><i></i>Live</div><div class="s done mono"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>Placed</div></div>
          </div>
          <div id="r1" class="tr"><span class="q mono">1 ×</span><span class="v">Chicken doner</span></div>
          <div id="r2" class="tr"><span class="q mono">1 ×</span><span class="v">Regular fries</span></div>
          <div id="r3" class="tr"><span class="q mono">1 ×</span><span class="v">Soda</span></div>
          <div id="r4" class="tr pk"><span class="q mono">◷</span><span class="v">Pickup · as soon as possible</span></div>
        </div>

        <div class="chips" id="cn"><div id="nm" class="chip">{ic("user")}<span><b class="lab">Name</b><b id="nmv">{"".join(f"<i>{c}</i>" for c in "Sarah")}</b><i class="cur"></i></span></div></div>
        <div class="chips" id="ci"><div id="i1" class="chip">{ic("wrap")}<span>Chicken doner</span></div><div id="i2" class="chip">{ic("fries")}<span>Regular fries</span></div></div>
        <div class="chips" id="cd"><div id="d1" class="chip"><i class="pick"></i>{ic("cup")}<span>Soda</span></div><div id="d2" class="chip">{ic("tea")}<span>Turkish tea</span></div></div>
        <div class="chips" id="cc"><div id="m1" class="chip"><span>No onions</span><i class="x"></i></div><div id="m2" class="chip"><span>Extra sauce</span><i class="x"></i></div></div>
        <div class="chips" id="cp"><div id="p1" class="chip"><i class="pick"></i>{ic("clock")}<span>As soon as possible</span></div><div id="p2" class="chip">{ic("clock")}<span>Specific time</span></div></div>

        {(chr(10) + "        ").join(cap_html)}
      </div>

      <!-- end banner ({CLIP} to {TOTAL}s) -->
      <div id="endc" class="clip" data-start="{CLIP}" data-duration="{END}" style="z-index:30">
        <div id="eR">{RTILE}</div>
        <div id="eq" class="mono">AI receptionist for restaurants</div>
        <div id="esee-m"><span id="esee">Never miss<br />a call again.</span></div>
        <div id="eurl" class="mono">rezflo.ca</div>
        <div id="ebelow"><span>Fill out the form below</span><b>↓</b></div>
      </div>

      <audio id="sfx-hook" src="sfx/switch.wav" data-start="0.12" data-duration="0.14" data-volume="0.25"></audio>
      <audio id="sfx-card" src="sfx/pop.wav" data-start="0.35" data-duration="0.17" data-volume="0.22"></audio>
      <audio id="sfx-nm" src="sfx/pop.wav" data-start="{K['name']}" data-duration="0.17" data-volume="0.2"></audio>
      <audio id="sfx-sarah" src="sfx/tick.wav" data-start="{K['sarah']}" data-duration="0.09" data-volume="0.3"></audio>
      <audio id="sfx-i1" src="sfx/pop.wav" data-start="{K['doner']}" data-duration="0.17" data-volume="0.2"></audio>
      <audio id="sfx-i2" src="sfx/pop.wav" data-start="{K['fries']}" data-duration="0.17" data-volume="0.2"></audio>
      <audio id="sfx-d1" src="sfx/pop.wav" data-start="{K['soda']}" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-d2" src="sfx/pop.wav" data-start="{K['tea']}" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-dp" src="sfx/tick.wav" data-start="{K['sodaPick']}" data-duration="0.09" data-volume="0.3"></audio>
      <audio id="sfx-m1" src="sfx/pop.wav" data-start="{K['onions']}" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-m2" src="sfx/pop.wav" data-start="{K['sauce']}" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-mx" src="sfx/snap.wav" data-start="{K['nope']}" data-duration="0.16" data-volume="0.25"></audio>
      <audio id="sfx-p1" src="sfx/pop.wav" data-start="{K['asap']}" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-p2" src="sfx/pop.wav" data-start="{K['specific']}" data-duration="0.17" data-volume="0.18"></audio>
      <audio id="sfx-pp" src="sfx/tick.wav" data-start="{K['asapPick']}" data-duration="0.09" data-volume="0.3"></audio>
      <audio id="sfx-tk" src="sfx/fill.wav" data-start="{K['readback']}" data-duration="0.5" data-volume="0.16"></audio>
      <audio id="sfx-rb1" src="sfx/tick.wav" data-start="{K['rb1']}" data-duration="0.09" data-volume="0.25"></audio>
      <audio id="sfx-rb2" src="sfx/tick.wav" data-start="{K['rb2']}" data-duration="0.09" data-volume="0.25"></audio>
      <audio id="sfx-rb3" src="sfx/tick.wav" data-start="{K['rb3']}" data-duration="0.09" data-volume="0.25"></audio>
      <audio id="sfx-ok" src="sfx/success.wav" data-start="{K['yeah']}" data-duration="0.6" data-volume="0.3"></audio>
      <audio id="sfx-fill" src="sfx/fill.wav" data-start="{CLIP - 0.42:.2f}" data-duration="0.5" data-volume="0.2"></audio>
      <audio id="sfx-end" src="sfx/chime.wav" data-start="{CLIP + 0.07:.2f}" data-duration="0.95" data-volume="0.3"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const K = {json.dumps(K)};
      const CAPS = {json.dumps(cap_js)};
      const AI = {json.dumps(AI)};
      const CUTS = {json.dumps(CUTS)};
      const CLIP = {CLIP};
      const AION = {{ opacity: 1, color: "#c4b9ff", textShadow: "0 0 22px rgba(143,123,255,0.95), 0 0 6px rgba(143,123,255,0.75), 0 4px 20px rgba(11,10,18,0.95)" }};
      const MEON = {{ opacity: 1, color: "#ffffff", textShadow: "0 0 18px rgba(255,255,255,0.5), 0 4px 20px rgba(11,10,18,0.95)" }};
      const chipIn = (sel, t) => tl.fromTo(sel, {{ opacity: 0, y: 24, scale: 0.86 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(1.6)" }}, t);
      const chipsOut = (sel, t) => tl.to(sel, {{ opacity: 0, y: -14, scale: 0.94, duration: 0.25, ease: "power3.in", stagger: 0.04 }}, t);
      const pick = (sel, t) => {{ tl.to(sel + " .pick", {{ opacity: 1, duration: 0.15 }}, t); tl.fromTo(sel, {{ scale: 1 }}, {{ scale: 1.1, duration: 0.14, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, t); }};
      const flash = (sel, t) => tl.fromTo(sel, {{ color: "#ffffff" }}, {{ color: "#c4b9ff", duration: 0.14, yoyo: true, repeat: 1, immediateRender: false }}, t);

      // jump cuts: alternate framing so each cut reads as a new angle
      CUTS.forEach((t, k) => tl.set("#vw", {{ scale: k % 2 === 0 ? 1.07 : 1 }}, t));
      tl.fromTo("#vw", {{ scale: 1.0 }}, {{ scale: 1.08, duration: 0.35, ease: "power3.out", immediateRender: false }}, K.rbPunch);
      tl.fromTo("#vw", {{ scale: 1.0 }}, {{ scale: 1.08, duration: 0.3, ease: "power3.out", immediateRender: false }}, K.cool);

      // hook (under 3s)
      tl.fromTo("#hook .ln span", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.12 }}, 0.05);
      tl.to("#hook", {{ opacity: 0, y: -50, duration: 0.3, ease: "power3.in" }}, 2.8);

      // "AI agent" card under the captions, then it clears for the pills
      tl.fromTo("#acard", {{ opacity: 0, y: 30, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.5)" }}, 0.3);
      tl.fromTo("#anote", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0.55);
      tl.to("#acard .dot", {{ opacity: 0.35, duration: 0.45, yoyo: true, repeat: 5, ease: "sine.inOut" }}, 0.7);
      tl.to("#agent > *", {{ opacity: 0, y: -16, duration: 0.3, ease: "power3.in", stagger: 0.05 }}, K.name - 0.55);

      // waveform moves while the AI talks (fixed pattern, so every render is identical)
      const H = [0.5, 0.85, 0.35, 1, 0.6, 0.9, 0.3, 0.75, 0.45, 0.95, 0.55];
      const bars = document.querySelectorAll("#bars i");
      AI.forEach(([a, b]) => {{
        if (a > K.name) return;
        for (let t = a, n = 0; t < b; t += 0.12, n++) {{
          bars.forEach((el, j) => tl.to(el, {{ scaleY: 0.18 + 0.82 * H[(j * 3 + n * 5) % 11] * (0.55 + 0.45 * ((n + j) % 4) / 3), duration: 0.11, ease: "sine.inOut" }}, t));
        }}
        tl.to(bars, {{ scaleY: 0.16, duration: 0.15 }}, b);
      }});

      // captions: chunk on/off, each word lights up as it is said
      CAPS.forEach(([k, a, b, ws]) => {{
        const el = document.getElementById("c" + k);
        tl.fromTo(el, {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, a);
        const on = el.classList.contains("ai") ? AION : MEON;
        el.querySelectorAll(".w").forEach((w, j) => tl.set(w, on, ws[j]));
        tl.set(el, {{ opacity: 0 }}, b);
      }});

      // name: chip with a cursor on "name", "Sarah" types in when she says it
      chipIn("#nm", K.name);
      tl.to("#nm .cur", {{ opacity: 0, duration: 0.25, yoyo: true, repeat: 5, ease: "steps(1)" }}, K.name + 0.1);
      document.querySelectorAll("#nmv i").forEach((el, j) => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, immediateRender: false }}, K.sarah + j * 0.06));
      chipsOut("#nm", K.sarah + 1.3);

      // her order: items pop up as she says them
      chipIn("#i1", K.doner); chipIn("#i2", K.fries);
      chipsOut("#ci .chip", K.itemsOut);

      // drink
      chipIn("#d1", K.soda); chipIn("#d2", K.tea);
      pick("#d1", K.sodaPick);
      tl.to("#d2", {{ opacity: 0.25, duration: 0.2 }}, K.sodaPick);
      chipsOut("#cd .chip", K.drinkOut);

      // changes: crossed out on "Nope"
      chipIn("#m1", K.onions); chipIn("#m2", K.sauce);
      tl.fromTo("#cc .x", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power3.out", stagger: 0.08 }}, K.nope);
      tl.to("#cc .chip", {{ opacity: 0.45, duration: 0.2 }}, K.nope + 0.2);
      chipsOut("#cc .chip", K.modsOut);

      // pickup time
      chipIn("#p1", K.asap); chipIn("#p2", K.specific);
      pick("#p1", K.asapPick);
      tl.to("#p2", {{ opacity: 0.25, duration: 0.2 }}, K.asapPick);
      chipsOut("#cp .chip", K.pickOut);

      // order review: ticket drops in on "read that back", rows light up as they're read
      tl.fromTo("#tk", {{ opacity: 0, y: -40, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.4)" }}, K.readback);
      tl.fromTo(".tr", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.28, ease: "power3.out", stagger: 0.09 }}, K.readback + 0.25);
      flash("#r1 .v", K.rb1); flash("#r2 .v", K.rb2); flash("#r3 .v", K.rb3);
      tl.fromTo("#tk", {{ scale: 1 }}, {{ scale: 1.035, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, K.correct);
      tl.to("#st .live", {{ opacity: 0, duration: 0.15 }}, K.yeah);
      tl.fromTo("#st .done", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)" }}, K.yeah);
      tl.to("#tk", {{ borderColor: "#34c759", boxShadow: "0 0 30px rgba(52,199,89,0.55), 0 24px 60px rgba(11,10,18,0.5)", duration: 0.3 }}, K.yeah);

      // end banner
      tl.fromTo("#eR", {{ scale: 0.6, opacity: 0, y: 40 }}, {{ scale: 1, opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.3)" }}, CLIP + 0.05);
      tl.fromTo("#eR .lane-g", {{ x: 14, y: -14, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.34, ease: "expo.out" }}, CLIP + 0.11);
      tl.fromTo("#eR .lane-p", {{ x: -14, y: 14, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.34, ease: "expo.out" }}, CLIP + 0.16);
      tl.fromTo("#eR .slash-g, #eR .slash-p", {{ x: -22, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.26, ease: "back.out(2)", stagger: 0.05 }}, CLIP + 0.35);
      tl.fromTo("#eq", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, CLIP + 0.4);
      tl.fromTo("#esee", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out" }}, CLIP + 0.6);
      tl.fromTo("#eurl", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, CLIP + 0.95);
      tl.fromTo("#ebelow", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, CLIP + 1.2);
      tl.fromTo("#ebelow b", {{ y: -4 }}, {{ y: 8, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 5, immediateRender: false }}, CLIP + 1.5);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(page)
print(len(chunks), "caption chunks,", TOTAL, "s, AI ranges", len(AI))
