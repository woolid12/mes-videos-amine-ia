import json
S='/tmp/claude-0/-home-user-mes-videos-amine-ia/f8b084f5-d612-5ae8-a97a-c3e86d2bb2c9/scratchpad'
A=json.load(open(S+'/vo/align.json'));chars=A['characters'];st=A['character_start_times_seconds'];en=A['character_end_times_seconds']
text=open(S+'/vo/script.txt').read().strip();lines=text.split('\n');s=''.join(chars)
# line spans in VO
spans=[];idx=0
for l in lines:
    p=s.find(l,idx);q=p+len(l)-1;idx=q;spans.append((p,q))
# words with times
words=[];i=0
while i<len(s):
    if s[i].isspace(): i+=1;continue
    j=i
    while j<len(s) and not s[j].isspace(): j+=1
    li=[k for k,(p,q) in enumerate(spans) if p<=i<=q][0]
    words.append(dict(w=s[i:j],t0=st[i],t1=en[j-1],line=li));i=j
# sections: (name, src, in, out, speed); src 'orig' or 'anim' or 'prod'
secs=[("intro","orig",0.0,4.833,0.90),("produit","orig",4.833,10.267,1.0),("explication","orig",10.267,18.067,1.0),
      ("main_graines","orig",18.067,19.033,0.5),("anim","anim",0,5.1,1.0),("ingredients_odeur","orig",19.033,29.2,1.5),
      ("pose","orig",29.2,34.667,0.72),("securite","orig",34.667,40.6,0.75),("produit_gen","prod",0,3.0,1.0),("fin","orig",41.933,46.267,1.0)]
t=0;sec_out=[]
for n,src,a,b,sp in secs:
    d=round((b-a)/sp*30)/30;sec_out.append(dict(name=n,src=src,a=a,b=b,speed=sp,t0=t,t1=t+d));t+=d
total=t
start={0:0.15,1:sec_out[1]['t0']+0.45,2:sec_out[2]['t0']+0.15,3:sec_out[3]['t0']-0.45,4:sec_out[4]['t0']+0.25,
       5:sec_out[5]["t0"]+0.3,6:sec_out[6]["t0"]-0.1,7:sec_out[7]["t0"]+0.5,8:sec_out[8]["t0"]+0.4}
place=[]
for k,(p,q) in enumerate(spans):
    a=st[p];b=en[q];place.append(dict(line=k,src_a=a,src_b=b,out=start[k],shift=start[k]-a))
for w in words: w['o0']=w['t0']+place[w['line']]['shift'];w['o1']=w['t1']+place[w['line']]['shift']
plan=dict(sections=sec_out,vo=place,words=words,total=total)
json.dump(plan,open(S+'/plan.json','w'),ensure_ascii=False,indent=1)
if __name__=='__main__':
    for x in sec_out: print(f"{x['name']:18s} {x['t0']:6.2f}-{x['t1']:6.2f}")
    for x in place: print(x['line']+1, round(x['out'],2), round(x['out']+x['src_b']-x['src_a'],2))
    print('total',round(total,2))
    for w in words:
        if w['line']==4: print(w['w'],round(w['o0']-sec_out[4]['t0'],2))
