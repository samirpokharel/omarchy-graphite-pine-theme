# Wallpapers 4-9: themed topographic variants (summit, ridgeline, sparse, dense, valley, glow).
# Usage: python3 topo-variants.py <output-dir>
# Topographic variants in the style of 2-topographic: graphite base, pine minor
# contours, accent every 5th. Each variant changes terrain, density or framing.
import numpy as np, sys, os
from PIL import Image
OUT=sys.argv[1]; W,H=3840,2160
def hx(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],np.float32)
BG,DARK,PINE,ACC,MUTED=map(hx,["#121513","#0a0c0b","#244a33","#4f8f63","#3b443e"])
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def base(vig=1.3):
    d=np.hypot((xx-W/2)/W,(yy-H/2)/H); t=np.clip(d*vig,0,1)[...,None]
    return BG*(1-t)+DARK*t
def blend(img,col,a): a=np.clip(a,0,1)[...,None]; return img*(1-a)+col*a
def lm(dist,w): return np.clip(w-np.abs(dist)+0.5,0,1)
def hills(rng,n,smin,smax,neg=True,box=(-0.1,1.1,-0.1,1.1)):
    f=np.zeros((H,W),np.float32)
    for _ in range(n):
        px=rng.uniform(box[0],box[1])*W; py=rng.uniform(box[2],box[3])*H
        sx=rng.uniform(smin,smax)*W; sy=sx*rng.uniform(0.6,1.5)
        a=rng.uniform(0.4,1.2)*(rng.choice([1,1,-0.6]) if neg else 1)
        f+=a*np.exp(-(((xx-px)/sx)**2+((yy-py)/sy)**2)/2)
    return f
def contour(img,f,levels,minor=0.75,major=0.6,majw=1.2,every=5,minw=0.7,mask=None):
    v=f*levels; gy,gx=np.gradient(v); g=np.hypot(gx,gy)+1e-6
    dist=np.abs(((v+0.5)%1)-0.5)/g; idx=np.floor(v+0.5).astype(int)
    m=np.ones_like(f) if mask is None else mask
    img=blend(img,PINE,lm(dist,minw)*np.where(idx%every==0,0,minor)*m)
    img=blend(img,ACC,lm(dist,majw)*np.where(idx%every==0,major,0)*m)
    return img
def save(img,name,seed):
    r=np.random.default_rng(seed)
    img=np.clip(img+r.normal(0,1.2,img.shape),0,255).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(OUT,name),quality=94,subsampling=0)
    print("wrote",name)

# 4 — summit: one dominant peak, off-centre right, rings radiating out
r=np.random.default_rng(11)
f=1.6*np.exp(-(((xx-W*0.66)/(W*0.22))**2+((yy-H*0.48)/(W*0.17))**2)/2)+0.35*hills(r,10,0.06,0.18)
save(contour(base(),f,30),"4-topo-summit.jpg",1)

# 5 — ridgeline: long diagonal ridge, lines stream across the screen
r=np.random.default_rng(23)
ridge=(yy-H*0.55)+(xx-W/2)*-0.35
f=1.3*np.exp(-(ridge/(H*0.28))**2)+0.25*np.sin(xx/W*7+yy/H*1.5)*np.exp(-(ridge/(H*0.5))**2)+0.3*hills(r,8,0.08,0.2)
save(contour(base(),f,38),"5-topo-ridgeline.jpg",2)

# 6 — sparse: wide spacing, very calm, lots of empty graphite for the bar & windows
r=np.random.default_rng(5)
save(contour(base(1.5),hills(r,9,0.15,0.35),14,minor=0.85,major=0.75),"6-topo-sparse.jpg",3)

# 7 — dense: tight survey-map lines, darker so it stays quiet
r=np.random.default_rng(42)
f=hills(r,26,0.06,0.22)+0.12*np.sin(xx/W*4.3-yy/H*3.1)
save(contour(base(),f,70,minor=0.5,major=0.45,every=10,minw=0.6),"7-topo-dense.jpg",4)

# 8 — valley: terrain only along the bottom, fading out upward (clean top half)
r=np.random.default_rng(8)
f=hills(r,16,0.07,0.22,box=(-0.1,1.1,0.55,1.25))
fade=np.clip((yy/H-0.25)/0.45,0,1)**1.5
save(contour(base(),f,34,mask=fade),"8-topo-valley.jpg",5)

# 9 — glow: classic terrain with a soft pine light behind the highest peak
r=np.random.default_rng(3)
f=hills(r,20,0.08,0.28)
py,px=np.unravel_index(np.argmax(f[::8,::8]),f[::8,::8].shape)
img=blend(base(),PINE,np.exp(-(np.hypot(xx-px*8,yy-py*8)/(W*0.22))**2)*0.45)
save(contour(img,f,34),"9-topo-glow.jpg",6)
