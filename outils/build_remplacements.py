import json,subprocess
S='/tmp/claude-0/-home-user-mes-videos-amine-ia/f8b084f5-d612-5ae8-a97a-c3e86d2bb2c9/scratchpad';V=S+'/v12';FR='25';F=25.0;R='/home/user/mes-videos-amine-ia/bibliotheque'
cuts=json.load(open(V+'/mask/cuts.json'))
REP={39:R+'/produit/main_paquet_interieur_39.mp4',40:R+'/produit/paquet_ouvert_graines.mp4',41:R+'/produit/femme_jardin_paquet.mp4',
     48:R+'/ingredients/menthe_cannelle_cedre_flacon.mp4',52:R+'/produit/paquet_table_nappe.mp4',53:R+'/produit/paquet_table_nappe.mp4',
     57:R+'/produit/femme_jardin_paquet.mp4',58:R+'/produit/mains_paquet_jardin.mp4',59:R+'/produit/paquet_ouvert_graines.mp4',
     60:R+'/produit/main_paquet_interieur_53.mp4',61:R+'/produit/paquet_plan_de_travail_cuisine.mp4'}
START={53:(cuts[53]-cuts[52])/F,57:1.5,59:1.5}
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
L=[]
for k in range(len(cuts)-1):
    a,b=cuts[k],cuts[k+1];n=b-a
    if n<=0: continue
    o=f"{V}/out/seg_{k:02d}.mp4"
    if k in REP:
        src=REP[k];t0=START.get(k,0);use=min(dur(src)-t0,n/F);sp=use/(n/F)
        vf=f"trim={t0}:{t0+use},setpts=(PTS-STARTPTS)/{sp},scale=720:1280:force_original_aspect_ratio=increase:flags=lanczos,crop=720:1280,setsar=1,fps={FR},tpad=stop_mode=clone:stop=30,trim=end_frame={n},setpts=N/({FR})/TB"
        subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vf',vf,'-an','-r',FR,'-frames:v',str(n),'-c:v','libx264','-crf','14','-preset','fast','-pix_fmt','yuv420p',o],check=True)
    else:
        subprocess.run(['ffmpeg','-v','error','-y','-i',V+'/src/orig.mp4','-vf',f"trim=start_frame={a}:end_frame={b},setpts=N/({FR})/TB,setsar=1",'-an','-r',FR,'-frames:v',str(n),'-c:v','libx264','-crf','14','-preset','fast','-pix_fmt','yuv420p',o],check=True)
    L.append(f"file '{o}'\n")
open(V+'/out/list.txt','w').write(''.join(L))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',V+'/out/list.txt','-c','copy',V+'/out/base.mp4'],check=True)
M1=min(c for c in cuts if c>=10*F)
fc=(f"[0:v]split[a][b];[a]trim=end_frame={M1},setpts=PTS-STARTPTS,hflip[m];[b]trim=start_frame={M1},setpts=PTS-STARTPTS[r];[m][r]concat=n=2:v=1:a=0,split[o][g];"
    "[g]eq=brightness=-0.16:contrast=1.08:saturation=0.55:gamma=0.85,colorbalance=rs=-0.12:gs=-0.03:bs=0.22:rm=-0.08:bm=0.16:rh=-0.05:bh=0.08[gd];[gd][o]blend=all_mode=normal:all_opacity=0.05,format=yuv420p[v]")
subprocess.run(['ffmpeg','-v','error','-y','-i',V+'/out/base.mp4','-i',V+'/src/orig.mp4','-filter_complex',fc,'-map','[v]','-map','1:a','-c:v','libx264','-crf','17','-preset','fast','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',V+'/out/video12.mp4'],check=True)
print('mirror until',M1/F)
