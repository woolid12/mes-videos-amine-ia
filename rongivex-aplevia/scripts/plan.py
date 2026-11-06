import json
S='/tmp/claude-0/-home-user-mes-videos-amine-ia/f8b084f5-d612-5ae8-a97a-c3e86d2bb2c9/scratchpad'
text=open(S+'/vo/script.txt').read().strip();lines=text.split('\n')
# per-line audio sources: full take, except line 7 (index 6) re-recorded with "plakar" pronunciation
OVR={6:('vo/line7_a.mp3','vo/line7_a.json',{'plakar,':'placards,'})}
def load(al):
    A=json.load(open(S+'/'+al));return ''.join(A['characters']),A['character_start_times_seconds'],A['character_end_times_seconds']
full=load('vo/align.json')
def words_of(s,st,en,p,q,li,fix):
    out=[];i=p
    while i<=q:
        if s[i].isspace(): i+=1;continue
        j=i
        while j<=q and not s[j].isspace(): j+=1
        w=s[i:j];out.append(dict(w=fix.get(w,w),t0=st[i],t1=en[j-1],line=li));i=j
    return out
src=[];words=[];idx=0
for li,l in enumerate(lines):
    s,st,en=full;p=s.find(l,idx);q=p+len(l)-1;idx=q
    if li in OVR:
        f,al,fix=OVR[li];s,st,en=load(al);p=0;q=len(s.rstrip())-1
    else: f,fix='vo/vo_full.mp3',{}
    src.append(dict(file=f,a=st[p],b=en[q]));words+=words_of(s,st,en,p,q,li,fix)
# sections: (name, src, in, out, speed, file)
secs=[("intro","orig",0.0,3.833,0.72,None),("produit_intro","prod",0,3.6,1.0,"kling2.mp4"),("femme","orig",6.167,7.7,1.0,None),
      ("explication","orig",7.7,16.633,1.2,None),("main_graines","orig",16.633,18.067,0.55,None),("anim","anim",0,5.4,1.0,None),
      ("aquarium","orig",21.267,29.2,1.25,None),("pose","orig",29.2,34.667,0.67,None),("securite","orig",34.667,40.6,0.75,None),
      ("produit_gen","prod",0,3.6,1.2,"kling.mp4"),("fin","orig",41.933,46.267,1.0,None)]
MIRROR=("intro","femme")  # first 10 s of the edit, extended to the end of the shot in progress (generated product clip excluded: its label must stay readable)
t=0;sec_out=[];T={}
for n,sr,a,b,sp,f in secs:
    d=round((b-a)/sp*30)/30;sec_out.append(dict(name=n,src=sr,a=a,b=b,speed=sp,file=f,mirror=n in MIRROR,t0=t,t1=t+d));T[n]=t;t+=d
total=t
start={0:0.15,1:T['produit_intro']+0.3,2:T['explication']+0.3,3:T["main_graines"]+0.0,4:T['anim']+0.25,
       5:T['aquarium']+0.15,6:T['pose']+0.0,7:T['securite']+0.5,8:T['produit_gen']+0.4}
place=[]
for k,s_ in enumerate(src):
    place.append(dict(line=k,file=s_['file'],src_a=s_['a'],src_b=s_['b'],out=start[k],shift=start[k]-s_['a']))
for w in words: w['o0']=w['t0']+place[w['line']]['shift'];w['o1']=w['t1']+place[w['line']]['shift']
json.dump(dict(sections=sec_out,vo=place,words=words,total=total),open(S+'/plan.json','w'),ensure_ascii=False,indent=1)
if __name__=='__main__':
    for x in sec_out: print(f"{x['name']:15s} {x['t0']:6.2f}-{x['t1']:6.2f}")
    for x in place: print(x['line']+1, round(x['out'],2), round(x['out']+x['src_b']-x['src_a'],2))
    print('total',round(total,2))
