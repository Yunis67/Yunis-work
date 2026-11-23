# Finds where speech really starts/ends near each span edge, from the cleaned audio's loudness (20 ms windows).
# Whisper's word times can be ~0.3 s off; cut points should sit in real silence.
import subprocess, sys, json, numpy as np
SR = 16000; W = 320; TH = -36            # dB: cleaned room sits near -50, voices near -20
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                  capture_output=True).stdout, np.int16).astype(np.float32) / 32768
db = 20 * np.log10(np.sqrt((x[:len(x)//W*W].reshape(-1, W)**2).mean(1)) + 1e-9)
def loud(t0, t1): return [i * W / SR for i in range(int(t0*SR/W), int(t1*SR/W)) if db[i] >= TH]
spans = json.loads(sys.argv[2])
for k, (a, b) in enumerate(spans):
    lo = spans[k-1][1] if k else a - 1.0; hi = spans[k+1][0] if k + 1 < len(spans) else b + 1.0
    on = loud((lo + a) / 2, a + 0.4); off = loud(b - 0.4, (b + hi) / 2)
    print(k, "start", a, "->", round(on[0], 2) if on else None, "| end", b, "->", round(off[-1] + W/SR, 2) if off else None)
