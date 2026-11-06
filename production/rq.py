import json,sys,time,urllib.request,urllib.error,base64,os,concurrent.futures as cf
H={"Authorization":"Bearer x","Content-Type":"application/json"}
def req(url,data=None):
    for i in range(12):
        try:
            r=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers=H,method='POST' if data else 'GET')
            return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            if e.code==429:
                try: ra=json.load(e).get('retry_after',5)
                except Exception: ra=5
                time.sleep(float(ra)+1); continue
            raise
    raise RuntimeError('too many 429')
def run(job):
    model,out,inp=job['model'],job['out'],dict(job['input'])
    if os.path.exists(out): return f'SKIP {out}'
    for k,v in list(inp.items()):
        if isinstance(v,str) and v.startswith('file:'):
            fp=v[5:]; ext=fp.rsplit('.',1)[-1].replace('jpg','jpeg')
            inp[k]=f"data:image/{ext};base64,"+base64.b64encode(open(fp,'rb').read()).decode()
    d=req(f"https://api.replicate.com/v1/models/{model}/predictions",{"input":inp})
    while d['status'] not in('succeeded','failed','canceled'):
        time.sleep(4); d=req(d['urls']['get'])
    if d['status']!='succeeded': return f"FAIL {out} {d.get('error')}"
    o=d['output']; o=o[0] if isinstance(o,list) else o
    urllib.request.urlretrieve(o,out); return f"OK {out} {d.get('metrics',{}).get('predict_time')}"
jobs=json.load(open(sys.argv[1])); conc=int(sys.argv[2]) if len(sys.argv)>2 else 2
with cf.ThreadPoolExecutor(conc) as ex:
    futs=[]
    for j in jobs:
        futs.append(ex.submit(run,j)); time.sleep(11)
    for f in cf.as_completed(futs):
        try: print(f.result(),flush=True)
        except Exception as e: print('ERR',e,flush=True)
