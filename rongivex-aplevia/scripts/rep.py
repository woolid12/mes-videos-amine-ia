import json,urllib.request,time,subprocess,os,mimetypes,uuid
API="https://api.replicate.com/v1"
H={"Authorization":"Bearer dummy","User-Agent":"video-editor/1.0"}
def req(method,url,data=None,headers=None,timeout=120):
    h=dict(H);h.update(headers or {})
    r=urllib.request.Request(url,data=data,method=method,headers=h)
    for k in range(40):
        try: return json.load(urllib.request.urlopen(r,timeout=timeout))
        except urllib.error.HTTPError as e:
            body=e.read()[:400]
            if e.code in (429,500,502,503,504) : print('http',e.code,url,body[:120],flush=True);time.sleep(12);continue
            raise RuntimeError(f"{e.code} {body}")
        except Exception as e:
            print('retry',url,repr(e),flush=True);time.sleep(8)
    raise RuntimeError("failed "+url)
def upload(path):
    b="----b"+uuid.uuid4().hex;ct=mimetypes.guess_type(path)[0] or "application/octet-stream"
    body=(f"--{b}\r\nContent-Disposition: form-data; name=\"content\"; filename=\"{os.path.basename(path)}\"\r\nContent-Type: {ct}\r\n\r\n").encode()+open(path,'rb').read()+f"\r\n--{b}--\r\n".encode()
    return req("POST",API+"/files",body,{"Content-Type":"multipart/form-data; boundary="+b},timeout=600)["urls"]["get"]
def run(model,inp,version=None,poll=5):
    if version: p=req("POST",API+"/predictions",json.dumps({"version":version,"input":inp}).encode(),{"Content-Type":"application/json"})
    else: p=req("POST",f"{API}/models/{model}/predictions",json.dumps({"input":inp}).encode(),{"Content-Type":"application/json"})
    while p["status"] not in ("succeeded","failed","canceled"):
        time.sleep(poll);p=req("GET",p["urls"]["get"])
    if p["status"]!="succeeded": raise RuntimeError(f"{model}: {p['status']} {p.get('error')} {(p.get('logs') or '')[-800:]}")
    return p["output"]
def download(url,path):
    r=urllib.request.Request(url,headers=H if "replicate.com" in url else {"User-Agent":"video-editor/1.0"})
    open(path,'wb').write(urllib.request.urlopen(r,timeout=600).read())
