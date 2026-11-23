# Builds index.html for the Ayana pickup-call ad (same family as ad-03 Joudy, with extra polish:
# light sweeps on picks, a price count-up, a "placed" ring, and a pop on her reaction).
# Inputs: clip-words.json (word timings of clip.mp4) and clip.segs.json (cut points), from cut.py + transcribe.py.
# Run: python3 build.py [preview seconds] ; npx hyperframes check ; npx hyperframes render
import json, html, sys, re

SEGS = json.load(open("clip.segs.json"))
CLIP = SEGS[-1]["out"][1]                 # clip.mp4 length
PREVIEW = float(sys.argv[1]) if len(sys.argv) > 1 else None
END = 3.6                                 # end banner length (fully on screen)
XF = 0.7                                  # dissolve from the call into the banner
TOTAL = round(PREVIEW if PREVIEW else CLIP + END, 2)
VID = round(min(CLIP, TOTAL), 2)
INTRO = SEGS[1]["out"][0]                 # end of the cold open; the call starts here
JUMPS = [SEGS[19]["out"][0]]              # after "See you soon" the recording jumps to her reaction: soft flash

# Whisper's word times run up to ~0.45 s early on this recording. Re-anchor every segment so its first word
# lands where speech really starts (span start in cut.py, measured from loudness), keeping the gaps inside it.
src = open("cut.py").read()
REAL = [142.30] + [float(a) for a, b in re.findall(r"^\s+\((\d+\.\d+), (\d+\.\d+)\),", src.split("spans = [")[1].split("]")[0], re.M)]
raw = json.load(open("clip-words.json"))
seg_of = lambda t: min(range(len(SEGS)), key=lambda k: 0 if SEGS[k]["out"][0] <= t < SEGS[k]["out"][1] else min(abs(t - SEGS[k]["out"][0]), abs(t - SEGS[k]["out"][1])))
for w in raw: w["k"] = seg_of((w["s"] + w["e"]) / 2)
for k, s in enumerate(SEGS):
    ws = [w for w in raw if w["k"] == k]
    if not ws: continue
    onset = s["out"][0] + (REAL[k] - s["src"][0])
    d = onset - ws[0]["s"]
    for w in ws: w["s"] = round(w["s"] + d, 2); w["e"] = round(min(w["e"] + d, s["out"][1]), 2)

# who is talking: segment k>=1 is span k-1 in cut.py. AI spans, plus her one-word answers inside them
AI_SPANS = {0, 2, 4, 6, 8, 10, 12, 13, 15, 16, 17}
HER = {146, 184, 199, 200}                # "No."  "Yes."  "That's it."
words = []
for i, w in enumerate(raw):
    ai = w["k"] >= 1 and (w["k"] - 1) in AI_SPANS and i not in HER
    words.append({"w": w["w"], "s": w["s"], "e": w["e"], "ai": ai, "i": i})
# caption text: keep the restaurant name off screen; fix what speech-to-text misheard or split
DROP = {11, 12, 13, 14, 15, 178, 204, 205}   # "Al-Basha Original in Surrey."  ".07"  "from Alvasha."
FIX = {10: "calling!", 16: "How", 57: "served", 135: "4:40", 136: "PM.", 172: "4:40", 173: "PM.", 195: "4:40", 196: "PM.",
       177: "$16.07", 192: "#1002,", 203: "ordering.", 159: "Sarah,"}
for w in words:
    w["w"] = FIX.get(w["i"], w["w"])
cwords = [w for w in words if w["i"] not in DROP and w["s"] < TOTAL - 0.2]
T = lambda i: raw[i]["s"]                 # (re-anchored) start time of word i in clip.mp4

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
    spans = []
    for w in c:
        hi = " hi" if w["i"] == 212 else ""                 # "seamless." gets the pop
        spans.append(f'<span class="w{hi}">{html.escape(w["w"])}</span>')
    cap_html.append(f'<div id="cap{k}" class="{cls}">' + " ".join(spans) + "</div>")
    cap_js.append([k, a, b, [w["s"] for w in c]])

