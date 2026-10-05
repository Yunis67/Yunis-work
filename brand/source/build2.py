import math
from build import word_path
PURPLE="#5B4BCE"; GREY="#737373"
# Constrained design: one cut angle (slope s = dx/dy) everywhere, lanes the same width on bar, bowl and leg.
Q=dict(cx=55.3, cy=29.0, r_in=4.62, r_mid=10.75, r_out=15.5, s=0.6,
       main_x=44.9,            # main-bar cut, x at the top edge
       leg_x=39.6,             # leg outer edge, x at the middle bar's top edge (y = cy + r_in)
       foot=58.0,
       s_x0=27.4, s_rx0=39.0,  # slash left/right cut, x at the top edge
       s_yl=15.85, s_yr=19.5)  # slash purple/grey split: y where it meets the left and right cuts
def paths(q=Q):
    cx,cy,ri,rm,ro,s=q['cx'],q['cy'],q['r_in'],q['r_mid'],q['r_out'],q['s']
    T=cy-ro; B1=cy-rm; B2=cy-ri; Yi=cy+ri; Ym=cy+rm; f=q['foot']
    k=math.sqrt(1+s*s)                      # horizontal width per unit of perpendicular width
    L=lambda y: q['leg_x']+s*(y-Yi)         # leg outer edge (purple, left)
    Mp=lambda y: L(y)+(rm-ri)*k             # purple/grey boundary on the leg
    G=lambda y: L(y)+(ro-ri)*k              # grey outer edge on the leg
    cut=lambda y: q['main_x']+s*(y-T)
    # where the grey leg edge meets the outer circle
    lo,hi=cy,cy+ro
    g=lambda y:(G(y)-cx)**2+(y-cy)**2-ro**2
    for _ in range(80):
        m=(lo+hi)/2; (lo,hi)=(m,hi) if g(m)<0 else (lo,m)
    yi=(lo+hi)/2; xi=G(yi)
    purple=(f"M{cut(B1):.3f},{B1:.3f} L{cx:.3f},{B1:.3f} A{rm:.3f},{rm:.3f} 0 0 1 {cx:.3f},{Ym:.3f} "
            f"L{Mp(Ym):.3f},{Ym:.3f} L{Mp(f):.3f},{f:.3f} L{L(f):.3f},{f:.3f} L{L(Yi):.3f},{Yi:.3f} "
            f"L{cx:.3f},{Yi:.3f} A{ri:.3f},{ri:.3f} 0 0 0 {cx:.3f},{B2:.3f} L{cut(B2):.3f},{B2:.3f} Z")
    grey=(f"M{cut(T):.3f},{T:.3f} L{cx:.3f},{T:.3f} A{ro:.3f},{ro:.3f} 0 0 1 {xi:.3f},{yi:.3f} "
          f"L{G(f):.3f},{f:.3f} L{Mp(f):.3f},{f:.3f} L{Mp(Ym):.3f},{Ym:.3f} L{cx:.3f},{Ym:.3f} "
          f"A{rm:.3f},{rm:.3f} 0 0 0 {cx:.3f},{B1:.3f} L{cut(B1):.3f},{B1:.3f} Z")
    sl=lambda y: q['s_x0']+s*(y-T); sr=lambda y: q['s_rx0']+s*(y-T)
    a=(sl(q['s_yl']),q['s_yl']); b=(sr(q['s_yr']),q['s_yr'])
    s_grey=f"M{sl(T):.3f},{T:.3f} L{sr(T):.3f},{T:.3f} L{b[0]:.3f},{b[1]:.3f} L{a[0]:.3f},{a[1]:.3f} Z"
    s_purp=f"M{a[0]:.3f},{a[1]:.3f} L{b[0]:.3f},{b[1]:.3f} L{sr(B2):.3f},{B2:.3f} L{sl(B2):.3f},{B2:.3f} Z"
    return [(grey,GREY),(s_grey,GREY),(purple,PURPLE),(s_purp,PURPLE)]
def svg(q, font, size, x0, base, bg=None, vb=(0,0,98,90)):
    parts=[f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{bg}"/>'] if bg else []
    parts+=[f'<path d="{d}" fill="{c}"/>' for d,c in paths(q)]
    d,_=word_path(font,size,x0,base); parts.append(f'<path d="{d}" fill="{PURPLE}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}">'+"".join(parts)+'</svg>'
