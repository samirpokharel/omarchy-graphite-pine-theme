# The theme-picker preview.png (synthetic desktop: editor, terminal, palette).
# Usage: python3 preview.py <theme-dir>   (needs JetBrainsMono Nerd Font)
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
T=sys.argv[1]; W,H=1800,1012
F="/usr/share/fonts/TTF/JetBrainsMonoNerdFont-%s.ttf"
f=ImageFont.truetype(F%"Regular",19); fb=ImageFont.truetype(F%"Bold",19); fs=ImageFont.truetype(F%"Regular",15)
C=dict(bg="#121513",dark="#0e100f",acc="#4f8f63",pine="#244a33",fg="#c3cac4",dfg="#6e7870",bfg="#e9eeea",muted="#3b443e",
 red="#a8786d",yellow="#a9b89f",orange="#94a283",green="#5f9e72",cyan="#6fa596",blue="#7fb08d",magenta="#8fa89a",bgreen="#7fbf91")
img=Image.open(T+"/backgrounds/2-topographic.jpg").convert("RGB").resize((W,H),Image.LANCZOS)
d=ImageDraw.Draw(img)
# bar
d.rectangle([0,0,W,30],fill=C["bg"])
for i in range(1,6):
    d.text((18+i*26-26,6),str(i),font=fs,fill=C["acc"] if i==1 else C["dfg"])
d.text((W/2-24,6),"11:15",font=fs,fill=C["fg"])
d.text((W-150,6),"  󰁹 87%",font=fs,fill=C["fg"])
def win(box,active):
    x0,y0,x1,y1=box
    d.rounded_rectangle(box,radius=0,fill=C["bg"],outline=C["acc"] if active else "#2a302c",width=2)
    return x0+22,y0+18
# left: code
x,y=win((14,44,1046,998),True)
code=[
 [("dfg","# graphite-pine / wallpapers.py")],
 [("magenta","import "),("fg","numpy "),("magenta","as "),("fg","np")],
 [],
 [("magenta","def "),("blue","contour"),("fg","(field, levels="),("orange","34"),("fg","):")],
 [("fg","    v = field * levels")],
 [("fg","    gy, gx = np."),("blue","gradient"),("fg","(v)")],
 [("fg","    dist = np."),("blue","abs"),("fg","(((v + "),("orange","0.5"),("fg",") % "),("orange","1"),("fg",") - "),("orange","0.5"),("fg",")")],
 [("magenta","    return "),("fg","dist / np."),("blue","hypot"),("fg","(gx, gy)")],
 [],
 [("fg","PALETTE = {")],
 [("green",'    "accent"'),("fg",": "),("green",'"#4f8f63"'),("fg",",")],
 [("green",'    "base"'),("fg",":   "),("green",'"#121513"'),("fg",",  "),("dfg","# graphite, faint green")],
 [("fg","}")],
 [],
 [("magenta","if "),("fg","__name__ == "),("green",'"__main__"'),("fg",":")],
 [("cyan","    print"),("fg","("),("yellow",'f"rendered {'),("fg","n"),("yellow",'} maps"'),("fg",")")],
]
for i,line in enumerate(code):
    d.text((x,y+i*30),f"{i+1:>3} ",font=f,fill=C["muted"])
    cx=x+52
    for col,txt in line:
        d.text((cx,y+i*30),txt,font=f,fill=C[col]); cx+=d.textlength(txt,font=f)
# status line
sy=y+len(code)*30+20
d.rectangle([x-8,sy,1030,sy+30],fill=C["dark"])
d.rectangle([x-8,sy,x+90,sy+30],fill=C["acc"]); d.text((x+4,sy+5),"NORMAL",font=fb,fill=C["bg"])
d.text((x+110,sy+5),"wallpapers.py",font=f,fill=C["fg"])
# right top: terminal
x,y=win((1060,44,1786,560),False)
lines=[[("acc","❯ "),("fg","ls")],
 [("blue","backgrounds/  "),("fg","colors.toml  icons.theme  shell.toml")],
 [("acc","❯ "),("fg","git status")],
 [("fg","On branch "),("bgreen","main")],
 [("green","  new:   "),("fg","colors.toml")],
 [("red","  del:   "),("fg","old-theme.toml")],
 [("yellow","  mod:   "),("fg","shell.toml")],
 [("acc","❯ "),("dfg","_")]]
for i,line in enumerate(lines):
    cx=x
    for col,txt in line:
        d.text((cx,y+i*32),txt,font=f,fill=C[col]); cx+=d.textlength(txt,font=f)
# palette strip
y=y+len(lines)*32+30
keys=["muted","dfg","fg","bfg","pine","acc","red","orange","yellow","green","cyan","blue","magenta"]
sw=(1786-22-x)/len(keys)
for i,k in enumerate(keys):
    d.rectangle([x+i*sw,y,x+(i+1)*sw-4,y+60],fill=C[k])
# right bottom: name card
x,y=win((1060,574,1786,998),False)
d.text((x,y+120),"Graphite Pine",font=ImageFont.truetype(F%"Bold",56),fill=C["bfg"])
d.text((x,y+200),"monochrome graphite · one pine accent",font=f,fill=C["dfg"])
d.rectangle([x,y+250,x+70,y+256],fill=C["acc"])
img.save(T+"/preview.png",optimize=True)
