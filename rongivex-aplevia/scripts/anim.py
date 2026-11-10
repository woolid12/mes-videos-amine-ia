import numpy as np,subprocess,json,math,random
from PIL import Image,ImageDraw,ImageFont,ImageFilter
S='/tmp/claude-0/-home-user-mes-videos-amine-ia/f8b084f5-d612-5ae8-a97a-c3e86d2bb2c9/scratchpad'
W,H,FPS,DUR=720,1280,30,5.4
F='/usr/share/fonts/opentype/inter/'
GREEN=(155,224,28)
plan=json.load(open(S+'/plan.json'));a0=[s for s in plan['sections'] if s['name']=='anim'][0]['t0']
def wstart(key):
    return [w['o0'] for w in plan['words'] if w['line']==4 and key in w['w']][0]-a0
pops=[wstart('bois')-0.08,wstart('huile')-0.08,wstart('menthe')-0.2,wstart('cannelle')-0.12]
print('pops',[round(p,2) for p in pops]);json.dump(pops,open(S+'/ingr/pops.json','w'))
items=[('cedre','Bois de cèdre'),('ricin','Huile de ricin'),('menthe','Menthe poivrée'),('cannelle','Cannelle')]
R=128;centers=[(190,420),(530,420),(190,745),(530,745)]
# background
yy,xx=np.mgrid[0:H,0:W];d=np.sqrt(((xx-W/2)/W)**2+((yy-H*0.45)/H)**2)
bg=np.clip(1-d*1.6,0,1)[...,None]*np.array([16,30,14])+np.array([5,7,5])
bg=Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
random.seed(3);pts=[(random.uniform(-100,W+100),random.uniform(-100,H+100)) for _ in range(70)]
def mesh(t):
    im=Image.new('RGBA',(W,H),(0,0,0,0));dr=ImageDraw.Draw(im)
    P=[(x+12*math.sin(t*0.6+i),y+10*math.cos(t*0.5+i*1.3)) for i,(x,y) in enumerate(pts)]
    for i,p in enumerate(P):
        ds=sorted(range(len(P)),key=lambda j:(P[j][0]-p[0])**2+(P[j][1]-p[1])**2)[1:4]
        for j in ds: dr.line([p,P[j]],fill=GREEN+(26,),width=1)
    return im
def medallion(k):
    im=Image.open(f'{S}/ingr/{k}.png').convert('RGB');s=2*R;im=im.resize((int(s*1.25),int(s*1.25)),Image.LANCZOS)
    o=(im.width-s)//2;im=im.crop((o,o,o+s,o+s))
    m=Image.new('L',(s,s),0);ImageDraw.Draw(m).ellipse((0,0,s-1,s-1),fill=255)
    out=Image.new('RGBA',(s+80,s+80),(0,0,0,0));glow=Image.new('RGBA',out.size,(0,0,0,0))
    ImageDraw.Draw(glow).ellipse((34,34,s+46,s+46),outline=GREEN+(255,),width=10);glow=glow.filter(ImageFilter.GaussianBlur(14))
    out.alpha_composite(glow);out.paste(im,(40,40),m)
    ImageDraw.Draw(out).ellipse((38,38,s+41,s+41),outline=GREEN+(255,),width=5)
    return out
meds=[medallion(k) for k,_ in items]
fT=ImageFont.truetype(F+'InterDisplay-ExtraBold.otf',62);fS=ImageFont.truetype(F+'InterDisplay-Bold.otf',38);fL=ImageFont.truetype(F+'Inter-Bold.otf',31)
def ease_back(x):
    x=min(max(x,0),1);c=1.9;return 1+(c+1)*(x-1)**3+c*(x-1)**2
def ease_out(x): x=min(max(x,0),1);return 1-(1-x)**3
def text_c(dr,img,cx,y,txt,font,fill,alpha):
    l=Image.new('RGBA',img.size,(0,0,0,0));d=ImageDraw.Draw(l);w=d.textlength(txt,font=font)
    d.text((cx-w/2,y),txt,font=font,fill=fill+(int(255*alpha),));img.alpha_composite(l)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',S+'/ingr/anim.mp4'],stdin=subprocess.PIPE)
for n in range(int(DUR*FPS)):
    t=n/FPS;img=bg.copy();img.alpha_composite(mesh(t))
    # title
    a=ease_out(t/0.35);dy=int((1-a)*-30)
    text_c(None,img,W/2,128+dy,'4 INGRÉDIENTS',fT,(255,255,255),a)
    a2=ease_out((t-0.15)/0.35);text_c(None,img,W/2,205+int((1-a2)*-20),'100% NATURELS',fS,GREEN,a2)
    dr=ImageDraw.Draw(img);lw=int(220*a2);dr.line([(W/2-lw/2,262),(W/2+lw/2,262)],fill=GREEN+(200,),width=3)
    zoom=1+0.03*max(0,t-4.4)
    for i,(c,(k,lab)) in enumerate(zip(centers,items)):
        u=(t-pops[i])/0.45
        if u<=0: continue
        sc=ease_back(u);al=min(1,u*3)
        m=meds[i];sz=max(2,int(m.width*sc*zoom));mm=m.resize((sz,sz),Image.LANCZOS)
        if al<1: mm.putalpha(Image.eval(mm.getchannel('A'),lambda v:int(v*al)))
        # flash ring
        if 0<u<1.4:
            fl=Image.new('RGBA',img.size,(0,0,0,0));rr=R+20+u*60
            ImageDraw.Draw(fl).ellipse((c[0]-rr,c[1]-rr,c[0]+rr,c[1]+rr),outline=GREEN+(int(160*(1-u/1.4)),),width=4)
            img.alpha_composite(fl)
        img.alpha_composite(mm,(int(c[0]-sz/2),int(c[1]-sz/2)))
        la=ease_out((t-pops[i]-0.12)/0.3)
        if la>0: text_c(None,img,c[0],c[1]+R+30+int((1-la)*14),lab,fL,(255,255,255),la)
    p.stdin.write(np.asarray(img.convert('RGB')).tobytes())
p.stdin.close();p.wait()
