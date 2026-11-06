import json,sys,subprocess,os,numpy as np,cv2
from concurrent.futures import ThreadPoolExecutor
S=sys.argv[1];sys.path.insert(0,S+'/code');import rep
ev=json.load(open(S+'/mask/events.json'));cuts=ev['cuts'];E=ev['events']
VER="e5ea7ae04e97c96a0e14c70d8e4cb899abdf326a377c01f1c10966ccd6c6bae4"
jobs=[]
for k in range(len(cuts)-1):
    a,b=cuts[k],cuts[k+1]
    if not any(e['a']<b and e['b']>=a for e in E): continue
    if a==1218: continue  # bronoir product shot, replaced by generated clip
    jobs.append((k,a,b))
def work(j):
    k,a,b=j;n=b-a;out=f"{S}/inp/shot{k:02d}.mp4"
    if os.path.exists(out): return k,'cached'
    v=f"{S}/shots/v{k:02d}.mp4";m=f"{S}/shots/m{k:02d}.mp4"
    sel=f"select='between(n\\,{a}\\,{b-1})',setpts=N/30/TB"
    subprocess.run(['ffmpeg','-v','error','-y','-i',S+'/src/orig.mp4','-vf',sel,'-an','-c:v','libx264','-crf','15','-pix_fmt','yuv420p','-r','30',v],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',S+'/mask/mask.mp4','-vf',sel,'-an','-c:v','libx264','-crf','0','-pix_fmt','yuv420p','-r','30',m],check=True)
    import base64;uv='data:video/mp4;base64,'+base64.b64encode(open(v,'rb').read()).decode();um='data:video/mp4;base64,'+base64.b64encode(open(m,'rb').read()).decode()
    o=rep.run(None,{"video":uv,"mask":um,"save_fps":30,"mask_dilation":6,"fp16":False,"subvideo_length":80,"neighbor_length":10,"ref_stride":10},version=VER)
    url=o if isinstance(o,str) else (o[-1] if isinstance(o,list) else list(o.values())[-1])
    rep.download(url,out)
    c=cv2.VideoCapture(out);return k,(n,int(c.get(7)),c.get(3),c.get(4))
only=[int(x) for x in sys.argv[2:]]
if only: jobs=[j for j in jobs if j[0] in only]
with ThreadPoolExecutor(6) as ex:
    def safe(j):
        for t in range(4):
            try: return work(j)
            except Exception as e: print('ERR',j[0],str(e)[:160],flush=True)
        return j[0],'FAILED'
    for r in ex.map(safe,jobs): print(r,flush=True)