# key moments, synced to the spoken word (word numbers from clip-words.json)
K = dict(
    pickup=T(27),                                            # "...order for pickup?"
    order=T(36), chicken=T(40),                              # "Can I get a chicken shawarma?"
    wrap=T(51), orig=T(56), plate=T(62), origPick=T(68), great=T(69), styleOut=T(75),
    drink=T(84), sprite=T(91), ginger=T(92), crush=T(94), spPick=T(101), spOk=T(102), drinkOut=T(110) - 0.2,
    asap=T(120), time=T(135), timeOut=T(137) - 0.1,
    allergy=T(141), noAll=T(146), allOut=T(147) + 0.5,
    name=T(151), sarah=T(158),
    readback=T(159), r1=T(161), r2=T(167), rPick=T(170), total=T(175), price=T(177),
    right=T(181), yes=T(184), placed=T(185), num=T(192), bye=T(206), react=T(209), seam=T(212),
)
K = {k: round(v, 2) for k, v in K.items()}

ICON = {
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "bag": '<path d="M5 8h14l-1.2 13H6.2z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "wrap": '<path d="M6 3h12l-3.2 18H9.2z"/><path d="M7 8h10M7.8 13h8.4"/>',
    "fries": '<path d="M5 10h14l-2 11H7z"/><path d="M8 10V4M11 10V3M14 10V4M17 10V6"/>',
    "plate": '<circle cx="12" cy="13" r="8"/><circle cx="12" cy="13" r="4.2"/>',
    "cup": '<path d="M6 8h12l-1.6 13H7.6z"/><path d="M5 8h14M13 8l2-5h3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "note": '<path d="M6 3h9l4 4v14H6z"/><path d="M9 11h7M9 15h7"/>',
}
RTILE = open("rtile.svg").read()
ic = lambda k: f'<svg class="ic" viewBox="0 0 24 24">{ICON[k]}</svg>'
TICK = '<svg class="tk" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
SH = '<i class="shw"><i class="sh"></i></i>'               # light sweep layer
def chip(id, icon, text, pickable=True):
    return (f'<div id="{id}" class="chip">' + ('<i class="pick"></i>' if pickable else "") + SH + ic(icon)
            + f"<span>{text}</span>" + (TICK if pickable else "") + "</div>")
