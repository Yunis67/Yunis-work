# Cuts the Joudy pickup call into clip.mp4 (1080x1920, 30 fps).
# Sound comes from the separate recording (raw-audio.m4a); picture from the phone video (raw-video.mp4).
# The video runs OFFSET seconds behind the audio file (measured by cross-correlation, constant, no drift).
# Spans are (first word start, last word end) in AUDIO time. Pauses between turns are kept up to CAP seconds.
# Run: python3 denoise.py ../raw/joudy-audio.m4a ../raw/joudy-audio-clean.wav
#      python3 cut.py ../raw/joudy-video.mp4 ../raw/joudy-audio-clean.wav clip.mp4 <tmp dir>
import subprocess, sys, json, os
vsrc, asrc, out, tmp = sys.argv[1:5]
OFFSET = 2.645
spans = [
    (10.88, 14.90),   # 0  AI: Hey, thanks for calling ... how may I help you?
    (15.32, 17.18),   # 1  Hi, can I place an order for a pickup, please?
    (19.42, 22.10),   # 2  AI: Absolutely. What name should I put the order under?
    (22.68, 23.54),   # 3  That would be Emily.
                      #    CUT 25.2-46.0: phone number ask, number, read-back (a real-looking number; keep it out of an ad)
    (46.26, 48.66),   # 4  AI: Great. What can I get started for you?
    (49.02, 51.42),   # 5  Can I get two original shawarmas, please?
                      #    CUT 51.4-73.0: the AI stalls ("I'm not familiar with...") and she repeats the order
    (73.12, 87.68),   # 6  AI: I want to make sure I get this right ... one of each?
    (89.24, 90.44),   # 7  I'll get one of each.   ("Okay. Um..." trimmed)
    (93.02, 99.02),   # 8  AI: You got it ... Anything else for you?
    (99.44, 101.30),  # 9  Can I get a side of fries?
    (103.52, 106.22), # 10 AI: small or large?
    (106.64, 107.86), # 11 Can I get a large fries?
    (109.46, 112.36), # 12 AI: Perfect. One large fries. Anything else?
    (112.82, 114.44), # 13 No, that would be everything. Thank you.
    (116.24, 118.74), # 14 AI: What time would you like that ready?
    (119.38, 120.74), # 15 In about 30 minutes.
    (123.26, 129.12), # 16 AI: Got it ... allergies?
    (129.88, 131.66), # 17 No, that is everything.
    (133.84, 143.68), # 18 AI: Alright, Emily. Let me confirm everything ... 30 minutes.
                      #    CUT 143.9-148.3: read-back of the phone number
    (149.32, 150.96), # 19 AI: Does everything sound correct?
    (151.34, 153.02), # 20 Yes, everything sounds perfect.
    (156.54, 159.56), # 21 AI: Thank you.  Her: Oh my god, that's so cool!
]
removed_after = {3, 5, 18}          # a chunk of the call was cut between span i and i+1
CAP, JUMP = 0.7, 0.5                # longest pause kept between turns; pause used across a cut
OUTRO = 1.0                         # roll on after "so cool!" while her voice fades
INTRO = (157.52, 159.95)            # cold open: "Oh my god, that's so cool!" plays first as the hook
keep = [INTRO]
for i, (a, b) in enumerate(spans):
    lead = 0.3 if i == 0 else (JUMP if i - 1 in removed_after else min(a - spans[i-1][1], CAP)) / 2
    tail = OUTRO if i == len(spans) - 1 else (JUMP if i in removed_after else min(spans[i+1][0] - b, CAP)) / 2
    if i == 7: lead = -0.31         # "Um" runs to 89.45, short dip, "I'll" starts 89.65: cut in the dip
    if i == 18: tail = 0.12         # stop before "That's under Emily, with phone number..."
    if i == 19: lead = 0.0          # the number's last digits run right up to "Does"
    keep.append((round(a - lead, 3), round(b + tail, 3)))

# Café noise is removed first by denoise.py (pass its output as the audio file). Here: trim rumble and hiss,
# a soft gate that lowers whatever room is left between words (~14 dB, never to silence), then even levels.
CLEAN = "highpass=f=90,lowpass=f=12000,agate=threshold=0.015:ratio=2:range=0.2:attack=5:release=200,"
LEVEL = "acompressor=threshold=0.12:ratio=2.5:attack=10:release=150:makeup=1.6,"
# phone export is 320x568: scale up cleanly to 1080x1920 with a light sharpen
VF = "scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0,format=yuv420p"
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
        "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-r", "30",
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
