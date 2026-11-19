import json,subprocess,sys
d=sys.argv[1];A=json.load(open(d+'/align.json'));s=''.join(A['characters']);st=A['character_start_times_seconds'];en=A['character_end_times_seconds']
L=open(d+'/script.txt').read().strip().split('\n');idx=0
for i,l in enumerate(L):
    p=s.find(l,idx);q=p+len(l)-1;idx=q
    subprocess.run(['ffmpeg','-v','error','-y','-i',d+'/vo_full.mp3','-ss',str(max(0,st[p]-0.05)),'-to',str(en[q]+0.15),f'{d}/l{i:02d}.mp3'],check=True)
