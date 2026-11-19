import json,sys,re,numpy as np,cv2,os,subprocess
S=sys.argv[1]
d={int(k):v for k,v in json.load(open(S+'/mask/ocr_3.json')).items()}
N=2759; W,H=720,1280
bad=re.compile(r'^-?[0-9]{1,3}$|^MOUSE$|^REPELLENT$|^POUCHES$|^BUY|ADD TO|CART$|Watch Them|Anywhere|Place These|^bronoir$|EUTEL|Herof|CASTOR')
def iou(a,b):
    x1,y1=max(a[0],b[0]),max(a[1],b[1]);x2,y2=min(a[2],b[2]),min(a[3],b[3])
    i=max(0,x2-x1)*max(0,y2-y1);return i/((a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-i)
tracks=[]
for f in sorted(d):
    for b,t,c in d[f]:
        if bad.search(t): continue
        xs=[p[0] for p in b];ys=[p[1] for p in b];bb=[min(xs),min(ys),max(xs),max(ys)]
        h=bb[3]-bb[1]
        logo=bool(re.search(r'NEST|ESTOFF|STOFF',t,re.I))
        if not logo and ((h<25 and not (14<=h and 520<bb[1]<680)) or (h>75 and not (bb[1]>880 and h<=125))): continue
        if re.search('klicken|entdecken',t): bb=[bb[0]-30,bb[1]-4,bb[2]+60,bb[3]+4]
        if re.search('SHOP',t): bb=[130,bb[1]-22,590,bb[3]+40]
        if re.search('Mausefallen|Schlag',t): bb=[bb[0],bb[1],max(bb[2],660)+20,bb[3]+4]
        if re.search('Rattenl',t): bb=[40,bb[1],690,bb[3]+6]
        if re.search('minze|holz',t): bb=[bb[0]-60,bb[1],bb[2]+10,bb[3]]
        if 'Sterne' in t: bb=[20,bb[1]-8,690,bb[3]+12]
        elif not logo and abs((bb[0]+bb[2])/2-360)>90: continue
        if logo: bb=[bb[0]-22,bb[1]-18,bb[2]+22,bb[3]+18]
        for tr in tracks:
            if f-tr['last']<=6 and iou(tr['bbs'][-1],bb)>0.6:
                tr['bbs'].append(bb);tr['last']=f;tr['texts'].append(t);break
        else: tracks.append({'first':f,'last':f,'bbs':[bb],'texts':[t]})
cuts=sorted(set([0]+[int(x) for x in open(S+'/mask/cuts.txt').read().split()]+[N]))
ev=[]
for tr in tracks:
    A=np.array(tr['bbs']);bb=[A[:,0].min(),A[:,1].min(),A[:,2].max(),A[:,3].max()]
    a=max(0,tr['first']-3);b=min(N-1,tr['last']+3)
    ev.append(dict(a=a,b=b,bb=[int(bb[0])-26,int(bb[1])-16,int(bb[2])+26,int(bb[3])+16],text=tr['texts'][0],n=len(tr['bbs'])))
ev=[e for e in ev if e['n']>=2]
for e in ev: print(e['a'],e['b'],e['bb'],e['text'],e['n'])
for k in range(22,31): ev.append(dict(a=cuts[k],b=cuts[k+1]-1,bb=[25,938,695,1062],text='band',n=99))  # word-by-word captions: mask the whole band
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
