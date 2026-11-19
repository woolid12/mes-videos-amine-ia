import json,subprocess
S='/tmp/claude-0/-home-user-mes-videos-amine-ia/49ff4019-927d-5cde-8e83-117da792ed31/scratchpad';V=S+'/v17';FR='30';F=30.0;R='/home/user/mes-videos-amine-ia/bibliotheque'
N=4373
REP=[(1016,1120,R+'/divers/billets_100_chf.mp4',0),(2038,2084,R+'/divers/billets_100_chf.mp4',3.4),
 (2939,2978,R+'/ingredients/menthe_cannelle_cedre_flacon.mp4',0),(2978,3017,R+'/ingredients/cannelle_assiette.mp4',0),
 (3114,3148,R+'/produit/paquet_ouvert_graines.mp4',0),(3553,3596,R+'/produit/paquet_table_nappe.mp4',0),
 (3641,3667,R+'/produit/paquet_plan_de_travail_cuisine.mp4',0),(3765,3796,R+'/produit/main_paquet_interieur_48.mp4',0),
 (3796,3890,R+'/produit/paquet_arc_cuisine.mp4',0),(3890,3919,R+'/produit/mains_paquet_jardin.mp4',0)]
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
segs=[];p=0
for a,b,src,t0 in REP:
    if a>p: segs.append((p,a,None,0))
    segs.append((a,b,src,t0));p=b
segs.append((p,N,None,0))
L=[]
for k,(a,b,src,t0) in enumerate(segs):
    n=b-a;o=f"{V}/out/seg_{k:02d}.mp4"
    if src:
        use=min(dur(src)-t0,n/F);sp=use/(n/F)
        vf=f"trim={t0}:{t0+use},setpts=(PTS-STARTPTS)/{sp},scale=720:1280:force_original_aspect_ratio=increase:flags=lanczos,crop=720:1280,setsar=1,fps={FR},tpad=stop_mode=clone:stop=30,trim=end_frame={n},setpts=N/({FR})/TB"
        subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vf',vf,'-an','-r',FR,'-frames:v',str(n),'-c:v','libx264','-crf','14','-preset','fast','-pix_fmt','yuv420p',o],check=True)
    else:
        subprocess.run(['ffmpeg','-v','error','-y','-i',V+'/src/orig.mp4','-vf',f"trim=start_frame={a}:end_frame={b},setpts=N/({FR})/TB,setsar=1",'-an','-r',FR,'-frames:v',str(n),'-c:v','libx264','-crf','14','-preset','fast','-pix_fmt','yuv420p',o],check=True)
    L.append(f"file '{o}'\n")
open(V+'/out/list.txt','w').write(''.join(L))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',V+'/out/list.txt','-c','copy',V+'/out/base.mp4'],check=True)
cuts=json.load(open(V+'/mask/cuts.json'));M1=min(c for c in cuts if c>=10*F)
fc=(f"[0:v]split[a][b];[a]trim=end_frame={M1},setpts=PTS-STARTPTS,hflip[m];[b]trim=start_frame={M1},setpts=PTS-STARTPTS[r];[m][r]concat=n=2:v=1:a=0,split[o][g];"
    "[g]eq=brightness=-0.16:contrast=1.08:saturation=0.55:gamma=0.85,colorbalance=rs=-0.12:gs=-0.03:bs=0.22:rm=-0.08:bm=0.16:rh=-0.05:bh=0.08[gd];[gd][o]blend=all_mode=normal:all_opacity=0.05,format=yuv420p[v]")
subprocess.run(['ffmpeg','-v','error','-y','-i',V+'/out/base.mp4','-filter_complex',fc,'-map','[v]','-c:v','libx264','-crf','17','-preset','fast','-movflags','+faststart',V+'/out/video17.mp4'],check=True)
print('mirror until',M1/F)
