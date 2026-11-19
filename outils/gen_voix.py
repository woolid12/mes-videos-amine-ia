import json,urllib.request,base64,sys
text=open('script.txt').read().strip()
body=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.4,"similarity_boost":0.8,"style":0.5,"use_speaker_boost":True,"speed":1.15}}).encode()
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/IHngRooVccHyPqB4uQkG/with-timestamps?output_format=mp3_44100_128",data=body,headers={"Content-Type":"application/json","xi-api-key":"dummy","User-Agent":"video-editor/1.0"})
try: d=json.load(urllib.request.urlopen(req,timeout=300))
except urllib.error.HTTPError as e: print(e.read()[:500]); sys.exit(1)
open('vo_full.mp3','wb').write(base64.b64decode(d['audio_base64']))
json.dump(d['alignment'],open('align.json','w'),ensure_ascii=False)
a=d['alignment'];chars=a['characters'];st=a['character_start_times_seconds'];en=a['character_end_times_seconds']
s="".join(chars);idx=0
for i,line in enumerate(text.split("\n")):
    p=s.find(line,idx);q=p+len(line)-1;idx=q
    print(i+1,round(st[p],2),round(en[q],2),round(en[q]-st[p],2))
print("total",en[-1])
