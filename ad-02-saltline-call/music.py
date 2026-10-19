# Original background track, synthesized from scratch (no licence needed).
# Soft tech-ad bed: pad chords, plucked arpeggio, sub bass, light kick and hats.
# Silent during the call; fades in on the last line and swells into the end banner. Writes music.wav.
# Run: python3 music.py <clip length> <end card length> <swell start>
import sys, wave
import numpy as np

CLIP, END, SWELL = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
SR, BPM = 48000, 104
DUR = CLIP + END
n = int(DUR * SR)
t = np.arange(n) / SR
beat = 60 / BPM
bar = 4 * beat
rng = np.random.default_rng(7)  # fixed seed so the track is identical every run

def midi(m): return 440 * 2 ** ((m - 69) / 12)

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y

# A minor → F → C → G, one bar each
CHORDS = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]
ROOTS = [45, 41, 36, 43]

out = np.zeros(n)

# pad: detuned saws, filtered, slow swell per chord
pad = np.zeros(n)
for k in range(int(DUR / bar) + 1):
    s, e = int(k * bar * SR), min(n, int((k + 1) * bar * SR) + int(0.3 * SR))
    if s >= n: break
    tt = np.arange(e - s) / SR
    env = np.minimum(1, tt / 0.6) * np.exp(-np.maximum(0, tt - bar) / 0.25)
    for m in CHORDS[k % 4]:
        for d in (-0.08, 0.08):
            f = midi(m) * 2 ** (d / 12)
            pad[s:e] += env * (2 * ((tt * f) % 1) - 1) * 0.06
pad = lowpass(pad, 900)

# pluck arpeggio on 8th notes
arp = np.zeros(n)
pattern = [0, 2, 1, 3, 2, 1, 3, 2]
for k in range(int(DUR / (beat / 2)) + 1):
    s = int(k * beat / 2 * SR)
    if s >= n: break
    chord = CHORDS[int(k * beat / 2 / bar) % 4]
    f = midi(chord[pattern[k % 8]] + 12)
    L = min(n - s, int(0.45 * SR)); tt = np.arange(L) / SR
    arp[s:s + L] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.12) * 0.16 + np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.05) * 0.04

# sub bass on beats 1 and 3
bass = np.zeros(n)
for k in range(int(DUR / (2 * beat)) + 1):
    s = int(k * 2 * beat * SR)
    if s >= n: break
    f = midi(ROOTS[int(k * 2 * beat / bar) % 4])
    L = min(n - s, int(2 * beat * SR)); tt = np.arange(L) / SR
    bass[s:s + L] += np.sin(2 * np.pi * f * tt) * np.minimum(1, tt / 0.02) * np.exp(-tt / 0.6) * 0.22

# kick on every beat, hats on the off-beats (drums come in after the first bar)
drums = np.zeros(n)
for k in range(4, int(DUR / beat) + 1):
    s = int(k * beat * SR)
    if s >= n: break
    L = min(n - s, int(0.3 * SR)); tt = np.arange(L) / SR
    ph = 2 * np.pi * (45 * tt + (110 / 18) * (1 - np.exp(-18 * tt)))
    drums[s:s + L] += np.sin(ph) * np.exp(-tt / 0.11) * 0.38
    h = int((k + 0.5) * beat * SR)
    if h < n:
        L = min(n - h, int(0.06 * SR)); noise = rng.standard_normal(L)
        noise = noise - lowpass(noise, 6000)
        drums[h:h + L] += noise * np.exp(-np.arange(L) / SR / 0.018) * 0.12

out = pad + arp + bass + drums
out /= np.max(np.abs(out)) + 1e-9

# level: silent under the call, smooth S-curve rise from SWELL into the banner (about -9 dBFS)
high = 10 ** (-9 / 20)
g = np.zeros(n)
ramp = (t >= SWELL) & (t < CLIP)
x = (t[ramp] - SWELL) / (CLIP - SWELL)
g[ramp] = high * (0.5 - 0.5 * np.cos(np.pi * x))
g[t >= CLIP] = high
fade = t > DUR - 0.9
g[fade] *= (DUR - t[fade]) / 0.9
out *= g

st = np.stack([out, np.roll(out, int(0.012 * SR)) * 0.92], axis=1)  # slight width
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("music.wav", round(DUR, 2), "s")
