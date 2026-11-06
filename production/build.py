import json, os, subprocess, sys
os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')
W, H, FPS = 1080, 1920, 30
segs = json.load(open('segs.json'))
A = json.load(open('vo/align.json'))
text, al = A['text'], A['al']
cs, ce = al['character_start_times_seconds'], al['character_end_times_seconds']
assert ''.join(al['characters']) == text

# segment start times
pos, starts = 0, []
for s in segs:
    i = text.index(s[0], pos); starts.append(cs[i]); pos = i + len(s[0])
audio_end = ce[-1]
total = audio_end + 1.3
bounds = [0.0] + starts[1:] + [total]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); raise SystemExit(1)

os.makedirs('out/seg', exist_ok=True)
files = []
vis = []  # (name, duration)
for k, s in enumerate(segs):
    names = s[1] if isinstance(s[1], list) else [s[1]]
    D = bounds[k + 1] - bounds[k]
    for nm in names: vis.append((nm, D / len(names)))
for k, (name, d) in enumerate(vis):
    out = f'out/seg/{k:02d}.mp4'; files.append(out)
    v = f'vid/{name}.mp4'
    if os.path.exists(v):
        dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v]).strip())
        f = min(max(d / dur, 1.0), 1.6)  # slow down a little if the clip is short
        vf = (f'setpts={f}*PTS,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},'
              f'tpad=stop_mode=clone:stop_duration={d},trim=duration={d},setsar=1')
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', v, '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', out])
    else:
        n = int(round(d * FPS)) + 1
        zin = k % 2 == 0
        z = f"'1.0+0.10*on/{n}'" if zin else f"'1.10-0.10*on/{n}'"
        vf = (f'scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},'
              f"zoompan=z={z}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
              f'trim=duration={d},setsar=1')
        run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', f'img/{name}.jpg', '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-t', f'{d}', out])
    print('seg', k, name, round(d, 2), flush=True)

# subtitles (ASS)
def t(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h}:{m:02d}:{s:05.2f}'
words, i = [], 0
for w in text.split(' '):
    j = text.index(w, i); words.append((w, cs[j], ce[j + len(w) - 1])); i = j + len(w)
lines, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w[0][-1] in '.,:…?!':
        lines.append(cur); cur = []
if cur: lines.append(cur)
ev = []
for n, L in enumerate(lines):
    st = L[0][1]; en = lines[n + 1][0][1] if n + 1 < len(lines) else audio_end + 0.2
    ev.append(f"Dialogue: 0,{t(st)},{t(en)},Sub,,0,0,0,,{' '.join(w[0] for w in L)}")
for k, s in enumerate(segs):
    if s[2] and s[2] != 'APLEVIA':
        ev.append(f"Dialogue: 1,{t(bounds[k])},{t(bounds[k+1])},Label,,0,0,0,,{s[2]}")
last = bounds[-2]
ev.append(f"Dialogue: 1,{t(last)},{t(total)},Brand,,0,0,0,,APLEVIA")
ev.append(f"Dialogue: 1,{t(last)},{t(total)},Small,,0,0,0,,Sachets anti-rongeurs\\N2+1 OFFERT  •  3+2 OFFERTS")
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,3,0,1,8,2,2,70,70,560,1
Style: Label,Inter Black,84,&H00FFFFFF,&H00FFFFFF,&H00467A2E,&H00000000,0,0,0,0,100,100,1,0,3,22,0,8,80,80,300,1
Style: Brand,Inter Black,150,&H00FFFFFF,&H00FFFFFF,&H00467A2E,&H00000000,0,0,0,0,100,100,6,0,3,30,0,8,80,80,260,1
Style: Small,Inter ExtraBold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,6,0,8,80,80,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + '\n'.join(ev) + '\n'
open('out/subs.ass', 'w', encoding='utf-8').write(ass)

open('out/list.txt', 'w').write(''.join(f"file 'seg/{os.path.basename(f)}'\n" for f in files))
run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'out/list.txt', '-c', 'copy', 'out/silent.mp4'])
run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'out/silent.mp4', '-i', 'vo/vo.mp3',
     '-vf', 'ass=out/subs.ass', '-af', f'apad,atrim=0:{total},loudnorm=I=-14:TP=-1.5',
     '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', str(FPS),
     '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', f'{total}', 'out/aplevia_v1.mp4'])
print('DONE', round(total, 2))
