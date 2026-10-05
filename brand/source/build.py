import math, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

P = dict(
  top=13.5, bot_bar=19.0, bot_bar2=24.5,      # top bar: grey 13.5-19, purple 19-24.5
  cx=54.8, cy=29.0, r_in=4.5, r_mid=10.0, r_out=15.5,
  cut=0.5,                                     # main-bar left cut slope dx/dy
  main_x=46.0,                                 # main bar cut at y=top
  leg=0.6,                                     # leg slope dx/dy
  legL=(41.0, 33.5),                           # purple outer (left) line passes here
  legR_p=(54.0, 44.0),                         # purple/grey boundary line on the leg
  legR_g=(67.5, 57.5),                         # grey right edge on the leg
  foot=57.5,
  # slash
  s_x0=28.0, s_cut=0.5, s_rx0=41.0, s_rcut=0.59, s_split=((29.05,15.6),(44.2,19.0)),
)
PURPLE="#5B4BCE"; GREY="#737373"

def lx(pt, slope, y):  # x on a line through pt with dx/dy slope at height y
    return pt[0] + slope*(y-pt[1])

def mark_paths(p=P):
    cx,cy=p['cx'],p['cy']; ri,rm,ro=p['r_in'],p['r_mid'],p['r_out']
    T,B1,B2=p['top'],p['bot_bar'],p['bot_bar2']
    cut=lambda y: p['main_x']+p['cut']*(y-T)
    yb_in, yb_mid, yb_out = cy+ri, cy+rm, cy+ro
    f=p['foot']
    # purple: main bar + bowl + middle bar + leg (one shape)
    xr39 = lx(p['legR_p'],p['leg'],yb_mid)
    purple = (f"M{cut(B1):.3f},{B1} L{cx},{B1} A{rm},{rm} 0 0 1 {cx},{yb_mid} "
              f"L{xr39:.3f},{yb_mid} L{lx(p['legR_p'],p['leg'],f):.3f},{f} "
              f"L{lx(p['legL'],p['leg'],f):.3f},{f} L{p['legL'][0]},{p['legL'][1]} "
              f"L{cx},{yb_in} A{ri},{ri} 0 0 0 {cx},{B2} L{cut(B2):.3f},{B2} Z")
    # grey: outer lane. Intersect outer circle with the leg's right edge line.
    lo,hi=cy,yb_out
    g=lambda y:(lx(p['legR_g'],p['leg'],y)-cx)**2+(y-cy)**2-ro**2
    for _ in range(60):
        m=(lo+hi)/2
        (lo,hi)=(m,hi) if g(m)<0 else (lo,m)
    yi=(lo+hi)/2; xi=lx(p['legR_g'],p['leg'],yi)
    grey = (f"M{cut(T):.3f},{T} L{cx},{T} A{ro},{ro} 0 0 1 {xi:.3f},{yi:.3f} "
            f"L{lx(p['legR_g'],p['leg'],f):.3f},{f} L{lx(p['legR_p'],p['leg'],f):.3f},{f} "
            f"L{xr39:.3f},{yb_mid} L{cx},{yb_mid} A{rm},{rm} 0 0 0 {cx},{B1} L{cut(B1):.3f},{B1} Z")
    # slash: block top..B2, left cut and right cut, split diagonally
    (ax,ay),(bx,by)=p['s_split']
    sl=lambda y: p['s_x0']+p['s_cut']*(y-T)
    sr=lambda y: p['s_rx0']+p['s_rcut']*(y-T)
    s_grey=f"M{sl(T):.3f},{T} L{sr(T):.3f},{T} L{bx:.3f},{by:.3f} L{ax:.3f},{ay:.3f} Z"
    s_purp=f"M{ax:.3f},{ay:.3f} L{bx:.3f},{by:.3f} L{sr(B2):.3f},{B2} L{sl(B2):.3f},{B2} Z"
    return [(grey,GREY),(s_grey,GREY),(purple,PURPLE),(s_purp,PURPLE)]

def word_path(font, size, x0, baseline, text="RezFlo", track=0.0):
    f=TTFont(font); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
    s=size/upm; x=x0; out=[]; hmtx=f['hmtx']
    kern={}
    for ch in text:
        gn=cmap[ord(ch)]
        pen=SVGPathPen(gs)
        tp=TransformPen(pen,(s,0,0,-s,x,baseline))
        gs[gn].draw(tp); out.append(pen.getCommands())
        x+=hmtx[gn][0]*s+track*size
    return " ".join(out), x

def width_of(font,size,text="RezFlo"):
    f=TTFont(font); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
    return sum(f['hmtx'][cmap[ord(c)]][0] for c in text)*size/upm

def svg(font, size, wx, base, mark=True, word=True, vb=(0,0,98,90), bg=None, track=0.0):
    parts=[]
    if bg: parts.append(f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{bg}"/>')
    if mark:
        for d,c in mark_paths(): parts.append(f'<path d="{d}" fill="{c}"/>')
    if word:
        d,_=word_path(font,size,wx,base,track=track); parts.append(f'<path d="{d}" fill="{PURPLE}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}">'+"".join(parts)+'</svg>'
