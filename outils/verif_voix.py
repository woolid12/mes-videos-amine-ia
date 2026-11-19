import json,subprocess,difflib,re,unicodedata,time,os,sys
L=open('script.txt').read().strip().split('\n')
NUM={'un':'1','une':'1','deux':'2','trois':'3','quatre':'4','trente':'30','soixante':'60','troisieme':'3e','quarante':'40','huit':'8'}
def norm(t):
    t=unicodedata.normalize('NFKD',t.lower());t=''.join(c for c in t if not unicodedata.combining(c))
    t=re.sub(r'[^a-z0-9 ]',' ',t).split();return [NUM.get(w,w) for w in t]
def tr(f):
    for k in range(6):
        o=subprocess.run(['curl','-sS','https://api.groq.com/openai/v1/audio/transcriptions','-H','Authorization: Bearer dummy','-F',f'file=@{f}','-F','model=whisper-large-v3','-F','language=fr','-F','temperature=0','-F','response_format=text'],capture_output=True,text=True).stdout.strip()
        if 'rate_limit' not in o: time.sleep(3.1);return o
        time.sleep(8)
    return ''
files=sys.argv[1:]  # pattern: label:file:lineidx
out={}
for spec in files:
    lab,f,i=spec.split(':');i=int(i);t=tr(f);r=difflib.SequenceMatcher(None,norm(L[i]),norm(t)).ratio()
    out[spec]=(round(r,2),t);print(f"{i+1:2d} {lab} {r:.2f}  {t}",flush=True)
json.dump(out,open('score_out.json','w'),ensure_ascii=False)