sfx = lambda id, f, t, d, v: f'<audio id="sfx-{id}" src="sfx/{f}.wav" data-start="{t:.2f}" data-duration="{d}" data-volume="{v}"></audio>' if t < TOTAL - 0.1 else ""
PRICE = 16.07
STEPS = [round(PRICE * (1 - (1 - j / 14) ** 3), 2) for j in range(15)]   # ease-out count-up values

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

      #vw {{ position: absolute; inset: 0; transform-origin: 540px 800px; }}
      #src {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; }}
      #shade {{ position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(11,10,18,0.55) 0%, rgba(11,10,18,0.22) 22%, rgba(11,10,18,0) 34%, rgba(11,10,18,0) 50%, rgba(11,10,18,0.38) 64%, rgba(11,10,18,0.38) 78%, rgba(11,10,18,0.05) 100%); }}
      /* soft cinematic vignette + a faint brand tint in the corners */
      #vig {{ position: absolute; inset: 0; background: radial-gradient(120% 80% at 50% 42%, rgba(11,10,18,0) 55%, rgba(11,10,18,0.42) 100%); }}
      #tint {{ position: absolute; inset: 0; background: radial-gradient(70% 40% at 0% 100%, rgba(91,65,218,0.22), rgba(91,65,218,0) 70%), radial-gradient(60% 34% at 100% 0%, rgba(91,65,218,0.16), rgba(91,65,218,0) 70%); mix-blend-mode: screen; }}

      /* hook */
      #hook {{ position: absolute; left: 0; top: 240px; width: 1080px; text-align: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 104px; line-height: 1.02; letter-spacing: -0.03em; color: #fff; }}
      #hook .ln {{ display: block; overflow: hidden; padding: 0 0 10px; }}
      #hook .ln > span {{ display: inline-block; text-shadow: 0 6px 30px rgba(11,10,18,0.75); }}
      #hook .ai {{ position: relative; color: var(--peri); text-shadow: 0 0 26px rgba(143,123,255,0.85), 0 6px 30px rgba(11,10,18,0.75); }}
      #hook .ul {{ position: absolute; left: 4px; right: 30px; bottom: -4px; height: 9px; border-radius: 5px; background: var(--peri); box-shadow: 0 0 18px var(--peri); transform-origin: 0 50%; }}

      /* "AI agent" card at the start */
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
      .chip {{ position: relative; height: 82px; padding: 0 32px; border-radius: 999px; display: flex; align-items: center; gap: 14px; font-weight: 700; font-size: 36px; color: #fff; white-space: nowrap;
        background: rgba(11,10,18,0.8); border: 2.5px solid var(--peri); box-shadow: 0 0 20px rgba(143,123,255,0.5); opacity: 0; }}
      .chip .ic {{ position: relative; width: 38px; height: 38px; fill: none; stroke: #b9adff; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
      .chip .pick {{ position: absolute; inset: -3px; border-radius: 999px; background: var(--brand); border: 2.5px solid #b9adff; opacity: 0; }}
      .chip .tk {{ position: relative; width: 34px; height: 34px; margin-left: 4px; fill: none; stroke: #fff; stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; opacity: 0; }}
      .chip span {{ position: relative; }}
      .shw {{ position: absolute; inset: -3px; border-radius: 999px; overflow: hidden; pointer-events: none; }}
      .sh {{ position: absolute; top: -20%; left: 0; width: 46%; height: 140%; transform: translateX(-140%) skewX(-18deg);
        background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.55) 50%, rgba(255,255,255,0) 100%); }}
      #opts .chip {{ padding: 0 28px; font-size: 34px; }}
      #nmv i {{ font-style: normal; opacity: 0; }}
      #nm .cur {{ display: inline-block; width: 4px; height: 42px; margin-left: 4px; vertical-align: -6px; background: var(--peri); }}
      #nm .lab {{ color: var(--peri); font-weight: 400; margin-right: 12px; }}

      /* order review ticket (top, only during the read-back) */
      #tk {{ position: absolute; left: 190px; top: 96px; width: 700px; padding: 22px 30px 18px; border-radius: 30px; background: rgba(11,10,18,0.88);
        border: 2.5px solid var(--peri); box-shadow: 0 0 26px rgba(143,123,255,0.5), 0 24px 60px rgba(11,10,18,0.5); opacity: 0; }}
      #tk .hd {{ display: flex; align-items: center; justify-content: space-between; padding-bottom: 14px; border-bottom: 2px solid rgba(143,123,255,0.3); }}
      #tk .t1 {{ font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 38px; color: #fff; letter-spacing: -0.01em; display: flex; align-items: baseline; gap: 14px; }}
      #onum {{ font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 26px; color: #c4b9ff; opacity: 0; display: inline-block; }}
      #tk .t2 {{ font-size: 19px; color: var(--peri); margin-top: 6px; }}
      #st {{ position: relative; width: 196px; height: 46px; }}
      #st .s {{ position: absolute; right: 0; top: 0; height: 46px; display: flex; align-items: center; gap: 10px; padding: 0 16px; border-radius: 999px; font-size: 19px; white-space: nowrap; }}
      #st .live {{ color: var(--peri); border: 2px solid rgba(143,123,255,0.6); }}
      #st .live i {{ width: 11px; height: 11px; border-radius: 50%; background: var(--peri); }}
      #st .done {{ color: #fff; background: var(--green); opacity: 0; }}
      #st .done svg {{ width: 22px; height: 22px; }}
      #ring {{ position: absolute; right: 40px; top: 26px; width: 120px; height: 120px; margin: -37px -12px 0 0; border-radius: 50%; border: 4px solid var(--green); opacity: 0; pointer-events: none; }}
      .tr {{ display: flex; align-items: center; gap: 18px; height: 50px; overflow: hidden; font-size: 30px; color: #fff; opacity: 0; }}
      .tr:first-of-type {{ margin-top: 8px; }}
      .tr .q {{ width: 64px; font-size: 22px; color: var(--peri); }}
      .tr .v {{ font-weight: 700; white-space: nowrap; }}
      .tr.pk .v {{ font-weight: 400; color: rgba(255,255,255,0.85); }}
      #rt {{ margin-top: 6px; border-top: 2px dashed rgba(143,123,255,0.3); height: 62px; }}
      #rt .v {{ font-weight: 400; color: rgba(255,255,255,0.85); }}
      #rt .amt {{ margin-left: auto; font-family: "JetBrains Mono", monospace; font-size: 36px; font-weight: 400; color: #fff; letter-spacing: 0.02em; }}
      #tkshw {{ border-radius: 30px; inset: 0; }}

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
        <div id="vig"></div>
        <div id="tint"></div>
        <div id="flash"></div>
      </div>
      <audio id="music" src="music.wav" data-start="0" data-duration="{TOTAL}" data-volume="1"></audio>

      <div id="ov" class="clip" data-start="0" data-duration="{VID}" style="z-index:20">
        <div id="hook"><span class="ln"><span>Watch her order</span></span><span class="ln"><span>from an <b class="ai">AI.<i class="ul"></i></b></span></span></div>

        <div id="agent">
          <div id="acard">
            <div class="row"><i class="dot"></i><img src="rezflo-logo-horizontal-on-dark.svg" alt="RezFlo" /><span class="lab">AI agent</span></div>
            <div id="bars">{"".join("<i></i>" for _ in range(22))}</div>
          </div>
          <div id="anote">Real conversation between<br />a caller and RezFlo AI</div>
        </div>

        <div class="chips" id="cpk">{chip("pko", "bag", "Pickup order", False)}</div>
        <div class="chips" id="cch">{chip("ch", "wrap", "Chicken shawarma", False)}</div>
        <div class="chips" id="opts">{chip("ow", "wrap", "Wrap")}{chip("oo", "fries", "Original + fries")}{chip("op", "plate", "Arabic plate")}</div>
        <div class="chips" id="cdr">{chip("ds", "cup", "Sprite")}{chip("dg", "cup", "Ginger Ale")}{chip("dc", "cup", "Crush")}</div>
        <div class="chips" id="ctm"><div id="tm" class="chip"><i class="pick"></i>{SH}{ic("clock")}<span id="tmq">As soon as possible</span><span id="tma">Ready at 4:40 PM</span>{TICK}</div></div>
        <div class="chips" id="cal"><div id="al" class="chip"><i class="pick"></i>{SH}{ic("note")}<span id="alq">Allergies or notes?</span><span id="aln">No allergies</span>{TICK}</div></div>
        <div class="chips" id="cnm"><div id="nm" class="chip">{SH}{ic("user")}<span><b class="lab">Name</b><b id="nmv">{"".join(f"<i>{c}</i>" for c in "Sarah")}</b><i class="cur"></i></span></div></div>

        <div id="tk">
          <i class="shw" id="tkshw"><i class="sh"></i></i>
          <div class="hd">
            <div><div class="t1">Order review <span id="onum">#1002</span></div><div class="t2 mono">Read back to the caller</div></div>
            <div id="st"><div class="s live mono"><i></i>Live</div><div class="s done mono"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>Placed</div></div>
          </div>
          <i id="ring"></i>
          <div id="rn" class="tr pk"><span class="q mono">◉</span><span class="v">Name · Sarah</span></div>
          <div id="r1" class="tr"><span class="q mono">1 ×</span><span class="v">Original chicken shawarma</span></div>
          <div id="r2" class="tr"><span class="q mono">1 ×</span><span class="v">Sprite</span></div>
          <div id="rp" class="tr pk"><span class="q mono">◷</span><span class="v">Pickup · ready at 4:40 PM</span></div>
          <div id="rt" class="tr"><span class="q mono">$</span><span class="v">Total with tax</span><span class="amt" id="amt">$0.00</span></div>
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
      {sfx("pko", "pop", K["pickup"], 0.17, 0.18)}
      {sfx("ch", "pop", K["chicken"], 0.17, 0.2)}
      {sfx("ow", "pop", K["wrap"], 0.17, 0.16)}
      {sfx("oo", "pop", K["orig"], 0.17, 0.16)}
      {sfx("op", "pop", K["plate"], 0.17, 0.16)}
      {sfx("oop", "tick", K["origPick"], 0.09, 0.3)}
      {sfx("ds", "pop", K["sprite"], 0.17, 0.16)}
      {sfx("dg", "pop", K["ginger"], 0.17, 0.16)}
      {sfx("dc", "pop", K["crush"], 0.17, 0.16)}
      {sfx("dsp", "tick", K["spPick"], 0.09, 0.3)}
      {sfx("tm", "pop", K["asap"], 0.17, 0.2)}
      {sfx("tmok", "tick", K["time"], 0.09, 0.28)}
      {sfx("al", "pop", K["allergy"], 0.17, 0.18)}
      {sfx("alok", "tick", K["noAll"], 0.09, 0.28)}
      {sfx("nm", "pop", K["name"], 0.17, 0.2)}
      {sfx("sarah", "tick", K["sarah"], 0.09, 0.3)}
      {sfx("tk", "pop", K["readback"], 0.17, 0.22)}
      {sfx("r1", "tick", K["r1"], 0.09, 0.25)}
      {sfx("r2", "tick", K["r2"], 0.09, 0.25)}
      {sfx("rp", "tick", K["rPick"], 0.09, 0.25)}
      {sfx("cnt", "counter", K["price"], 0.6, 0.22)}
      {sfx("ok", "success", K["yes"], 0.6, 0.3)}
      {sfx("num", "snap", K["num"], 0.2, 0.22)}
      {sfx("star", "star", K["seam"], 0.6, 0.2)}
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
      const STEPS = {json.dumps(STEPS)};
      const VID = {VID};
      const INTRO = {INTRO};
      const AION = {{ opacity: 1, color: "#c4b9ff", textShadow: "0 0 22px rgba(143,123,255,0.95), 0 0 6px rgba(143,123,255,0.75), 0 4px 20px rgba(11,10,18,0.95)" }};
      const MEON = {{ opacity: 1, color: "#ffffff", textShadow: "0 0 18px rgba(255,255,255,0.5), 0 4px 20px rgba(11,10,18,0.95)" }};
      const chipIn = (sel, t) => tl.fromTo(sel, {{ opacity: 0, y: 24, scale: 0.86 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(1.6)" }}, t);
      const chipsOut = (sel, t) => tl.to(sel, {{ opacity: 0, y: -14, scale: 0.94, duration: 0.25, ease: "power3.in", stagger: 0.04 }}, t);
      const sweep = (sel, t, d) => tl.fromTo(sel + " .sh", {{ xPercent: -140 }}, {{ xPercent: 340, duration: d || 0.55, ease: "power2.inOut", immediateRender: false }}, t);
      const pick = (sel, t) => {{
        tl.to(sel + " .pick", {{ opacity: 1, duration: 0.15 }}, t);
        tl.fromTo(sel + " .tk", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.4)" }}, t + 0.05);
        tl.fromTo(sel, {{ scale: 1 }}, {{ scale: 1.1, duration: 0.14, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, t);
        sweep(sel, t + 0.08);
      }};
      const dim = (sel, t) => tl.to(sel, {{ opacity: 0.25, scale: 0.94, duration: 0.22 }}, t);
      const glow = (sel, t) => tl.fromTo(sel, {{ boxShadow: "0 0 20px rgba(143,123,255,0.5)" }}, {{ boxShadow: "0 0 46px rgba(196,185,255,1)", duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, t);

      // camera: the cold open sits tighter on her reaction; the call starts wide, then slow push-ins that hold
      tl.fromTo("#vw", {{ scale: 1.08 }}, {{ scale: 1.13, duration: INTRO, ease: "none" }}, 0);
      tl.set("#vw", {{ scale: 1 }}, INTRO);
      tl.fromTo("#flash", {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.35, ease: "power2.out", immediateRender: false }}, INTRO);
      tl.fromTo("#vw", {{ scale: 1 }}, {{ scale: 1.03, duration: K.order - INTRO - 0.3, ease: "none", immediateRender: false }}, INTRO);
      tl.to("#vw", {{ scale: 1.07, duration: 1.8, ease: "sine.inOut" }}, K.order - 0.3);       // "Can I get a chicken shawarma?"
      tl.to("#vw", {{ scale: 1.03, duration: 1.6, ease: "sine.inOut" }}, K.wrap - 0.8);        // wide for the options
      tl.to("#vw", {{ scale: 1.1, duration: 1.6, ease: "sine.inOut" }}, K.origPick - 0.3);     // "I'll take an original"
      tl.to("#vw", {{ scale: 1.04, duration: 1.6, ease: "sine.inOut" }}, K.drink - 0.4);       // drinks
      tl.to("#vw", {{ scale: 1.09, duration: 1.6, ease: "sine.inOut" }}, K.spPick - 0.3);      // "I'll take Sprite"
      tl.to("#vw", {{ scale: 1.05, duration: 1.6, ease: "sine.inOut" }}, K.asap - 0.6);
      tl.to("#vw", {{ scale: 1.09, duration: 2.2, ease: "sine.inOut" }}, K.readback - 0.3);    // read-back
      tl.to("#vw", {{ scale: 1.14, duration: 1.8, ease: "sine.inOut" }}, K.yes - 0.2);         // "Yes."
      tl.to("#vw", {{ scale: 1.08, duration: Math.min(1.4, K.react - 0.3 - (K.bye - 0.6)), ease: "sine.inOut" }}, K.bye - 0.6);
      tl.fromTo("#vw", {{ scale: 1.16 }}, {{ scale: 1.22, duration: VID - K.react + 0.4, ease: "none", immediateRender: false }}, K.react - 0.25);   // her reaction
      JUMPS.forEach((t) => {{ if (t < VID) tl.fromTo("#flash", {{ opacity: 0.3 }}, {{ opacity: 0, duration: 0.3, ease: "power2.out", immediateRender: false }}, t); }});

      // hook (under 3s): lines rise in, "AI." gets an underline swipe
      tl.fromTo("#hook .ln > span", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.12 }}, 0.05);
      tl.fromTo("#hook .ul", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power3.out" }}, 0.55);
      tl.to("#hook", {{ opacity: 0, y: -50, duration: 0.3, ease: "power3.in" }}, INTRO + 0.35);

      // "AI agent" card, then it clears for the pills
      tl.fromTo("#acard", {{ opacity: 0, y: 30, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.5)" }}, INTRO + 0.3);
      tl.fromTo("#anote", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, INTRO + 0.55);
      tl.to("#acard .dot", {{ opacity: 0.35, duration: 0.45, yoyo: true, repeat: 3, ease: "sine.inOut" }}, INTRO + 0.7);
      tl.to("#agent > *", {{ opacity: 0, y: -16, duration: 0.3, ease: "power3.in", stagger: 0.05 }}, K.pickup - 0.45);

      // waveform moves while the AI talks (fixed pattern, so every render is identical)
      const H = [0.5, 0.85, 0.35, 1, 0.6, 0.9, 0.3, 0.75, 0.45, 0.95, 0.55];
      const bars = document.querySelectorAll("#bars i");
      AI.forEach(([a, b]) => {{
        if (a > K.pickup) return;
        b = Math.min(b, K.pickup - 0.45);
        for (let t = a, n = 0; t < b; t += 0.12, n++) {{
          bars.forEach((el, j) => tl.to(el, {{ scaleY: 0.18 + 0.82 * H[(j * 3 + n * 5) % 11] * (0.55 + 0.45 * ((n + j) % 4) / 3), duration: 0.11, ease: "sine.inOut" }}, t));
        }}
        tl.to(bars, {{ scaleY: 0.16, duration: 0.15 }}, b);
      }});

      // captions: chunk on/off, each word lights up as it is said
      CAPS.forEach(([k, a, b, ws]) => {{
        const el = document.getElementById("cap" + k);
        tl.fromTo(el, {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, a);
        const on = el.classList.contains("ai") ? AION : MEON;
        el.querySelectorAll(".w").forEach((w, j) => tl.set(w, on, ws[j]));
        tl.set(el, {{ opacity: 0 }}, b);
      }});
      // "seamless." pops on her reaction
      tl.fromTo(".cap .hi", {{ scale: 1 }}, {{ scale: 1.22, color: "#c4b9ff", textShadow: "0 0 30px rgba(143,123,255,1), 0 4px 20px rgba(11,10,18,0.95)", duration: 0.35, ease: "back.out(2.2)", immediateRender: false }}, K.seam);

      // pickup, then her order
      chipIn("#pko", K.pickup); sweep("#pko", K.pickup + 0.15);
      chipsOut("#pko", K.chicken - 0.35);
      chipIn("#ch", K.chicken); sweep("#ch", K.chicken + 0.15);
      chipsOut("#ch", K.wrap - 0.35);

      // style: wrap / original + fries / Arabic plate -> "original"
      chipIn("#ow", K.wrap); chipIn("#oo", K.orig); chipIn("#op", K.plate);
      pick("#oo", K.origPick); dim("#ow", K.origPick); dim("#op", K.origPick);
      glow("#oo", K.great);
      chipsOut("#opts .chip", K.styleOut);

      // drink: Sprite / Ginger Ale / Crush -> Sprite
      chipIn("#ds", K.sprite); chipIn("#dg", K.ginger); chipIn("#dc", K.crush);
      pick("#ds", K.spPick); dim("#dg", K.spPick); dim("#dc", K.spPick);
      glow("#ds", K.spOk);
      chipsOut("#cdr .chip", K.drinkOut);

      // pickup time: "As soon as possible" -> "Ready at 4:40 PM"
      tl.set("#tma", {{ display: "none" }}, 0);
      chipIn("#tm", K.asap);
      tl.set("#tmq", {{ display: "none" }}, K.time);
      tl.set("#tma", {{ display: "inline" }}, K.time);
      pick("#tm", K.time);
      chipsOut("#tm", K.timeOut);

      // allergies: question, answered "No"
      tl.set("#aln", {{ display: "none" }}, 0);
      chipIn("#al", K.allergy);
      tl.set("#alq", {{ display: "none" }}, K.noAll);
      tl.set("#aln", {{ display: "inline" }}, K.noAll);
      pick("#al", K.noAll);
      chipsOut("#al", K.allOut);

      // name: chip with a cursor, "Sarah" types in when she says it
      chipIn("#nm", K.name);
      tl.to("#nm .cur", {{ opacity: 0, duration: 0.25, yoyo: true, repeat: 5, ease: "steps(1)" }}, K.name + 0.1);
      document.querySelectorAll("#nmv i").forEach((el, j) => tl.fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, immediateRender: false }}, K.sarah + j * 0.06));
      sweep("#nm", K.sarah + 0.3);
      chipsOut("#nm", K.readback + 0.6);

      // order review: ticket drops in with the read-back, rows light up as they're read, total counts up
      const flash = (sel, t) => tl.fromTo(sel, {{ color: "#ffffff" }}, {{ color: "#c4b9ff", duration: 0.14, yoyo: true, repeat: 1, immediateRender: false }}, t);
      tl.fromTo("#tk", {{ opacity: 0, y: -40, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.4)" }}, K.readback);
      [["#rn", K.readback + 0.2, 50], ["#r1", K.r1, 50], ["#r2", K.r2, 50], ["#rp", K.rPick, 50], ["#rt", K.total, 62]].forEach(([s, t, h]) => {{
        tl.fromTo(s, {{ height: 0, opacity: 0, x: -30 }}, {{ height: h, duration: 0.28, ease: "power3.out" }}, t);
        tl.to(s, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }}, t + 0.08);
        flash(s + " .v", t + 0.05);
      }});
      STEPS.forEach((v, j) => tl.set("#amt", {{ innerText: "$" + v.toFixed(2) }}, K.price + j * 0.045));
      tl.fromTo("#amt", {{ scale: 1 }}, {{ scale: 1.15, color: "#c4b9ff", duration: 0.16, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, K.price + 0.65);
      tl.fromTo("#tk", {{ scale: 1 }}, {{ scale: 1.035, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, K.right);
      // "Yes." -> placed: status flips green, a ring pulses out, light sweeps across the ticket
      tl.to("#st .live", {{ opacity: 0, duration: 0.15 }}, K.yes);
      tl.fromTo("#st .done", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)" }}, K.yes);
      tl.to("#tk", {{ borderColor: "#34c759", boxShadow: "0 0 34px rgba(52,199,89,0.6), 0 24px 60px rgba(11,10,18,0.5)", duration: 0.3 }}, K.yes);
      tl.fromTo("#ring", {{ opacity: 0.9, scale: 0.4 }}, {{ opacity: 0, scale: 1.8, duration: 0.7, ease: "power2.out", immediateRender: false }}, K.yes + 0.05);
      tl.fromTo("#tkshw .sh", {{ xPercent: -140 }}, {{ xPercent: 340, duration: 0.8, ease: "power2.inOut", immediateRender: false }}, K.yes + 0.1);
      // "number 1002" -> order number stamps into the header
      tl.fromTo("#onum", {{ opacity: 0, scale: 1.8, y: -6 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.35, ease: "back.out(2.4)" }}, K.num + 0.1);
      // ticket clears for her reaction
      tl.to("#tk", {{ opacity: 0, y: -30, scale: 0.96, duration: 0.35, ease: "power3.in" }}, K.react - 0.2);

      if (document.getElementById("endc")) {{
        // end banner: dissolves in over her last moment, then the logo builds
        const CLIP = {CLIP}, XF = {XF}, E = CLIP - 0.25;
        tl.fromTo("#endc", {{ opacity: 0 }}, {{ opacity: 1, duration: XF, ease: "sine.inOut" }}, CLIP - XF);
        tl.to(".cap", {{ opacity: 0, duration: XF * 0.6, ease: "power2.in" }}, CLIP - XF);
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
print(len(chunks), "caption chunks,", TOTAL, "s, AI ranges", len(AI))
print("K", K)
