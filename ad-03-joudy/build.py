# Builds index.html for the Joudy pickup-call ad, in the same style as ad-01 (Sarah).
# Inputs: clip-words.json (word timings of clip.mp4) and clip.segs.json (cut points), both from cut.py + transcribe.py.
# Run: python3 build.py [preview seconds] ; npx hyperframes check ; npx hyperframes render
# With a preview length, the composition stops there (no end card) so a first section can be reviewed.
import json, html, sys

SEGS = json.load(open("clip.segs.json"))
CLIP = SEGS[-1]["out"][1]                 # clip.mp4 length
PREVIEW = float(sys.argv[1]) if len(sys.argv) > 1 else None
END = 3.6                                 # end banner length (fully on screen)
XF = 0.7                                  # dissolve from the call into the banner
TOTAL = round(PREVIEW if PREVIEW else CLIP + END, 2)
VID = round(min(CLIP, TOTAL), 2)
INTRO = SEGS[1]["out"][0]                 # end of the cold open; the call starts here
# where a chunk of the call was removed (phone number, the AI's stall, the number read-back): soft flash
JUMPS = [SEGS[k]["out"][0] for k in (5, 7, 20)]

# who is talking: segment k>=1 is span k-1 in cut.py; these spans are the AI (21 opens with the AI's "Thank you.")
AI_SPANS = {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 19}
raw = json.load(open("clip-words.json"))
seg_of = lambda t: min(range(len(SEGS)), key=lambda k: 0 if SEGS[k]["out"][0] <= t < SEGS[k]["out"][1] else min(abs(t - SEGS[k]["out"][0]), abs(t - SEGS[k]["out"][1])))
words = []
for i, w in enumerate(raw):
    k = seg_of((w["s"] + w["e"]) / 2)
    ai = k >= 1 and (k - 1 in AI_SPANS or (k - 1 == 21 and w["w"].lower().startswith(("thank", "you!", "you."))))
    words.append({"w": w["w"], "s": w["s"], "e": w["e"], "ai": ai, "i": i})
# caption text: keep the restaurant (and agent) name off screen; fix what speech-to-text misheard
DROP = {10, 11, 12, 231, 232}             # "Alabasha Original." "Siri,"  and a misheard "You're welcome."
FIX = {9: "calling!", 13: "How", 167: "that"}
for w in words:
    w["w"] = FIX.get(w["i"], w["w"])
cwords = [w for w in words if w["i"] not in DROP and w["s"] < TOTAL - 0.2]
T = lambda i: raw[i]["s"]                 # start time of word i in clip.mp4

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
for w in cwords:
    if cur and (w["ai"] != cur[-1]["ai"] or w["s"] - cur[-1]["e"] > 0.35 or len(cur) >= 4
                or cur[-1]["w"][-1] in ".?!" or (cur[-1]["w"][-1] == "," and len(cur) >= 2)):
        chunks.append(cur); cur = []
    cur.append(w)
chunks.append(cur)
cap_html, cap_js = [], []
for k, c in enumerate(chunks):
    a = round(c[0]["s"] - 0.06, 2)
    nxt = chunks[k + 1][0]["s"] - 0.06 if k + 1 < len(chunks) else VID
    b = round(min(nxt, c[-1]["e"] + 0.5, VID), 2)
    cls = "cap ai" if c[0]["ai"] else "cap me"
    cap_html.append(f'<div id="c{k}" class="{cls}">' + " ".join(f'<span class="w">{html.escape(w["w"])}</span>' for w in c) + "</div>")
    cap_js.append([k, a, b, [w["s"] for w in c]])

