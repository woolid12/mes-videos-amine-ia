import json,sys,re,numpy as np,cv2,os,subprocess
S=sys.argv[1]
d={int(k):v for k,v in json.load(open(S+'/mask/ocr_3.json')).items()}
N=1388; W,H=720,1280
bad=re.compile(r'^bronoir$|RATTEN|ABWEHRB|MAUSE|^TEL$|Herof|CASTOR')
def iou(a,b):
    x1,y1=max(a[0],b[0]),max(a[1],b[1]);x2,y2=min(a[2],b[2]),min(a[3],b[3])
    i=max(0,x2-x1)*max(0,y2-y1);return i/((a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i)
tracks=[]
for f in sorted(d):
    for b,t,c in d[f]:
        if bad.search(t): continue
        xs=[p[0] for p in b];ys=[p[1] for p in b];bb=[min(xs),min(ys),max(xs),max(ys)]
        h=bb[3]-bb[1]
        if h<25 or h>70: continue
        for tr in tracks:
            if f-tr['last']<=6 and iou(tr['bbs'][-1],bb)>0.6:
                tr['bbs'].append(bb);tr['last']=f;tr['texts'].append(t);break
        else: tracks.append({'first':f,'last':f,'bbs':[bb],'texts':[t]})
cuts=[0,78,115,145,185,231,262,308,375,406,499,542,571,621,638,694,747,794,837,876,909,961,998,1040,1071,1094,1117,1162,1218,1258,1298,1343,1361,N]
ev=[]
for tr in tracks:
    A=np.array(tr['bbs']);bb=[A[:,0].min(),A[:,1].min(),A[:,2].max(),A[:,3].max()]
    a=max(0,tr['first']-3);b=min(N-1,tr['last']+3)
    ev.append(dict(a=a,b=b,bb=[int(bb[0])-26,int(bb[1])-16,int(bb[2])+26,int(bb[3])+16],text=tr['texts'][0],n=len(tr['bbs'])))
ev=[e for e in ev if e['n']>=2]
for e in ev: print(e['a'],e['b'],e['bb'],e['text'],e['n'])
json.dump(dict(events=ev,cuts=cuts),open(S+'/mask/events.json','w'),ensure_ascii=False)
os.makedirs(S+'/mask/png',exist_ok=True)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','gray','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','0','-pix_fmt','yuv420p',S+'/mask/mask.mp4'],stdin=subprocess.PIPE)
for f in range(N):
    m=np.zeros((H,W),np.uint8)
    for e in ev:
        if e['a']<=f<=e['b']:
            x1,y1,x2,y2=e['bb'];m[max(0,y1):y2,max(0,x1):x2]=255
    p.stdin.write(m.tobytes())
p.stdin.close();p.wait()
