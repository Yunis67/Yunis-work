# AI upscale (Real-ESRGAN "realesr-general-x4v3", BSD-3 licence) for low-res phone footage, on CPU.
# Reads frames from a video, upscales 4x, scales to 1080x1920, writes a new video (no audio).
# Run: python3 upscale.py <in.mp4> <out.mp4> [start s] [duration s]
import sys, subprocess, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F

class SRVGGNetCompact(nn.Module):      # the network Real-ESRGAN uses for its small "general" model
    def __init__(self, nf=64, nc=32, scale=4):
        super().__init__()
        self.scale = scale
        self.body = nn.ModuleList([nn.Conv2d(3, nf, 3, 1, 1), nn.PReLU(nf)])
        for _ in range(nc): self.body.extend([nn.Conv2d(nf, nf, 3, 1, 1), nn.PReLU(nf)])
        self.body.append(nn.Conv2d(nf, 3 * scale * scale, 3, 1, 1))
        self.up = nn.PixelShuffle(scale)
    def forward(self, x):
        out = x
        for m in self.body: out = m(out)
        return self.up(out) + F.interpolate(x, scale_factor=self.scale, mode="nearest")

src, dst = sys.argv[1], sys.argv[2]
extra = ["-ss", sys.argv[3], "-t", sys.argv[4]] if len(sys.argv) > 4 else []
W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(","))
net = SRVGGNetCompact()
sd = torch.load(__file__.replace("upscale.py", "realesr-general-x4v3.pth"), map_location="cpu")
net.load_state_dict(sd.get("params", sd)); net.eval()
torch.set_num_threads(4)
rd = subprocess.Popen(["ffmpeg", "-v", "error", *extra, "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W*4}x{H*4}", "-r", "30", "-i", "-",
                       "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "14", "-preset", "fast", dst], stdin=subprocess.PIPE)
n, t0 = 0, time.time()
with torch.inference_mode():
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        x = torch.from_numpy(np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()).permute(2, 0, 1)[None].float() / 255
        y = net(x).clamp(0, 1)[0].permute(1, 2, 0).mul(255).round().byte().numpy()
        wr.stdin.write(y.tobytes()); n += 1
        if n % 30 == 0: print(f"{n} frames, {(time.time()-t0)/n:.2f} s/frame", flush=True)
wr.stdin.close(); wr.wait(); print("done", n, "frames")
