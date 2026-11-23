# Puts the AI-upscaled picture together with the cut's cleaned audio, and brightens it (the café footage is dim).
# Run: LOWRES=1 python3 cut.py ../raw/joudy-video.mp4 ../raw/joudy-audio-clean.wav clip-lo.mp4 <tmp>
#      python3 ../kit/upscale/upscale.py clip-lo.mp4 clip-up.mp4
#      python3 finish.py clip-up.mp4 clip-lo.mp4 clip.mp4
import sys, subprocess
up, lo, out = sys.argv[1:4]
GRADE = "eq=brightness=0.035:gamma=1.14:contrast=1.03:saturation=1.06,cas=0.35,format=yuv420p"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", up, "-i", lo, "-map", "0:v", "-map", "1:a", "-vf", GRADE,
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
    "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-r", "30", "-c:a", "copy", "-shortest", out], check=True)
print("wrote", out)
