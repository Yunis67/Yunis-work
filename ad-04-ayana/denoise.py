# Removes café noise from the lav recording before cutting. Learns the room from moments where nobody talks
# (both waiting on the AI), then spectral-gates it out (noisereduce, non-stationary: handles chatter and clatter).
# Works on both voices, including the AI coming out of the phone speaker.
# Run: python3 denoise.py ../raw/ayana-audio.m4a ../raw/ayana-audio-clean.wav
import sys, subprocess, wave
import numpy as np, noisereduce as nr
src, out = sys.argv[1:3]
SR = 48000
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
QUIET = [(13.5, 15.8), (47.9, 50.4), (71.1, 72.9), (78.0, 79.6)]   # audio-time gaps with only café sound
noise = np.concatenate([x[int(a * SR):int(b * SR)] for a, b in QUIET])
PROP = 0.9                       # how much of the noise to remove (1.0 starts to sound watery)
y = nr.reduce_noise(y=x, sr=SR, y_noise=noise, stationary=False, prop_decrease=PROP)
with wave.open(out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
print("wrote", out)
