# Cuts the raw SaltLine call into clip.mp4.
# Video: brightened (the raw is dim and warm), 8-bit SDR. Audio: taken from the cleaned full-length track.
# Spans are (first word start, last word end) of each speaking turn in the raw recording;
# pauses between turns are kept up to CAP seconds so the conversation still breathes.
# Run: python3 cut.py <raw.mp4> <clean.wav> clip.mp4 <tmp dir>
import subprocess, sys, json, os
src, clean, out, tmp = sys.argv[1:5]
spans = [(4.26,7.36),(7.54,9.26),(11.52,14.78),(14.94,16.94),(19.28,22.00),(22.64,24.42),(25.98,30.52),
         (31.14,36.88),(39.86,42.96),(43.22,46.62),(49.42,57.28),(57.74,59.54),(61.06,64.34),(64.60,65.42),
         (67.98,71.64),(71.92,72.92),(75.36,79.44),(79.88,80.98),(82.06,82.54),(84.18,94.04),(94.28,95.00),
         (97.48,103.80),(106.26,107.86),(110.62,121.02),(121.36,122.86),(125.36,128.40)]
CAP = 0.7        # longest pause kept between turns (the AI's wait before answering gets trimmed to this)
LEAD, OUTRO = 0.25, 1.2
GRADE = "eq=gamma=1.15:brightness=0.03:contrast=1.05:saturation=0.98,colorbalance=rs=-0.03:bs=0.03,format=yuv420p"
keep = []
for i, (a, b) in enumerate(spans):
    lead = LEAD if i == 0 else min(a - spans[i-1][1], CAP) / 2
    tail = OUTRO if i == len(spans)-1 else min(spans[i+1][0] - b, CAP) / 2
    keep.append((round(a - lead, 3), round(b + tail, 3)))
os.makedirs(tmp, exist_ok=True); lst = []
for i, (a, b) in enumerate(keep):
    du = b - a; f = f"{tmp}/s{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{a}","-i",src,"-ss",f"{a}","-i",clean,"-t",f"{du:.3f}",
        "-map","0:v","-map","1:a","-vf",GRADE,"-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
        "-af",f"afade=t=in:d=0.03,afade=t=out:st={du-(1.0 if i == len(keep)-1 else 0.04):.3f}:d={0.95 if i == len(keep)-1 else 0.04}","-c:v","libx264","-crf","14","-preset","fast","-r","30",
        "-c:a","aac","-b:a","192k","-ar","48000",f], check=True)
    lst.append(f"file '{f}'")
open(tmp + "/list.txt", "w").write("\n".join(lst))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",tmp+"/list.txt","-c","copy",out], check=True)
t = 0; seg = []
for a, b in keep: seg.append({"src": [a, b], "out": [round(t, 3), round(t + b - a, 3)]}); t += b - a
json.dump(seg, open(out.replace(".mp4", ".segs.json"), "w"), indent=1); print("total", round(t, 2))
