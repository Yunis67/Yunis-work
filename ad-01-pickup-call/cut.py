# Cuts the raw call into clip.mp4. Spans are (first word start, last word end) in the raw recording.
# Pauses between turns are kept up to CAP seconds so the conversation still breathes.
import subprocess, sys, json, os
src, out, tmp = sys.argv[1], sys.argv[2], sys.argv[3]
spans = [(18.38,23.02),(24.56,24.92),(27.44,29.82),(31.62,34.32),(34.96,37.88),(41.46,46.92),(47.42,48.54),
         (55.24,60.72),(62.72,68.96),(70.94,73.14),(95.76,96.70),(104.80,108.54),(111.40,114.26),(119.20,120.45)]
CAP, JUMP = 0.75, 0.55   # max kept pause between consecutive turns; pause used where lines were removed
consec = {(0,1),(2,3),(3,4),(4,5),(5,6),(7,8),(8,9),(11,12)}  # pairs that were back to back in the raw call
keep = []
for i,(a,b) in enumerate(spans):
    if i == 0: lead = 0.3
    else:
        g = a - spans[i-1][1]
        lead = (min(g, CAP) if (i-1,i) in consec else JUMP) / 2
    if i == len(spans)-1: tail = 0.35
    else:
        g = spans[i+1][0] - b
        tail = (min(g, CAP) if (i,i+1) in consec else JUMP) / 2
    if i == 10: lead = 0.1   # "Perfect." ends at 95.56 just before; don't catch it
    keep.append((round(a-lead,3), round(b+tail,3)))
os.makedirs(tmp, exist_ok=True); lst=[]
# HDR (HLG) iPhone footage → SDR bt709 in the same pass
vf = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
for i,(a,b) in enumerate(keep):
    du=b-a; f=f"{tmp}/s{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{a}","-i",src,"-t",f"{du:.3f}","-vf",vf,
      "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
      "-af",f"afade=t=in:d=0.03,afade=t=out:st={du-0.04:.3f}:d=0.04","-c:v","libx264","-crf","14","-preset","fast","-r","30",
      "-c:a","aac","-b:a","192k","-ar","48000",f],check=True)
    lst.append(f"file '{f}'")
open(tmp+"/list.txt","w").write("\n".join(lst))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",tmp+"/list.txt","-c","copy",out],check=True)
t=0; seg=[]
for a,b in keep: seg.append({"src":[a,b],"out":[round(t,3),round(t+b-a,3)]}); t+=b-a
json.dump(seg,open(out.replace(".mp4",".segs.json"),"w"),indent=1); print("total",round(t,2))
