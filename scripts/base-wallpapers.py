# Wallpapers 1-3: geometric, topographic (the original), grain.
# Usage: python3 base-wallpapers.py <output-dir>
import numpy as np, sys, os
from PIL import Image
OUT=sys.argv[1]; W,H=3840,2160
rng=np.random.default_rng(7)
def hx(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],float)
BG,DARK,PINE,ACC,FG,MUTED=map(hx,["#121513","#0a0c0b","#244a33","#4f8f63","#c3cac4","#3b443e"])
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def save(img,name):
    img=np.clip(img+rng.normal(0,1.2,img.shape),0,255).astype(np.uint8)  # dither, kills banding
    Image.fromarray(img).save(os.path.join(OUT,name.replace('.png','.jpg')),quality=94,subsampling=0)
def base():  # gentle vignette over graphite
    d=np.hypot((xx-W/2)/W,(yy-H/2)/H)
    t=np.clip(d*1.3,0,1)[...,None]
    return BG*(1-t)+DARK*t
def blend(img,col,a): a=np.clip(a,0,1)[...,None]; return img*(1-a)+col*a
def line_mask(dist,w): return np.clip(w-np.abs(dist)+0.5,0,1)  # 1px AA

# 1 — geometric: dot grid, one large ring, a few precise lines, a single accent square
img=base()
g=96; dx=(xx%g)-g/2; dy=(yy%g)-g/2
img=blend(img,MUTED,np.clip(1.6-np.hypot(dx,dy),0,1)*0.55)
cx,cy,R=W*0.68,H*0.52,H*0.36
r=np.hypot(xx-cx,yy-cy)
img=blend(img,PINE,line_mask(r-R,1.5))
img=blend(img,PINE,line_mask(r-R*0.62,0.8)*0.6)
img=blend(img,ACC,line_mask(r-R*1.18,0.8)*0.35*((xx>cx)&(yy<cy)))
img=blend(img,PINE,line_mask(yy-cy,0.8)*(xx>W*0.08)*(xx<W*0.92)*0.7)
img=blend(img,PINE,line_mask((xx-cx)+(yy-cy)*0.0,0.8)*(yy>H*0.1)*(yy<H*0.9)*0.4)
sq=(np.abs(xx-(cx+R))<10)&(np.abs(yy-cy)<10)
img=blend(img,ACC,sq.astype(float))
save(img,"1-geometric.png")

# 2 — topographic: smooth field from summed gaussian hills, contoured
f=np.zeros((H,W),np.float32)
for _ in range(22):
    px,py=rng.uniform(-0.1,1.1)*W,rng.uniform(-0.1,1.1)*H
    s=rng.uniform(0.08,0.3)*W; a=rng.uniform(0.4,1.2)*rng.choice([1,1,-0.6])
    f+=a*np.exp(-((xx-px)**2+(yy-py)**2)/(2*s*s))
f+=0.15*np.sin(xx/W*5.1+yy/H*2.3)
levels=34; v=f*levels
gy,gx=np.gradient(v); grad=np.hypot(gx,gy)+1e-6
dist=(np.abs(((v+0.5)%1)-0.5))/grad          # pixel distance to nearest contour
idx=np.floor(v+0.5).astype(int)
major=(idx%5==0)
img=base()
img=blend(img,PINE,line_mask(dist,0.7)*np.where(major,0,0.75))
img=blend(img,ACC,line_mask(dist,1.2)*np.where(major,0.6,0))
save(img,"2-topographic.png")

# 3 — grain + gradient: pine glow rising from lower-left, heavy film grain
img=base()
d=np.hypot((xx-W*0.15)/W,(yy-H*1.05)/H*1.4)
glow=np.exp(-(d/0.55)**2)
img=blend(img,PINE,glow*0.85)
img=blend(img,ACC,np.exp(-(d/0.22)**2)*0.35)
grain=rng.normal(0,7,(H,W)).astype(np.float32)[...,None]
img=img+grain
save(img,"3-grain.png")
