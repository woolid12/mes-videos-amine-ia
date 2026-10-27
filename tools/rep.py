# usage: rep.py <model-or-version> <json-input> <out-prefix>; values starting with @ are uploaded files
import json, sys, time, subprocess, urllib.request
def sh(args): return subprocess.run(args, capture_output=True, text=True, check=True).stdout
def upload(p):
    return json.loads(sh(["curl","-sS","https://api.replicate.com/v1/files","-F",f"content=@{p}"]))["urls"]["get"]
model, inp, out = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3]
for k,v in list(inp.items()):
    if isinstance(v,str) and v.startswith("@"): inp[k]=upload(v[1:])
    if isinstance(v,list): inp[k]=[upload(x[1:]) if isinstance(x,str) and x.startswith("@") else x for x in v]
if "/" in model: url, body = f"https://api.replicate.com/v1/models/{model}/predictions", {"input":inp}
else: url, body = "https://api.replicate.com/v1/predictions", {"version":model,"input":inp}
while True:
    p = json.loads(sh(["curl","-sS",url,"-H","Content-Type: application/json","-d",json.dumps(body)]))
    if "id" in p: break
    print("retry", p.get("detail","")[:80], flush=True); time.sleep(12)
print("id", p.get("id"), p.get("detail",""), flush=True)
while p.get("status") not in ("succeeded","failed","canceled"):
    time.sleep(4); p = json.loads(sh(["curl","-sS",f"https://api.replicate.com/v1/predictions/{p['id']}"]))
print(p["status"], p.get("error"))
o = p.get("output"); items = o if isinstance(o,list) else (list(o.values()) if isinstance(o,dict) else [o])
names = list(o.keys()) if isinstance(o,dict) else range(len(items))
for n,u in zip(names,items):
    if not u: continue
    ext = u.rsplit(".",1)[-1].split("?")[0][:4]
    sh(["curl","-sS","-L","-o",f"{out}_{n}.{ext}",u]); print("saved", f"{out}_{n}.{ext}")