# key moments, synced to the spoken word (word numbers from clip-words.json)
K = dict(
    name=T(30), emily=T(40), nameOut=T(41) + 0.3,
    two=T(52), twoOut=T(67) + 0.9,                         # "Can I get two original shawarmas" … AI starts the options
    chicken=T(70), beef=T(74), each=T(104),               # "original chicken" / "original beef" / "one of each"
    okChicken=T(112), okBeef=T(117), optsOut=T(119) - 0.1, # AI confirms both, then "Anything else"
    fries=T(127),                                          # "a side of fries"
    small=T(135), large=T(138), lgPick=T(144), lgOk=T(148), sizeOut=T(150) - 0.1,
    pickup=T(173), pickOk=T(175), pickOut=T(182) - 0.3,    # "In about 30 minutes" / "Got it"
    allergy=T(186), noNotes=T(191), notesOut=T(195) - 0.3,
    readback=T(195), rName=T(196), r1=T(205), r2=T(209), r3=T(213), rPick=T(216),
    correct=T(224), yes=T(225), cool=T(233),
    order=T(49), each2=T(102),
)
K = {k: round(v, 2) for k, v in K.items()}

ICON = {
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "wrap": '<path d="M6 3h12l-3.2 18H9.2z"/><path d="M7 8h10M7.8 13h8.4"/>',
    "fries": '<path d="M5 10h14l-2 11H7z"/><path d="M8 10V4M11 10V3M14 10V4M17 10V6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "note": '<path d="M6 3h9l4 4v14H6z"/><path d="M9 11h7M9 15h7"/>',
}
RTILE = open("rtile.svg").read()
ic = lambda k: f'<svg class="ic" viewBox="0 0 24 24">{ICON[k]}</svg>'
TICK = '<svg class="tk" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
sfx = lambda id, f, t, d, v: f'<audio id="sfx-{id}" src="sfx/{f}.wav" data-start="{t:.2f}" data-duration="{d}" data-volume="{v}"></audio>' if t < TOTAL - 0.1 else ""

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

      #vw {{ position: absolute; inset: 0; transform-origin: 540px 760px; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; }}
      #shade {{ position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(11,10,18,0.5) 0%, rgba(11,10,18,0.2) 24%, rgba(11,10,18,0) 36%, rgba(11,10,18,0) 52%, rgba(11,10,18,0.34) 66%, rgba(11,10,18,0.34) 78%, rgba(11,10,18,0) 100%); }}

      /* hook */
      #hook {{ position: absolute; left: 0; top: 250px; width: 1080px; text-align: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 100px; line-height: 1.02; letter-spacing: -0.03em; color: #fff; }}
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

      /* captions: bottom edge sits just above the pills */
      .cap {{ position: absolute; left: 110px; bottom: 712px; width: 860px; text-align: center; font-weight: 700; font-size: 60px; line-height: 1.1; letter-spacing: -0.01em; opacity: 0; }}
      .cap .w {{ display: inline-block; color: #fff; opacity: 0.7; text-shadow: 0 2px 0 rgba(11,10,18,0.45), 0 4px 20px rgba(11,10,18,0.95); }}

      /* pills, right under the captions */
      .chips {{ position: absolute; left: 60px; top: 1232px; width: 960px; display: flex; flex-wrap: wrap; justify-content: center; gap: 18px; }}
      .chip {{ position: relative; height: 82px; padding: 0 34px; border-radius: 999px; display: flex; align-items: center; gap: 14px; font-weight: 700; font-size: 36px; color: #fff; white-space: nowrap;
        background: rgba(11,10,18,0.8); border: 2.5px solid var(--peri); box-shadow: 0 0 20px rgba(143,123,255,0.5); opacity: 0; }}
      .chip .ic {{ position: relative; width: 38px; height: 38px; fill: none; stroke: #b9adff; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
      .chip .pick {{ position: absolute; inset: -3px; border-radius: 999px; background: var(--brand); border: 2.5px solid #b9adff; opacity: 0; }}
      .chip .tk {{ position: relative; width: 34px; height: 34px; margin-left: 4px; fill: none; stroke: #fff; stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; opacity: 0; }}
      .chip span {{ position: relative; }}
      .chip .q {{ font-family: "JetBrains Mono", monospace; font-weight: 400; color: #c4b9ff; margin-right: 4px; }}
      #nmv i {{ font-style: normal; opacity: 0; }}
      #nm .cur {{ display: inline-block; width: 4px; height: 42px; margin-left: 4px; vertical-align: -6px; background: var(--peri); }}
      #nm .lab {{ color: var(--peri); font-weight: 400; margin-right: 12px; }}

      /* order review ticket (top, only during the read-back) */
      #tk {{ position: absolute; left: 200px; top: 110px; width: 680px; padding: 22px 30px 16px; border-radius: 30px; background: rgba(11,10,18,0.86);
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
      .tr {{ display: flex; align-items: center; gap: 18px; height: 50px; overflow: hidden; font-size: 30px; color: #fff; opacity: 0; }}
      .tr:first-of-type {{ margin-top: 8px; }}
      .tr .q {{ width: 64px; font-size: 22px; color: var(--peri); }}
      .tr .v {{ font-weight: 700; white-space: nowrap; }}
      .tr.pk .v {{ font-weight: 400; color: rgba(255,255,255,0.85); }}

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
      <!-- the call (0 to {VID}s): cut-down clip.mp4 -->
      <div id="vw">
        <video id="src" class="clip" src="clip.mp4" data-start="0" data-duration="{VID}" data-has-audio="true" playsinline></video>
        <div id="shade"></div>
        <div id="flash"></div>
      </div>
      <audio id="music" src="music.wav" data-start="0" data-duration="{TOTAL}" data-volume="1"></audio>

      <div id="ov" class="clip" data-start="0" data-duration="{VID}" style="z-index:20">
        <div id="hook"><span class="ln"><span>She's ordering</span></span><span class="ln"><span>from an <b class="ai">AI.</b></span></span></div>

        <div id="agent">
          <div id="acard">
            <div class="row"><i class="dot"></i><img src="rezflo-logo-horizontal-on-dark.svg" alt="RezFlo" /><span class="lab">AI agent</span></div>
            <div id="bars">{"".join("<i></i>" for _ in range(22))}</div>
          </div>
          <div id="anote">Real conversation between<br />a caller and RezFlo AI</div>
        </div>

        <div class="chips" id="cn"><div id="nm" class="chip">{ic("user")}<span><b class="lab">Name</b><b id="nmv">{"".join(f"<i>{c}</i>" for c in "Emily")}</b><i class="cur"></i></span></div></div>
        <div class="chips" id="cq"><div id="two" class="chip">{ic("wrap")}<span><b class="q">2 ×</b>Original shawarma</span></div></div>
        <div class="chips" id="co"><div id="oc" class="chip"><i class="pick"></i>{ic("wrap")}<span>Chicken shawarma</span>{TICK}</div><div id="ob" class="chip"><i class="pick"></i>{ic("wrap")}<span>Beef shawarma</span>{TICK}</div></div>
        <div class="chips" id="cf"><div id="fr" class="chip">{ic("fries")}<span>Side of fries</span></div></div>
        <div class="chips" id="cs"><div id="fs" class="chip"><i class="pick"></i>{ic("fries")}<span>Small fries</span>{TICK}</div><div id="fl" class="chip"><i class="pick"></i>{ic("fries")}<span>Large fries</span>{TICK}</div></div>
        <div class="chips" id="cp"><div id="pk" class="chip"><i class="pick"></i>{ic("clock")}<span>Pickup in about 30 min</span>{TICK}</div></div>
        <div class="chips" id="cx"><div id="al" class="chip"><i class="pick"></i>{ic("note")}<span id="alq">Allergies or notes?</span><span id="aln">No notes or allergies</span>{TICK}</div></div>

        <div id="tk">
          <div class="hd">
            <div><div class="t1">Order review</div><div class="t2 mono">Read back to the caller</div></div>
            <div id="st"><div class="s live mono"><i></i>Live</div><div class="s done mono"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>Placed</div></div>
          </div>
          <div id="rn" class="tr pk"><span class="q mono">◉</span><span class="v">Name · Emily</span></div>
          <div id="r1" class="tr"><span class="q mono">1 ×</span><span class="v">Original chicken shawarma</span></div>
          <div id="r2" class="tr"><span class="q mono">1 ×</span><span class="v">Original beef shawarma</span></div>
          <div id="r3" class="tr"><span class="q mono">1 ×</span><span class="v">Large fries</span></div>
          <div id="rp" class="tr pk"><span class="q mono">◷</span><span class="v">Pickup · in about 30 minutes</span></div>
        </div>

        {(chr(10) + "        ").join(cap_html)}
      </div>
{"" if PREVIEW else f'''
      <!-- end banner (dissolves in from {round(CLIP - XF, 2)}s, full at {CLIP}s, ends {TOTAL}s) -->
      <div id="endc" class="clip" data-start="{round(CLIP - XF, 2)}" data-duration="{round(END + XF, 2)}" style="z-index:30">
        <div id="eR">{RTILE}</div>
        <div id="eq" class="mono">AI receptionist for restaurants</div>
        <div id="esee-m"><span id="esee">Never miss<br />a call again.</span></div>
        <div id="eurl" class="mono">rezflo.ca</div>
        <div id="ebelow"><span>Fill out the form below</span><b>↓</b></div>
      </div>'''}

      {sfx("hook", "switch", 0.12, 0.14, 0.25)}
      {sfx("whoosh", "fill", INTRO - 0.2, 0.5, 0.18)}
      {sfx("card", "pop", INTRO + 0.35, 0.17, 0.22)}
      {sfx("nm", "pop", K["name"], 0.17, 0.2)}
      {sfx("emily", "tick", K["emily"], 0.09, 0.3)}
      {sfx("two", "pop", K["two"], 0.17, 0.2)}
      {sfx("oc", "pop", K["chicken"], 0.17, 0.18)}
      {sfx("ob", "pop", K["beef"], 0.17, 0.18)}
      {sfx("each", "tick", K["each"], 0.09, 0.3)}
      {sfx("okc", "tick", K["okChicken"], 0.09, 0.22)}
      {sfx("okb", "tick", K["okBeef"], 0.09, 0.22)}
      {sfx("fr", "pop", K["fries"], 0.17, 0.2)}
      {sfx("fs", "pop", K["small"], 0.17, 0.18)}
      {sfx("fl", "pop", K["large"], 0.17, 0.18)}
      {sfx("flp", "tick", K["lgPick"], 0.09, 0.3)}
      {sfx("pk", "pop", K["pickup"], 0.17, 0.2)}
      {sfx("pkok", "tick", K["pickOk"], 0.09, 0.28)}
      {sfx("al", "pop", K["allergy"], 0.17, 0.18)}
      {sfx("alok", "tick", K["noNotes"], 0.09, 0.28)}
      {sfx("tk", "pop", K["readback"], 0.17, 0.22)}
      {sfx("rn", "tick", K["rName"], 0.09, 0.25)}
      {sfx("r1", "tick", K["r1"], 0.09, 0.25)}
      {sfx("r2", "tick", K["r2"], 0.09, 0.25)}
      {sfx("r3", "tick", K["r3"], 0.09, 0.25)}
      {sfx("rp", "tick", K["rPick"], 0.09, 0.25)}
      {sfx("ok", "success", K["yes"], 0.6, 0.3)}
      {sfx("fill", "fill", CLIP - 0.9, 0.5, 0.2)}
      {sfx("end", "chime", CLIP - 0.25, 0.95, 0.3)}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const K = {json.dumps(K)};
      const CAPS = {json.dumps(cap_js)};
      const AI = {json.dumps(AI)};
      const JUMPS = {json.dumps(JUMPS)};
      const VID = {VID};
      const INTRO = {INTRO};
      const AION = {{ opacity: 1, color: "#c4b9ff", textShadow: "0 0 22px rgba(143,123,255,0.95), 0 0 6px rgba(143,123,255,0.75), 0 4px 20px rgba(11,10,18,0.95)" }};
      const MEON = {{ opacity: 1, color: "#ffffff", textShadow: "0 0 18px rgba(255,255,255,0.5), 0 4px 20px rgba(11,10,18,0.95)" }};
      const chipIn = (sel, t) => tl.fromTo(sel, {{ opacity: 0, y: 24, scale: 0.86 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(1.6)" }}, t);
      const chipsOut = (sel, t) => tl.to(sel, {{ opacity: 0, y: -14, scale: 0.94, duration: 0.25, ease: "power3.in", stagger: 0.04 }}, t);
      const pick = (sel, t) => {{
        tl.to(sel + " .pick", {{ opacity: 1, duration: 0.15 }}, t);
        tl.fromTo(sel + " .tk", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.4)" }}, t + 0.05);
        tl.fromTo(sel, {{ scale: 1 }}, {{ scale: 1.1, duration: 0.14, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, t);
      }};
      const glow = (sel, t) => tl.fromTo(sel, {{ boxShadow: "0 0 20px rgba(143,123,255,0.5)" }}, {{ boxShadow: "0 0 46px rgba(196,185,255,1)", duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, t);

      // camera: the cold open sits tighter on her reaction; the call starts wide, then slow push-ins that hold
      tl.fromTo("#vw", {{ scale: 1.08 }}, {{ scale: 1.12, duration: INTRO, ease: "none" }}, 0);
      tl.set("#vw", {{ scale: 1 }}, INTRO);
      tl.fromTo("#flash", {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.35, ease: "power2.out", immediateRender: false }}, INTRO);
      tl.fromTo("#vw", {{ scale: 1 }}, {{ scale: 1.03, duration: K.order - INTRO - 0.3, ease: "none", immediateRender: false }}, INTRO);
      tl.to("#vw", {{ scale: 1.08, duration: 2.0, ease: "sine.inOut" }}, K.order - 0.3);       // her order
      tl.to("#vw", {{ scale: 1.13, duration: 1.8, ease: "sine.inOut" }}, K.each2 - 0.3);      // "one of each"
      tl.to("#vw", {{ scale: 1.06, duration: 1.6, ease: "sine.inOut" }}, K.fries - 1.2);      // ease back out for the fries
      tl.to("#vw", {{ scale: 1.1, duration: 2.2, ease: "sine.inOut" }}, K.readback - 0.3);    // read-back
      tl.to("#vw", {{ scale: 1.15, duration: 1.8, ease: "sine.inOut" }}, K.yes - 0.2);       // "Yes, everything sounds perfect"
      tl.to("#vw", {{ scale: 1.2, duration: 2.6, ease: "sine.inOut" }}, K.cool - 0.3);       // her reaction
      // soft flash where part of the call was cut out
      JUMPS.forEach((t) => {{ if (t < VID) tl.fromTo("#flash", {{ opacity: 0.22 }}, {{ opacity: 0, duration: 0.3, ease: "power2.out", immediateRender: false }}, t); }});

      // hook (under 3s)
      tl.fromTo("#hook .ln span", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.12 }}, 0.05);
      tl.to("#hook", {{ opacity: 0, y: -50, duration: 0.3, ease: "power3.in" }}, INTRO + 0.35);

      // "AI agent" card under the captions, then it clears for the pills
      tl.fromTo("#acard", {{ opacity: 0, y: 30, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.5)" }}, INTRO + 0.3);
      tl.fromTo("#anote", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, INTRO + 0.55);
      tl.to("#acard .dot", {{ opacity: 0.35, duration: 0.45, yoyo: true, repeat: 7, ease: "sine.inOut" }}, INTRO + 0.7);
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

      // name: chip with a cursor on "name", "Emily" types in when she says it
      chipIn("#nm", K.name);
      tl.to("#nm .cur", {{ opacity: 0, duration: 0.25, yoyo: true, repeat: 5, ease: "steps(1)" }}, K.name + 0.1);
      document.querySelectorAll("#nmv i").forEach((el, j) => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, immediateRender: false }}, K.emily + j * 0.06));
      chipsOut("#nm", K.nameOut);

      // her order: "2 × Original shawarma", then the AI splits it into chicken / beef
      chipIn("#two", K.two);
      chipsOut("#two", K.twoOut);
      chipIn("#oc", K.chicken); chipIn("#ob", K.beef);
      pick("#oc", K.each); pick("#ob", K.each + 0.12);           // "one of each"
      glow("#oc", K.okChicken); glow("#ob", K.okBeef);            // AI repeats them back
      chipsOut("#co .chip", K.optsOut);

      // fries: side of fries, then small / large, "large" picked, glows when the AI repeats it
      chipIn("#fr", K.fries);
      chipsOut("#fr", K.small - 0.35);
      chipIn("#fs", K.small); chipIn("#fl", K.large);
      pick("#fl", K.lgPick);
      tl.to("#fs", {{ opacity: 0.25, duration: 0.2 }}, K.lgPick);
      glow("#fl", K.lgOk);
      chipsOut("#cs .chip", K.sizeOut);

      // pickup time
      chipIn("#pk", K.pickup);
      pick("#pk", K.pickOk);
      chipsOut("#pk", K.pickOut);

      // allergies: question chip, answered "No" -> "No notes or allergies" with a tick
      tl.set("#aln", {{ display: "none" }}, 0);
      chipIn("#al", K.allergy);
      tl.set("#alq", {{ display: "none" }}, K.noNotes);
      tl.set("#aln", {{ display: "inline" }}, K.noNotes);
      pick("#al", K.noNotes);
      chipsOut("#al", K.notesOut);

      // order review: ticket drops in on "let me confirm", rows light up as they're read
      const flash = (sel, t) => tl.fromTo(sel, {{ color: "#ffffff" }}, {{ color: "#c4b9ff", duration: 0.14, yoyo: true, repeat: 1, immediateRender: false }}, t);
      tl.fromTo("#tk", {{ opacity: 0, y: -40, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.4)" }}, K.readback);
      [["#rn", K.rName], ["#r1", K.r1], ["#r2", K.r2], ["#r3", K.r3], ["#rp", K.rPick]].forEach(([s, t]) => {{
        tl.fromTo(s, {{ height: 0, opacity: 0, x: -30 }}, {{ height: 50, duration: 0.28, ease: "power3.out" }}, t);
        tl.to(s, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }}, t + 0.08);
        flash(s + " .v", t + 0.05);
      }});
      tl.fromTo("#tk", {{ scale: 1 }}, {{ scale: 1.035, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, K.correct);
      tl.to("#st .live", {{ opacity: 0, duration: 0.15 }}, K.yes);
      tl.fromTo("#st .done", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)" }}, K.yes);
      tl.to("#tk", {{ borderColor: "#34c759", boxShadow: "0 0 30px rgba(52,199,89,0.55), 0 24px 60px rgba(11,10,18,0.5)", duration: 0.3 }}, K.yes);

      if (document.getElementById("endc")) {{
        // end banner: dissolves in over her last moment, then the logo builds
        const CLIP = {CLIP}, XF = {XF}, E = CLIP - 0.25;
        tl.fromTo("#endc", {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: "sine.inOut" }}, CLIP - XF);
        tl.to("#tk, .cap", {{ opacity: 0, duration: XF * 0.6, ease: "power2.in" }}, CLIP - XF);
        tl.fromTo("#eR", {{ scale: 0.6, opacity: 0, y: 40 }}, {{ scale: 1, opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.3)" }}, E);
        tl.fromTo("#eR .lane-g", {{ x: 14, y: -14, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.34, ease: "expo.out" }}, E + 0.06);
        tl.fromTo("#eR .lane-p", {{ x: -14, y: 14, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.34, ease: "expo.out" }}, E + 0.11);
        tl.fromTo("#eR .slash-g, #eR .slash-p", {{ x: -22, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.26, ease: "back.out(2)", stagger: 0.05 }}, E + 0.3);
        tl.fromTo("#eq", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, E + 0.35);
        tl.fromTo("#esee", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out" }}, E + 0.55);
        tl.fromTo("#eurl", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, E + 0.9);
        tl.fromTo("#ebelow", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, E + 1.15);
        tl.fromTo("#ebelow b", {{ y: -4 }}, {{ y: 8, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 5, immediateRender: false }}, E + 1.45);
      }}

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(page)
print(len(chunks), "caption chunks,", TOTAL, "s, AI ranges", len(AI), "K", K)
