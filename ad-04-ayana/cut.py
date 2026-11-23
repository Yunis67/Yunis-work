# Cuts the Ayana pickup call into clip.mp4 (1080x1920, 30 fps).
# Sound comes from the separate recording (raw-audio.m4a); picture from the phone video (raw-video.mp4).
# The video runs OFFSET seconds behind the audio file (measured by cross-correlation, constant, no drift).
# Spans are (first word start, last word end) in AUDIO time. Pauses between turns are kept up to CAP seconds.
# Run: /usr/bin/python3 denoise.py ../raw/ayana-audio.m4a ../raw/ayana-audio-clean.wav
#      python3 cut.py ../raw/ayana-video.mp4 ../raw/ayana-audio-clean.wav clip.mp4 <tmp dir>
import subprocess, sys, json, os
vsrc, asrc, out, tmp = sys.argv[1:5]
OFFSET = 2.06
spans = [               # real speech edges, set from the cleaned audio's loudness (Whisper runs ~0.4 s early here)
    (4.65, 8.40),     # 0  AI: Hey, thanks for calling ... How may I help you?
                      #    gap 8.85-11.15: someone else nearby says "Hello, how can I help you?" (cut)
    (12.25, 13.70),   # 1  Can I place an order for pickup?
    (16.12, 18.66),   # 2  AI: Absolutely. What can I get started for you?
    (19.85, 21.10),   # 3  Can I get a chicken shawarma?
    (22.52, 29.52),   # 4  AI: Sure thing. Wrap, original with fries, or the Arabic shawarma plate?
    (30.40, 31.34),   # 5  I'll take an original.
    (33.58, 37.70),   # 6  AI: Great choice. Anything else ... just the one original?
    (38.92, 39.32),   # 7  That's it.
    (41.20, 45.86),   # 8  AI: Want a drink with that? Sprite, Ginger Ale, Crush ...
    (46.96, 47.66),   # 9  I'll take Sprite.
    (50.60, 56.68),   # 10 AI: Sprite it is. Got it. One Sprite added. What time ... pickup?
    (57.82, 58.88),   # 11 As soon as possible.
    (61.84, 71.00),   # 12 AI: Sounds good ... about 4:40 p.m. Any allergies?   Her: No.
    (73.50, 76.66),   # 13 AI: Got it. And what name should I put the order under?
    (77.50, 77.92),   # 14 Sarah.
    (80.12, 90.86),   # 15 AI: Sarah, that's one chicken original ... $16.07 with tax. Is that right?   Her: Yes.
    (93.10, 100.98),  # 16 AI: Your order is placed ... number 1002 ... Anything else?   Her: That's it.
    (102.45, 104.90), # 17 AI: Thanks for ordering ... See you soon.
                      #    CUT 105-120: "Wow, that was such a seamless" (cut off) and off-camera chatter
    (120.05, 122.30), # 18 That was insanely seamless. I can't believe it.
]
removed_after = {17}               # a chunk of the recording was cut between span i and i+1
CAP, JUMP = 0.7, 0.5                # longest pause kept between turns; pause used across a cut
OUTRO = 1.0                         # roll on after "so cool!" while her voice fades
INTRO = (142.10, 144.30)            # cold open: "Oh my God. That was so cool." (best of four takes) plays first as the hook
keep = [INTRO]
for i, (a, b) in enumerate(spans):
    lead = 0.3 if i == 0 else (JUMP if i - 1 in removed_after else min(a - spans[i-1][1], CAP)) / 2
    tail = OUTRO if i == len(spans) - 1 else (JUMP if i in removed_after else min(spans[i+1][0] - b, CAP)) / 2
    if i == 0: tail = 0.20          # the other voice starts at 8.85
    keep.append((round(a - lead, 3), round(b + tail, 3)))

# Café noise is removed first by denoise.py (pass its output as the audio file). Here: trim rumble and hiss,
# a soft gate that lowers whatever room is left between words (~14 dB, never to silence), then even levels.
CLEAN = "highpass=f=90,lowpass=f=12000,agate=threshold=0.015:ratio=2:range=0.2:attack=5:release=200,"
LEVEL = "acompressor=threshold=0.12:ratio=2.5:attack=10:release=150:makeup=1.6,"
# phone export is 608x1080 and already bright: scale up cleanly to 1080x1920 with a light sharpen, no grade
# with LOWRES=1 the picture stays at its native 320x568 (crf 8) for the AI upscaler (kit/upscale, then finish.py)
LOWRES = os.environ.get("LOWRES") == "1"
VF = "format=yuv420p" if LOWRES else "scale=1080:1920:flags=lanczos,unsharp=5:5:0.45:5:5:0,format=yuv420p"
os.makedirs(tmp, exist_ok=True); lst = []
for i, (a, b) in enumerate(keep):
    du = b - a; f = f"{tmp}/s{i:02d}.mp4"
    last = i == len(keep) - 1
    fade = (f"afade=t=in:d=0.03,afade=t=out:st={du-OUTRO+0.05:.3f}:d={OUTRO-0.1:.2f}" if last
            else f"afade=t=in:d=0.03,afade=t=out:st={du-0.2:.3f}:d=0.18" if i == 0
            else f"afade=t=in:d=0.03,afade=t=out:st={du-0.04:.3f}:d=0.04")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a + OFFSET}", "-i", vsrc, "-ss", f"{a}", "-i", asrc,
        "-t", f"{du:.3f}", "-map", "0:v", "-map", "1:a", "-vf", VF, "-af", CLEAN + LEVEL + fade,
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:v", "libx264", "-crf", "8" if LOWRES else "16", "-preset", "fast", "-r", "30",
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f.replace(".mp4", ".mov")], check=True)
    lst.append(f"file '{f.replace('.mp4', '.mov')}'")
open(tmp + "/list.txt", "w").write("\n".join(lst))
# join, then set loudness to -16 LUFS (Reels/TikTok) with ONE fixed gain for the whole clip. A plain loudnorm
# pass rides the level up in the pauses, which brings the café noise back, so measure first and apply linearly.
joined = tmp + "/joined.mov"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", tmp + "/list.txt", "-c", "copy", joined], check=True)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", joined, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
m = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
LN = (f"loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
      f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-c:v", "copy", "-af", LN,
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out], check=True)
t = 0; seg = []
for a, b in keep: seg.append({"src": [a, b], "out": [round(t, 3), round(t + b - a, 3)]}); t += b - a
json.dump(seg, open(out.replace(".mp4", ".segs.json"), "w"), indent=1); print("total", round(t, 2))
