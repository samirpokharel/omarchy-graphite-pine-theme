# topo-live.mp4 (1920x1080, 30 fps, 30 s seamless loop). Needs ffmpeg.
# Usage: python3 live-wallpaper.py <out.mp4>    env: W H FPS SECS SEED
#        python3 live-wallpaper.py <frame.png> 0 450   renders still frames
# Live topographic wallpaper: same look as 2-topographic, animated as a
# seamless loop. Contour levels drift by exactly 5 steps per loop (so the
# accent every-5th line lands back on itself) while each hill orbits a small
# circle — both periodic, so frame N wraps into frame 0 with no seam.
import numpy as np, sys, os, subprocess
from multiprocessing import Pool
W,H=int(os.environ.get("W",1920)),int(os.environ.get("H",1080))
FPS=int(os.environ.get("FPS",30)); SECS=int(os.environ.get("SECS",30)); N=FPS*SECS
SEED=int(os.environ.get("SEED",404))
def hx(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],np.float32)
BG,DARK,PINE,ACC=map(hx,["#121513","#0a0c0b","#244a33","#4f8f63"])
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
d=np.hypot((xx-W/2)/W,(yy-H/2)/H); t=np.clip(d*1.3,0,1)[...,None]; BASE=BG*(1-t)+DARK*t
rng=np.random.default_rng(SEED)
HILLS=[]
for _ in range(22):
    px,py=rng.uniform(-0.1,1.1),rng.uniform(-0.1,1.1)
    s=rng.uniform(0.08,0.3); a=rng.uniform(0.4,1.2)*rng.choice([1,1,-0.6])
    HILLS.append((px,py,s,a,rng.uniform(0,6.283),rng.uniform(0.012,0.03),rng.choice([-1,1])))
PH=rng.uniform(0,6.28)
DITHER=np.random.default_rng(1).normal(0,1.0,(H,W,1)).astype(np.float32)  # fixed: no flicker
LW=W/1920  # line widths are tuned at 1080p
def blend(img,col,a): a=np.clip(a,0,1)[...,None]; return img*(1-a)+col*a
def lm(dist,w): return np.clip(w-np.abs(dist)+0.5,0,1)
def frame(i):
    tau=2*np.pi*i/N
    f=np.zeros((H,W),np.float32)
    for px,py,s,a,ph,r,dirn in HILLS:
        cx=(px+r*np.cos(dirn*tau+ph))*W; cy=(py+r*np.sin(dirn*tau+ph))*H; sw=s*W
        f+=a*np.exp(-((xx-cx)**2+(yy-cy)**2)/(2*sw*sw))
    f+=0.15*np.sin(xx/W*5.1+yy/H*2.3+PH+0.0*tau)
    v=f*34-5*i/N
    gy,gx=np.gradient(v); g=np.hypot(gx,gy)+1e-6
    dist=np.abs(((v+0.5)%1)-0.5)/g; major=(np.floor(v+0.5).astype(int)%5==0)
    img=blend(BASE,PINE,lm(dist,0.8*LW)*np.where(major,0,0.75))
    img=blend(img,ACC,lm(dist,1.1*LW)*np.where(major,0.6,0))
    return np.clip(img+DITHER,0,255).astype(np.uint8).tobytes()
if __name__=="__main__":
    out=sys.argv[1]
    if out.endswith(".png"):   # preview mode: frames listed in argv[2:]
        from PIL import Image
        for k in sys.argv[2:]:
            Image.frombytes("RGB",(W,H),frame(int(k))).save(out.replace(".png",f"-{k}.png"))
        sys.exit()
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p","-profile:v","high","-x264-params","ipratio=1.0:pbratio=1.0:keyint=150:min-keyint=150","-movflags","+faststart",out],stdin=subprocess.PIPE)
    with Pool(max(1,os.cpu_count()-1)) as p:
        for k,b in enumerate(p.imap(frame,range(N),chunksize=4)):
            ff.stdin.write(b)
            if k%150==0: print(f"frame {k}/{N}",flush=True)
    ff.stdin.close(); ff.wait(); print("done",out)
