import json,subprocess,os,sys
S='/tmp/claude-0/-home-user-mes-videos-amine-ia/f8b084f5-d612-5ae8-a97a-c3e86d2bb2c9/scratchpad'
def sh(a): print(' '.join(a[:6]),'...',flush=True);subprocess.run(a,check=True)
plan=json.load(open(S+'/plan.json'));ev=json.load(open(S+'/mask/events.json'));cuts=ev['cuts']
caps=json.load(open(S+'/subs/caps.json'))
# 1) clean (subtitle-free) source
segs=[]
for k in range(len(cuts)-1):
    a,b=cuts[k],cuts[k+1];f=f"{S}/inp/shot{k:02d}.mp4"
    o=f"{S}/out/clean_{k:02d}.mp4"
    if os.path.exists(f): src,sel=f,f"trim=end_frame={b-a},setpts=N/30/TB"
    else: src,sel=S+'/src/orig.mp4',f"trim=start_frame={a}:end_frame={b},setpts=N/30/TB"
    if not os.path.exists(S+'/out/clean.mp4'): sh(['ffmpeg','-v','error','-y','-i',src,'-vf',sel+",scale=720:1280,setsar=1,fps=30",'-an','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',o])
    segs.append(o)
open(S+'/out/clean.txt','w').write(''.join(f"file '{p}'\n" for p in segs))
os.path.exists(S+'/out/clean.mp4') or sh(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',S+'/out/clean.txt','-c','copy',S+'/out/clean.mp4'])
# 2) sections
parts=[]
for i,s in enumerate(plan['sections']):
    n=round((s['t1']-s['t0'])*30);o=f"{S}/out/sec_{i:02d}.mp4"
    if s['src']=='orig':
        fa,fb=round(s['a']*30),round(s['b']*30);vf=f"trim=start_frame={fa}:end_frame={fb},setpts=N/30/TB"
        if s['mirror']: vf+=",hflip"
        vf+=f",setpts=PTS/{s['speed']}"
        if s['speed']<1: vf+=",minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
        else: vf+=",fps=30"
        src=S+'/out/clean.mp4'
    elif s['src']=='anim': src=S+'/ingr/anim.mp4';vf="fps=30"
    else: src=S+'/prod/'+s['file'];vf=f"trim={s['a']}:{s['b']},setpts=(PTS-STARTPTS)/{s['speed']},scale=720:-2:flags=lanczos,crop=720:1280,fps=30"
    vf+=f",tpad=stop_mode=clone:stop=30,trim=end_frame={n},setpts=N/30/TB,setsar=1,format=yuv420p"
    sh(["ffmpeg","-v","error","-y","-i",src,"-vf",vf,"-an","-r","30","-fps_mode","cfr","-frames:v",str(n),"-c:v","libx264","-crf","12",o]);parts.append(o)
open(S+'/out/parts.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
sh(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',S+'/out/parts.txt','-c','copy',S+'/out/base.mp4'])
# 3) dark night grade 5% + subtitles
anim=[s for s in plan['sections'] if s['name']=='anim'][0]
inputs=['-i',S+'/out/base.mp4'];fc="[0:v]split[o][g];[g]eq=brightness=-0.16:contrast=1.08:saturation=0.55:gamma=0.85,colorbalance=rs=-0.12:gs=-0.03:bs=0.22:rm=-0.08:bm=0.16:rh=-0.05:bh=0.08[gd];[gd][o]blend=all_mode=normal:all_opacity=0.05,format=yuv420p[v0]"
for i,c in enumerate(caps):
    inputs+=['-i',c['png']];h=60+54*(len(c['lines'])-1)
    mid=(anim['t0']<=c['t0']<anim['t1']-0.05)
    yc=1075 if mid else 885
    fc+=f";[v{i}][{i+1}:v]overlay=x=0:y={int(yc-h/2)}:enable='between(t,{c['t0']},{c['t1']-0.001})'[v{i+1}]"
sh(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map',f'[v{len(caps)}]','-c:v','libx264','-crf','16','-preset','slow','-pix_fmt','yuv420p',S+'/out/video_noaudio.mp4'])
# 4) audio
total=plan['total']
vofiles=sorted({v['file'] for v in plan['vo']});af=[];ai=['-i',S+'/audio/no_vocals.wav']
for f in vofiles: ai+=['-i',S+'/'+f]
# SFX stem re-timed per section
sfx=[]
for i,s in enumerate(plan['sections']):
    d=s['t1']-s['t0']
    if s['src']=='orig':
        af.append(f"[0:a]atrim={s['a']}:{s['b']},asetpts=PTS-STARTPTS,atempo={s['speed']},apad,atrim=0:{d}[s{i}]")
    else:
        af.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{d}[s{i}]")
    sfx.append(f"[s{i}]")
af.append(''.join(sfx)+f"concat=n={len(sfx)}:v=0:a=1,aformat=sample_rates=44100:channel_layouts=stereo[sfx]")
# VO lines
vo=[]
for k,v in enumerate(plan['vo']):
    a=max(0,v['src_a']-0.04);b=v['src_b']+0.12;dl=int((v['out']-(v['src_a']-a))*1000)
    fi=1+vofiles.index(v['file'])
    af.append(f"[{fi}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.05}:d=0.05,adelay={dl}|{dl},aformat=sample_rates=44100:channel_layouts=stereo[l{k}]");vo.append(f"[l{k}]")
af.append(''.join(vo)+f"amix=inputs={len(vo)}:normalize=0,apad,atrim=0:{total}[vo]")
# pops for ingredient animation
pops=json.load(open(S+'/ingr/pops.json'))
for j,p in enumerate(pops):
    dl=int((anim['t0']+p)*1000)
    af.append(f"aevalsrc='0.55*sin(2*PI*(260+520*exp(-t*40))*t)*exp(-t*28)':s=44100:d=0.18,aformat=sample_rates=44100:channel_layouts=stereo,adelay={dl}|{dl}[p{j}]")
af.append("[p0][p1][p2][p3]amix=inputs=4:normalize=0,apad,atrim=0:%s[pops]"%total)
af.append(f"[sfx]volume=1.0[sfxv];[vo][sfxv][pops]amix=inputs=3:normalize=0,atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
sh(['ffmpeg','-v','error','-y',*ai,'-filter_complex',';'.join(af),'-map','[aout]','-ar','44100','-c:a','pcm_s16le',S+'/out/audio.wav'])
sh(['ffmpeg','-v','error','-y','-i',S+'/out/video_noaudio.mp4','-i',S+'/out/audio.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',S+'/out/final.mp4'])
print('done')
