import json,subprocess,re,os,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
V='/tmp/claude-0/-home-user-mes-videos-amine-ia/49ff4019-927d-5cde-8e83-117da792ed31/scratchpad/v17'
STEP=sys.argv[1]
VD=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',V+'/out/video17.mp4'],capture_output=True,text=True).stdout)
CH={14:'t2',17:'t2',38:'t2'}
L=open(V+'/vo/script.txt').read().strip().split('\n');D=open(V+'/vo/script_disp.txt').read().strip().split('\n')
an=[float(x) for x in open(V+'/vo/anchors.txt').read().split()]
TK={}
for t in ('t1','t2'):
    A=json.load(open(f'{V}/vo/{t}/align.json'));s=''.join(A['characters'])
    TK[t]=dict(s=s,st=A['character_start_times_seconds'],en=A['character_end_times_seconds'],pos=[])
    idx=0
    for l in L: p=s.find(l,idx);q=p+len(l)-1;idx=q;TK[t]['pos'].append((p,q))
place=[];prev=-1
for i in range(len(L)):
    t=CH.get(i,'t1');k=TK[t];p,q=k['pos'][i];out=max(an[i]+0.1,prev+0.2);prev=out+k['en'][q]-k['st'][p];place.append((t,p,q,out))
T=max(VD,prev+0.6);print('vo end',round(prev,2),'video',round(VD,2),'T',round(T,2))
SR=44100
if STEP=='audio':
    mix=np.zeros(int((T+0.5)*SR),np.float32);SRC={}
    for t in TK: SRC[t]=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f'{V}/vo/{t}/vo_full.mp3','-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout,np.float32)
    for (t,p,q,o) in place:
        k=TK[t];a=max(0,k['st'][p]-0.04);b=k['en'][q]+0.12;seg=SRC[t][int(a*SR):int(b*SR)].copy();n=len(seg)
        fi=min(n,int(0.02*SR));fo=min(n,int(0.05*SR));seg[:fi]*=np.linspace(0,1,fi);seg[n-fo:]*=np.linspace(1,0,fo)
        d=int((o-(k['st'][p]-a))*SR);mix[d:d+n]+=seg[:max(0,len(mix)-d)]
    mix=mix[:int(T*SR)]
    pr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_s16le',V+'/vo/vo_raw.wav'],stdin=subprocess.PIPE)
    pr.stdin.write(mix.tobytes());pr.stdin.close();pr.wait();sys.exit()
words=[]
for i,(t,p,q,out) in enumerate(place):
    k=TK[t];s=k['s'];sh=out-k['st'][p];j=p;dw=D[i].split();wi=0
    while j<=q:
        if s[j].isspace(): j+=1;continue
        e=j
        while e<=q and not s[e].isspace(): e+=1
        words.append(dict(w=dw[wi],o0=k['st'][j]+sh,o1=k['en'][e-1]+sh,line=i));wi+=1;j=e
    assert wi==len(dw)
K=1.0;ft=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf',42);tw=lambda t:ft.getlength(t);MAXW=590
caps=[];cur=[]
for k,w in enumerate(words):
    cur.append(w);nx=words[k+1] if k+1<len(words) else None;txt=' '.join(x['w'] for x in cur)
    if nx is None or nx['line']!=w['line'] or re.search(r'[.?!:…]$',w['w']) or (re.search(r',$',w['w']) and len(cur)>=3) or tw(txt+' '+(nx['w'] if nx else ''))>MAXW*1.8 or len(cur)>=7:
        caps.append(cur);cur=[]
m=[]
for c in caps:
    if m and len(c)==1 and c[0]['line']==m[-1][-1]['line'] and tw(' '.join(x['w'] for x in m[-1]+c))<=MAXW*1.9: m[-1]+=c
    else: m.append(c)
caps=m
def split2(ws):
    t=[x['w'] for x in ws];full=' '.join(t)
    if tw(full)<=MAXW*0.8: return [full]
    best=None
    for k in range(1,len(t)):
        a,b=' '.join(t[:k]),' '.join(t[k:]);sc=abs(tw(a)-tw(b))+(10000 if max(tw(a),tw(b))>MAXW else 0)
        if best is None or sc<best[0]: best=(sc,[a,b])
    return best[1] if best else [full]
os.makedirs(V+'/subs',exist_ok=True);out=[]
def render(ls,path):
    BH,PI,PX,R=60,54,19,9
    img=Image.new('RGBA',(720,BH+PI*(len(ls)-1)+6),(0,0,0,0));d=ImageDraw.Draw(img)
    for i,l in enumerate(ls): w=tw(l);d.rounded_rectangle((360-w/2-PX,i*PI,360+w/2+PX,i*PI+BH),radius=R,fill=(255,255,255,255))
    for i,l in enumerate(ls): d.text((360-tw(l)/2,i*PI+BH/2),l,font=ft,fill=(0,0,0,255),anchor='lm')
    img.save(path);return img.height
for k,c in enumerate(caps):
    t0=c[0]['o0']-0.05;nxt=caps[k+1][0]['o0']-0.05 if k+1<len(caps) else None;t1=c[-1]['o1']+0.35
    if nxt is not None and nxt-t1<0.8: t1=nxt
    if nxt is not None: t1=min(t1,nxt)
    ls=split2(c);png=f"{V}/subs/c{k:02d}.png";h=render(ls,png);out.append(dict(t0=t0,t1=t1,lines=ls,png=png,h=h))
json.dump(out,open(V+'/subs/caps.json','w'),ensure_ascii=False,indent=1)
def ts(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(round((x%1)*1000))%1000:03d}"
open(V+'/subs/sous-titres_fr.srt','w').write(''.join(f"{i+1}\n{ts(c['t0'])} --> {ts(c['t1'])}\n"+'\n'.join(c['lines'])+"\n\n" for i,c in enumerate(out)))
inp=['-i',V+'/out/video17.mp4'];fc=f"[0:v]tpad=stop_mode=clone:stop_duration={T-VD+0.1:.2f},trim=0:{T:.3f}[v0]"
for i,c in enumerate(out):
    inp+=['-i',c['png']];fc+=f";[v{i}][{i+1}:v]overlay=x=0:y={int(900-c['h']/2)}:enable='between(t,{c['t0']:.3f},{c['t1']-0.001:.3f})'[v{i+1}]"
subprocess.run(['ffmpeg','-v','error','-y',*inp,'-filter_complex',fc,'-map',f'[v{len(out)}]','-c:v','libx264','-crf','21','-preset','medium','-pix_fmt','yuv420p',V+'/out/video_noaudio.mp4'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',V+'/vo/enh/output-denoised.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','44100','-ac','2','-c:a','pcm_s16le',V+'/out/audio_fr.wav'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',V+'/out/video_noaudio.mp4','-i',V+'/out/audio_fr.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',V+'/out/RongiVex_video17_FR.mp4'],check=True)
for c in out: print(f"{c['t0']:6.2f}  "+' / '.join(c['lines']))
