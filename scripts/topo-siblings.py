# Wallpapers 10-15: same recipe as 2-topographic, different terrain per seed.
# Usage: python3 topo-siblings.py <output-dir> 404 606 707 202 303 909
# Close siblings of 2-topographic: identical recipe (22 hills, sin wave, 34
# levels, accent every 5th), only the seed — and so the terrain — changes.
import numpy as np, sys, os
from PIL import Image
OUT=sys.argv[1]; seeds=[int(s) for s in sys.argv[2:]]; W,H=3840,2160
def hx(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],np.float32)
BG,DARK,PINE,ACC=map(hx,["#121513","#0a0c0b","#244a33","#4f8f63"])
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
d=np.hypot((xx-W/2)/W,(yy-H/2)/H); t=np.clip(d*1.3,0,1)[...,None]; BASE=BG*(1-t)+DARK*t
def blend(img,col,a): a=np.clip(a,0,1)[...,None]; return img*(1-a)+col*a
def lm(dist,w): return np.clip(w-np.abs(dist)+0.5,0,1)
for seed in seeds:
    rng=np.random.default_rng(seed)
    f=np.zeros((H,W),np.float32)
    for _ in range(22):
        px,py=rng.uniform(-0.1,1.1)*W,rng.uniform(-0.1,1.1)*H
        s=rng.uniform(0.08,0.3)*W; a=rng.uniform(0.4,1.2)*rng.choice([1,1,-0.6])
        f+=a*np.exp(-((xx-px)**2+(yy-py)**2)/(2*s*s))
    ph=rng.uniform(0,6.28); f+=0.15*np.sin(xx/W*5.1+yy/H*2.3+ph)
    v=f*34; gy,gx=np.gradient(v); g=np.hypot(gx,gy)+1e-6
    dist=np.abs(((v+0.5)%1)-0.5)/g; major=(np.floor(v+0.5).astype(int)%5==0)
    img=blend(BASE,PINE,lm(dist,0.7)*np.where(major,0,0.75))
    img=blend(img,ACC,lm(dist,1.2)*np.where(major,0.6,0))
    img=np.clip(img+rng.normal(0,1.2,img.shape),0,255).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(OUT,f"seed-{seed}.jpg"),quality=94,subsampling=0)
    print("seed",seed)
